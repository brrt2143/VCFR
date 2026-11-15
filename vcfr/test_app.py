import pathlib
import queue
import tempfile
import threading
import unittest
from unittest.mock import patch

from vcfr import app as vcfr_module


class Tests(unittest.TestCase):
    def test_note_append_and_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            base = pathlib.Path(d)
            note = base / "note.md"
            note.write_text("Texto original\n")
            with patch.object(vcfr_module, "BASE", base), patch.object(vcfr_module, "NOTE", note):
                vcfr_module.save_note(vcfr_module.PARAS[1])
                first = note.read_text()
                vcfr_module.save_note(vcfr_module.PARAS[1])
                self.assertEqual(first, note.read_text())
                self.assertTrue(first.startswith("Texto original\n"))
                self.assertEqual(len(list((base / "backups").glob("*.md"))), 1)

    def test_reject_unknown_text(self):
        with self.assertRaises(ValueError):
            vcfr_module.save_note("texto inventado")

    def test_match_and_short_fragment(self):
        self.assertEqual(vcfr_module.paragraph(vcfr_module.PARAS[1][:100]), 1)
        self.assertIsNone(vcfr_module.paragraph("mente"))

    def test_pause_idempotent(self):
        with (
            patch.object(vcfr_module, "prop", return_value="Paused"),
            patch.object(vcfr_module, "wait_state", return_value=True),
            patch.object(vcfr_module, "run") as run,
        ):
            vcfr_module.action("Pause")
            run.assert_not_called()

    def test_failed_pause_is_error(self):
        with (
            patch.object(vcfr_module, "prop", return_value="Playing"),
            patch.object(vcfr_module, "wait_state", return_value=False),
            patch.object(vcfr_module, "run", return_value="123"),
        ):
            with self.assertRaises(RuntimeError):
                vcfr_module.action("Pause")

    def test_keyboard_fallback(self):
        with (
            patch.object(vcfr_module, "prop", return_value="Playing"),
            patch.object(vcfr_module, "wait_state", side_effect=[False, True]),
            patch.object(vcfr_module, "run", return_value="123") as run,
        ):
            vcfr_module.action("Pause")
            self.assertIn(
                unittest.mock.call(["xdotool", "key", "--clearmodifiers", "space"]),
                run.call_args_list,
            )

    def test_voice_needs_prefix(self):
        a = vcfr_module.App.__new__(vcfr_module.App)
        a.wake_phrase = "VCFR"
        a.language = "es"
        a.snapshot_lock = threading.RLock()
        a.cancel_resume = threading.Event()
        a.voice = None
        a.tasks = queue.Queue()
        a.q = queue.Queue()
        a.current = 1
        a.previous = 0
        a.sentence = "test"
        a.submit("pausa", voice=True)
        self.assertTrue(a.tasks.empty())
        a.submit("vcfr pausa", voice=True)
        self.assertEqual(a.tasks.get()[0], "pausa")
        a.submit("vcfr [unk] pausa", voice=True)
        self.assertTrue(a.tasks.empty())


class ReadingFlowTests(unittest.TestCase):
    def app(self):
        import threading

        a = vcfr_module.App.__new__(vcfr_module.App)
        a.q = queue.Queue()
        a.voz = True
        a.model = "test"
        a.auto_resume = True
        a.stop = threading.Event()
        a.cancel_resume = threading.Event()
        a.last_answer = ""
        a.voice = None
        return a

    def test_save_does_not_pause_or_speak(self):
        a = self.app()
        with (
            patch.object(vcfr_module, "save_note", return_value="Guardado") as save,
            patch.object(vcfr_module, "action") as act,
            patch.object(a, "speak") as speak,
        ):
            a.execute("guarda este párrafo", 1, 0, "")
            save.assert_called_once_with(vcfr_module.PARAS[1], chapter=vcfr_module.CHAPTERS[1])
            act.assert_not_called()
            speak.assert_not_called()

    def test_previous_snapshot(self):
        a = self.app()
        with (
            patch.object(vcfr_module, "save_note", return_value="Guardado") as save,
            patch.object(vcfr_module, "action") as act,
        ):
            a.execute("guarda el párrafo anterior", 1, 0, "")
            save.assert_called_once_with(vcfr_module.PARAS[0], chapter=vcfr_module.CHAPTERS[0])
            act.assert_not_called()

    def test_unknown_paragraph_does_not_interrupt(self):
        a = self.app()
        with (
            patch.object(vcfr_module, "save_note") as save,
            patch.object(vcfr_module, "action") as act,
        ):
            with self.assertRaises(ValueError):
                a.execute("guarda este párrafo", None, None, "")
            save.assert_not_called()
            act.assert_not_called()

    def test_failed_save_keeps_player(self):
        a = self.app()
        with (
            patch.object(vcfr_module, "save_note", side_effect=OSError("read only")),
            patch.object(vcfr_module, "action") as act,
        ):
            with self.assertRaises(OSError):
                a.execute("guarda este párrafo", 1, 0, "")
            act.assert_not_called()

    def test_save_and_pause_is_explicit(self):
        a = self.app()
        with (
            patch.object(vcfr_module, "save_note", return_value="Guardado"),
            patch.object(vcfr_module, "action") as act,
        ):
            a.execute("guarda y pausa", 1, 0, "")
            act.assert_called_once_with("Pause")

    def test_reply_resumes_only_if_previously_playing(self):
        for status, expected in [("Playing", ["Pause", "Play"]), ("Paused", ["Pause"])]:
            a = self.app()
            a.last_answer = "Respuesta previa"
            with (
                patch.object(vcfr_module, "prop", return_value=status),
                patch.object(vcfr_module, "action") as act,
                patch.object(a, "speak"),
            ):
                a.execute("repite la respuesta", 1, 0, "")
                self.assertEqual([c.args[0] for c in act.call_args_list], expected)

    def test_interruption_cancels_resume(self):
        a = self.app()
        a.last_answer = "Respuesta previa"
        with (
            patch.object(vcfr_module, "prop", return_value="Playing"),
            patch.object(vcfr_module, "action") as act,
            patch.object(a, "speak", side_effect=lambda _: a.cancel_resume.set()),
        ):
            a.execute("repite la respuesta", 1, 0, "")
            self.assertEqual([c.args[0] for c in act.call_args_list], ["Pause"])

    def test_catalog_is_complete(self):
        from vcfr.commands import COMMANDS, parse_command, voice_phrases

        for language, commands in COMMANDS.items():
            for key, phrases in commands.items():
                for phrase in phrases:
                    self.assertEqual(parse_command(phrase, language), key)
                    self.assertIn(phrase, voice_phrases(language))


if __name__ == "__main__":
    unittest.main()
