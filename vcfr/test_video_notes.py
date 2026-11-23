import pathlib
import tempfile
import threading
import unittest
from types import SimpleNamespace

from .commands import COMMANDS, parse_command
from .video_notes import (
    TranscriptSegment,
    TranscriptWorkspace,
    TranscriptionResult,
    VideoNotesError,
    append_segment_note,
    format_timestamp,
    safe_source_label,
    transcribe_media,
    validate_source,
    youtube_timestamp_url,
)


class VideoNotesTests(unittest.TestCase):
    def test_timestamps_clamp_and_pad(self):
        self.assertEqual(format_timestamp(3723.9), "01:02:03")
        self.assertEqual(format_timestamp(-4), "00:00:00")

    def test_validate_local_and_reject_missing_or_unsupported(self):
        with tempfile.TemporaryDirectory() as directory:
            media = pathlib.Path(directory) / "talk.MP4"
            media.touch()
            self.assertEqual(validate_source(str(media)), str(media.resolve()))
            with self.assertRaises(VideoNotesError):
                validate_source(str(media.with_name("missing.mp4")))
            unknown = pathlib.Path(directory) / "talk.txt"
            unknown.touch()
            with self.assertRaises(VideoNotesError):
                validate_source(str(unknown))

    def test_url_validation_and_safe_labels(self):
        self.assertEqual(validate_source(" https://youtu.be/abcDEF_1234?t=4 "), "https://youtu.be/abcDEF_1234?t=4")
        with self.assertRaises(VideoNotesError):
            validate_source("file:///etc/passwd")
        with self.assertRaises(VideoNotesError):
            validate_source("https://user:password@example.org/video")
        self.assertEqual(safe_source_label("https://example.org/watch?id=secret"), "example.org/watch")

    def test_youtube_time_links_are_canonical_and_token_free(self):
        link = youtube_timestamp_url("https://www.youtube.com/watch?v=abcDEF_1234&token=secret", 65.8)
        self.assertEqual(link, "https://www.youtube.com/watch?v=abcDEF_1234&t=65s")
        self.assertIsNone(youtube_timestamp_url("https://notyoutube.com/watch?v=abcDEF_1234", 4))

    def test_transcribe_local_with_injected_model(self):
        class Model:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            def transcribe(self, path, **kwargs):
                self.path = path
                return ([SimpleNamespace(start=1.1, end=2.4, text=" Hola ")], SimpleNamespace(language="es"))

        with tempfile.TemporaryDirectory() as directory:
            media = pathlib.Path(directory) / "lecture.wav"
            media.touch()
            result = transcribe_media(str(media), model_factory=Model)
        self.assertEqual(result.title, "lecture")
        self.assertEqual(result.language, "es")
        self.assertEqual(result.segments, (TranscriptSegment(1.1, 2.4, "Hola"),))

    def test_append_note_timestamp_dedup_and_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            base = pathlib.Path(directory)
            note = base / "notes.md"
            note.write_text("Existing notes\n", encoding="utf-8")
            backup = base / "backups"
            result = TranscriptionResult(
                "https://youtu.be/abcDEF_1234?token=private", "Talk <title>", "en",
                (TranscriptSegment(65, 70, "First line\nSecond line"),),
            )
            self.assertTrue(append_segment_note(note, result, result.segments[0], backups_dir=backup))
            content = note.read_text(encoding="utf-8")
            self.assertIn("Existing notes", content)
            self.assertIn("[Abrir en YouTube · 00:01:05](https://www.youtube.com/watch?v=abcDEF_1234&t=65s)", content)
            self.assertIn("> First line\n> Second line", content)
            self.assertNotIn("private", content)
            self.assertNotIn("<title>", content)
            self.assertFalse(append_segment_note(note, result, result.segments[0], backups_dir=backup))
            self.assertEqual(len(list(backup.glob("*.md"))), 1)

    def test_workspace_selection_previous_and_voice_catalog(self):
        done = threading.Event()
        result = TranscriptionResult(
            "/private/path/talk.wav", "talk", "es",
            (TranscriptSegment(0, 1, "Uno"), TranscriptSegment(1, 2, "Dos")),
        )

        def fake_transcriber(*_args):
            done.set()
            return result

        workspace = TranscriptWorkspace(fake_transcriber)
        with tempfile.TemporaryDirectory() as directory:
            media = pathlib.Path(directory) / "talk.wav"
            media.touch()
            workspace.set_source(str(media))
            workspace.start()
            self.assertTrue(done.wait(2))
            # Wait until the worker publishes its result.
            for _ in range(100):
                if workspace.snapshot()[0] is not None:
                    break
                threading.Event().wait(0.01)
            self.assertEqual(workspace.current().text, "Uno")
            workspace.move(1)
            self.assertEqual(workspace.current().text, "Dos")
            self.assertEqual(workspace.previous().text, "Uno")
        self.assertEqual(parse_command("guarda el fragmento anterior", "es"), "save_previous_video_segment")
        for language, commands in COMMANDS.items():
            self.assertIn("open_video_notes", commands)
            self.assertIn("save_video_segment", commands)
            self.assertIn("transcribe_video", commands)


if __name__ == "__main__":
    unittest.main()
