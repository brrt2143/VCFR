"""Local transcription and timestamped note helpers for video/audio sources."""

from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import html
import pathlib
import re
import tempfile
import threading
from dataclasses import dataclass
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


MEDIA_EXTENSIONS = {
    ".aac", ".aiff", ".avi", ".flac", ".m4a", ".mka", ".mkv", ".mov",
    ".mp3", ".mp4", ".oga", ".ogg", ".opus", ".wav", ".webm", ".wma",
}
MODEL_SIZES = ("tiny", "base", "small", "medium", "large-v3")
LANGUAGES = {"auto", "es", "en", "fr", "pt"}


class VideoNotesError(RuntimeError):
    """An actionable error suitable for displaying in VCFR."""


@dataclass(frozen=True)
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class TranscriptionResult:
    source: str
    title: str
    language: str
    segments: tuple[TranscriptSegment, ...]


def format_timestamp(seconds: float) -> str:
    """Format non-negative seconds as a stable HH:MM:SS timestamp."""
    total = max(0, int(float(seconds)))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def validate_source(source: str) -> str:
    """Accept an existing media file or a public HTTP(S) video URL."""
    source = str(source).strip()
    if not source:
        raise VideoNotesError("Elige un archivo o pega el enlace de un video.")
    parsed = urlparse(source)
    if parsed.scheme:
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise VideoNotesError("El enlace debe usar HTTP o HTTPS.")
        if parsed.username or parsed.password:
            raise VideoNotesError("Quita usuario y contraseña del enlace antes de importarlo.")
        return source
    path = pathlib.Path(source).expanduser().resolve()
    if not path.is_file():
        raise VideoNotesError("No encuentro ese archivo de video o audio.")
    if path.suffix.lower() not in MEDIA_EXTENSIONS:
        raise VideoNotesError("Ese formato no está en la lista de formatos admitidos.")
    return str(path)


def safe_source_label(source: str) -> str:
    """Return a share-safe source label without credentials or query tokens."""
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"} and parsed.hostname:
        return (parsed.hostname + parsed.path)[:240]
    return pathlib.Path(source).name


def youtube_timestamp_url(source: str, seconds: float) -> str | None:
    """Build a clean timestamp link only for recognizable YouTube video URLs."""
    parsed = urlparse(source)
    host = (parsed.hostname or "").lower()
    query = parse_qs(parsed.query)
    video_id = query.get("v", [None])[0]
    if host in {"youtu.be", "www.youtu.be"}:
        video_id = parsed.path.strip("/").split("/")[0]
    elif host == "youtube.com" or host.endswith(".youtube.com"):
        parts = [part for part in parsed.path.split("/") if part]
        if not video_id and len(parts) >= 2 and parts[0] in {"embed", "shorts", "live"}:
            video_id = parts[1]
    else:
        return None
    if not video_id or not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", video_id):
        return None
    base = urlunparse(("https", "www.youtube.com", "/watch", "", urlencode({"v": video_id}), ""))
    return base + "&t=" + str(max(0, int(float(seconds)))) + "s"


def _download_url(source: str, directory: pathlib.Path) -> tuple[pathlib.Path, str]:
    try:
        import yt_dlp
    except ImportError as error:
        raise VideoNotesError(
            "Para importar enlaces instala la opción en línea: pip install '.[video-online]'"
        ) from error

    options = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": str(directory / "source.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "overwrites": False,
        "restrictfilenames": True,
    }
    try:
        with yt_dlp.YoutubeDL(options) as downloader:
            info = downloader.extract_info(source, download=True)
            candidates = [
                pathlib.Path(item["filepath"])
                for item in info.get("requested_downloads", [])
                if item.get("filepath")
            ]
            candidates.append(pathlib.Path(downloader.prepare_filename(info)))
            media_path = next((p for p in candidates if p.is_file()), None)
            if media_path is None:
                media_path = next((p for p in directory.iterdir() if p.is_file()), None)
            if media_path is None:
                raise VideoNotesError("El sitio no entregó un archivo de audio/video compatible.")
            return media_path, str(info.get("title") or safe_source_label(source))
    except VideoNotesError:
        raise
    except Exception as error:
        raise VideoNotesError(
            "No pude obtener este enlace. Usa una fuente pública y permitida, o importa un archivo local. "
            + str(error)
        ) from error


def transcribe_media(
    source: str,
    model_size: str = "base",
    language: str = "auto",
    *,
    model_factory=None,
) -> TranscriptionResult:
    """Transcribe a local media file or an accessible URL using CPU int8 Whisper."""
    source = validate_source(source)
    if model_size not in MODEL_SIZES:
        raise VideoNotesError("Elige un tamaño de modelo disponible.")
    if language not in LANGUAGES:
        raise VideoNotesError("Elige un idioma admitido o detección automática.")

    if model_factory is None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as error:
            raise VideoNotesError(
                "Falta el motor local. Instálalo con: pip install '.[video]'"
            ) from error
        model_factory = WhisperModel

    def run_transcription(media_path: pathlib.Path, title: str) -> TranscriptionResult:
        try:
            model = model_factory(model_size, device="cpu", compute_type="int8")
            segments, metadata = model.transcribe(
                str(media_path),
                language=None if language == "auto" else language,
                beam_size=5,
                vad_filter=True,
            )
            normalized = tuple(
                TranscriptSegment(float(segment.start), float(segment.end), segment.text.strip())
                for segment in segments
                if segment.text and segment.text.strip()
            )
        except VideoNotesError:
            raise
        except Exception as error:
            raise VideoNotesError("Falló la transcripción local: " + str(error)) from error
        if not normalized:
            raise VideoNotesError("No encontré voz en ese archivo.")
        detected = getattr(metadata, "language", None) or (language if language != "auto" else "")
        return TranscriptionResult(source, title, detected, normalized)

    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        with tempfile.TemporaryDirectory(prefix="vcfr-video-") as temporary:
            path, title = _download_url(source, pathlib.Path(temporary))
            return run_transcription(path, title)
    path = pathlib.Path(source)
    return run_transcription(path, path.stem)


def append_segment_note(
    note_path: pathlib.Path,
    result: TranscriptionResult,
    segment: TranscriptSegment,
    *,
    backups_dir: pathlib.Path | None = None,
) -> bool:
    """Append one de-duplicated transcript excerpt, timestamp, and source reference."""
    note_path = pathlib.Path(note_path).expanduser().resolve()
    note_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = format_timestamp(segment.start)
    identity = "\0".join((result.source, str(segment.start), segment.text))
    marker = "<!-- vcfr-video:" + hashlib.sha256(identity.encode()).hexdigest()[:16] + " -->"
    with note_path.open("a+", encoding="utf-8") as target:
        fcntl.flock(target, fcntl.LOCK_EX)
        target.seek(0)
        original = target.read()
        if marker in original:
            return False
        if backups_dir is not None and note_path.exists() and original:
            backups_dir.mkdir(parents=True, exist_ok=True)
            when = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            safe_copy = backups_dir / f"{when}-{note_path.name}"
            safe_copy.write_text(original, encoding="utf-8")
        title = html.escape(result.title.replace("\n", " ").strip() or "Video", quote=False)
        source_label = safe_source_label(result.source)
        player_url = youtube_timestamp_url(result.source, segment.start)
        source_line = f"[Abrir en YouTube · {stamp}]({player_url})" if player_url else f"Fuente: {source_label}"
        excerpt = "\n".join("> " + line for line in segment.text.splitlines())
        block = (
            f"\n{marker}\n### {title} · {stamp}\n\n"
            f"{source_line}  \n"
            f"_Transcripción local · {result.language or 'idioma no detectado'} · "
            f"{format_timestamp(segment.end)}_\n\n"
            f"{excerpt}\n\n"
        )
        target.seek(0, 2)
        target.write(block)
        target.flush()
    return True


class TranscriptWorkspace:
    """Thread-safe selected-segment state shared by the window and voice commands."""

    def __init__(self, transcriber=transcribe_media):
        self._transcriber = transcriber
        self._lock = threading.RLock()
        self._source = ""
        self._model_size = "base"
        self._language = "auto"
        self._result: TranscriptionResult | None = None
        self._index = 0
        self._previous_index: int | None = None
        self._busy = False
        self._listeners = []

    def subscribe(self, listener):
        with self._lock:
            self._listeners.append(listener)

    def set_source(self, source: str):
        with self._lock:
            self._source = source.strip()

    def configure(self, model_size: str, language: str):
        if model_size not in MODEL_SIZES or language not in LANGUAGES:
            raise VideoNotesError("La configuración de transcripción no es válida.")
        with self._lock:
            self._model_size = model_size
            self._language = language

    def _emit(self, event, value=None):
        with self._lock:
            listeners = tuple(self._listeners)
        for listener in listeners:
            listener(event, value)

    def start(self):
        with self._lock:
            if self._busy:
                raise VideoNotesError("La transcripción ya está en curso.")
            source, model_size, language = self._source, self._model_size, self._language
            validate_source(source)
            self._busy = True
            self._result = None
            self._index = 0
            self._previous_index = None
        thread = threading.Thread(
            target=self._run, args=(source, model_size, language), daemon=True,
            name="vcfr-video-transcription",
        )
        self._emit("started", None)
        thread.start()
        return thread

    def _run(self, source, model_size, language):
        try:
            result = self._transcriber(source, model_size, language)
            with self._lock:
                self._result = result
                self._index = 0
                self._busy = False
            self._emit("complete", result)
        except Exception as error:
            with self._lock:
                self._busy = False
            self._emit("error", str(error))

    @property
    def busy(self):
        with self._lock:
            return self._busy

    def snapshot(self):
        with self._lock:
            return self._result, self._index, self._previous_index, self._busy

    def select(self, index: int):
        with self._lock:
            if self._result is None or not 0 <= index < len(self._result.segments):
                raise VideoNotesError("Elige primero un fragmento transcrito.")
            if index != self._index:
                self._previous_index = self._index
            self._index = index
            return self._result.segments[index]

    def move(self, delta: int):
        with self._lock:
            if self._result is None:
                raise VideoNotesError("Primero transcribe un video.")
            target = min(max(0, self._index + delta), len(self._result.segments) - 1)
        return self.select(target)

    def current(self):
        with self._lock:
            if self._result is None or not self._result.segments:
                return None
            return self._result.segments[self._index]

    def previous(self):
        with self._lock:
            if self._result is None or self._previous_index is None:
                return None
            return self._result.segments[self._previous_index]

    def save_current(self, note_path: pathlib.Path, backups_dir: pathlib.Path | None = None):
        with self._lock:
            if self._result is None:
                raise VideoNotesError("Primero transcribe un video.")
            result = self._result
            segment = result.segments[self._index]
        return append_segment_note(note_path, result, segment, backups_dir=backups_dir)

    def save_previous(self, note_path: pathlib.Path, backups_dir: pathlib.Path | None = None):
        with self._lock:
            if self._result is None or self._previous_index is None:
                raise VideoNotesError("No hay un fragmento anterior seleccionado.")
            result = self._result
            segment = result.segments[self._previous_index]
        return append_segment_note(note_path, result, segment, backups_dir=backups_dir)
