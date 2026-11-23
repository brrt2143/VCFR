"""Tk interface for local video transcription and timestamped notes."""

from __future__ import annotations

import pathlib
import queue
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .video_notes import LANGUAGES, MODEL_SIZES, TranscriptWorkspace, VideoNotesError, format_timestamp


class VideoNotesWindow:
    def __init__(self, app, workspace: TranscriptWorkspace, note_path: pathlib.Path):
        self.app = app
        self.workspace = workspace
        self.note_path = pathlib.Path(note_path)
        self.top = tk.Toplevel(app.root)
        self.top.title("VCFR · Transcripción de video")
        self.top.geometry("900x680")
        self.top.minsize(700, 500)
        self.events = queue.Queue()
        self.source = tk.StringVar()
        self.model = tk.StringVar(value="base")
        self.language = tk.StringVar(value="auto")
        self.status = tk.StringVar(value="El audio se procesa localmente. Elige un archivo o enlace público.")
        self.top.configure(bg="#0b1220")
        frame = ttk.Frame(self.top, padding=18)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Transcribe y guarda por fragmentos", font=("DejaVu Sans", 16, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Archivos locales o enlaces públicos compatibles con yt-dlp. No se omite DRM ni acceso privado.", wraplength=850).pack(anchor="w", pady=(4, 12))

        source_row = ttk.Frame(frame)
        source_row.pack(fill="x", pady=4)
        ttk.Entry(source_row, textvariable=self.source).pack(side="left", fill="x", expand=True)
        ttk.Button(source_row, text="Elegir archivo…", command=self.browse).pack(side="left", padx=(8, 0))
        options = ttk.Frame(frame)
        options.pack(fill="x", pady=6)
        ttk.Label(options, text="Modelo local").pack(side="left")
        ttk.Combobox(options, textvariable=self.model, values=MODEL_SIZES, state="readonly", width=12).pack(side="left", padx=(6, 18))
        ttk.Label(options, text="Idioma").pack(side="left")
        ttk.Combobox(options, textvariable=self.language, values=sorted(LANGUAGES), state="readonly", width=12).pack(side="left", padx=6)
        self.source.trace_add("write", lambda *_: self.workspace.set_source(self.source.get()))
        self.model.trace_add("write", lambda *_: self.configure_workspace())
        self.language.trace_add("write", lambda *_: self.configure_workspace())
        self.start_button = ttk.Button(options, text="Transcribir", command=self.start, style="Accent.TButton")
        self.start_button.pack(side="right")

        self.listing = ttk.Treeview(frame, columns=("time", "text"), show="headings", selectmode="browse")
        self.listing.heading("time", text="Tiempo")
        self.listing.heading("text", text="Transcripción")
        self.listing.column("time", width=95, stretch=False)
        self.listing.column("text", width=680, stretch=True)
        self.listing.pack(fill="both", expand=True, pady=(8, 6))
        self.listing.bind("<<TreeviewSelect>>", self.on_select)
        nav = ttk.Frame(frame)
        nav.pack(fill="x", pady=4)
        ttk.Button(nav, text="← Anterior", command=lambda: self.move(-1)).pack(side="left")
        ttk.Button(nav, text="Siguiente →", command=lambda: self.move(1)).pack(side="left", padx=6)
        ttk.Button(nav, text="Guardar fragmento actual", command=self.save).pack(side="right")
        ttk.Label(frame, textvariable=self.status, wraplength=850).pack(anchor="w", pady=(8, 0))
        ttk.Label(frame, text="Voz: «transcribe video», «siguiente fragmento», «guarda este fragmento», «guarda el fragmento anterior».", wraplength=850).pack(anchor="w", pady=(5, 0))
        self.workspace.subscribe(lambda event, value: self.events.put((event, value)))
        self.top.protocol("WM_DELETE_WINDOW", self.top.withdraw)
        self.top.after(100, self.poll)

    def exists(self):
        try:
            return bool(self.top.winfo_exists())
        except tk.TclError:
            return False

    def show(self):
        self.top.deiconify()
        self.top.lift()
        self.refresh()

    def browse(self):
        path = filedialog.askopenfilename(
            parent=self.top,
            title="Elige un archivo de audio o video",
            filetypes=[("Audio y video", "*.aac *.aiff *.avi *.flac *.m4a *.mka *.mkv *.mov *.mp3 *.mp4 *.oga *.ogg *.opus *.wav *.webm *.wma"), ("Todos los archivos", "*.*")],
        )
        if path:
            self.source.set(path)
            self.workspace.set_source(path)

    def start(self):
        try:
            self.workspace.set_source(self.source.get())
            self.workspace.configure(self.model.get(), self.language.get())
            self.workspace.start()
        except VideoNotesError as error:
            messagebox.showerror("No se pudo iniciar", str(error), parent=self.top)

    def configure_workspace(self):
        try:
            self.workspace.configure(self.model.get(), self.language.get())
        except VideoNotesError:
            pass

    def on_select(self, _event=None):
        selection = self.listing.selection()
        if selection:
            try:
                self.workspace.select(int(selection[0]))
            except (ValueError, VideoNotesError):
                pass

    def move(self, delta):
        try:
            self.workspace.move(delta)
            result, index, _, _ = self.workspace.snapshot()
            if result:
                self.listing.selection_set(str(index))
                self.listing.see(str(index))
        except VideoNotesError as error:
            self.status.set(str(error))

    def select_segment(self, segment):
        result, index, _, _ = self.workspace.snapshot()
        if result:
            self.listing.selection_set(str(index))
            self.listing.see(str(index))
            self.status.set(f"Seleccionado {format_timestamp(segment.start)} · {segment.text}")

    def save(self):
        self.workspace.set_source(self.source.get())
        try:
            added = self.workspace.save_current(self.note_path, self.note_path.parent / "backups")
            self.status.set("Fragmento guardado en " + str(self.note_path) if added else "Ese fragmento ya estaba en la nota.")
        except (VideoNotesError, OSError) as error:
            messagebox.showerror("No se pudo guardar", str(error), parent=self.top)

    def refresh(self):
        result, index, _, busy = self.workspace.snapshot()
        if busy:
            self.start_button.state(["disabled"])
        else:
            self.start_button.state(["!disabled"])
        if result:
            existing = len(self.listing.get_children())
            if existing != len(result.segments):
                self.listing.delete(*self.listing.get_children())
                for number, segment in enumerate(result.segments):
                    self.listing.insert("", "end", iid=str(number), values=(format_timestamp(segment.start), segment.text))
            if result.segments:
                self.listing.selection_set(str(index))
                self.listing.see(str(index))

    def poll(self):
        if not self.exists():
            return
        try:
            while True:
                event, value = self.events.get_nowait()
                if event == "started":
                    self.status.set("Transcribiendo… la primera ejecución puede descargar el modelo local elegido.")
                elif event == "complete":
                    self.status.set(f"Listo · {len(value.segments)} fragmentos · idioma detectado: {value.language or 'no identificado'} · fuente: {value.title}")
                    self.refresh()
                elif event == "error":
                    self.status.set("No se completó la transcripción: " + str(value))
                    self.refresh()
        except queue.Empty:
            pass
        self.top.after(120, self.poll)
