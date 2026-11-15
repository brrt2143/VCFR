"""Localized, closed command catalog for speech and the interface."""

import re
import unicodedata


COMMANDS = {
    "es": {
        "pause": ("pausa", "detente", "para"),
        "play": ("continúa", "reanuda", "sigue leyendo", "reproduce"),
        "save": ("guarda este párrafo", "guarda el párrafo", "subraya este párrafo", "guarda y continúa"),
        "save_previous": ("guarda el párrafo anterior", "subraya el párrafo anterior"),
        "save_pause": ("guarda y pausa",),
        "next": ("siguiente frase", "frase siguiente"),
        "previous": ("frase anterior", "anterior frase"),
        "explain": ("explica este párrafo", "explícalo"),
        "summarize": ("resume este párrafo", "resúmelo"),
        "example": ("dame un ejemplo",),
        "keywords": ("conceptos clave",),
        "quiz": ("hazme una pregunta",),
        "repeat_answer": ("repite la respuesta",),
        "show_paragraph": ("muestra el párrafo",),
        "normal_speed": ("velocidad normal",),
        "slower": ("más lento",),
        "faster": ("más rápido",),
        "open_note": ("abre la nota",),
        "diagnose": ("diagnóstico", "estado del sistema"),
        "help": ("ayuda", "lista de comandos"),
        "stop_voice": ("detén tu voz",),
        "mute_voice": ("responde por escrito",),
        "enable_voice": ("responde con voz",),
        "mic_off": ("apaga el micrófono",),
    },
    "en": {
        "pause": ("pause", "stop reading", "stop"),
        "play": ("continue", "resume", "keep reading", "play"),
        "save": ("save this paragraph", "save paragraph", "highlight this paragraph"),
        "save_previous": ("save previous paragraph", "highlight previous paragraph"),
        "save_pause": ("save and pause",),
        "next": ("next sentence",),
        "previous": ("previous sentence",),
        "explain": ("explain this paragraph", "explain it"),
        "summarize": ("summarize this paragraph", "summarize it"),
        "example": ("give me an example",),
        "keywords": ("key concepts",),
        "quiz": ("ask me a question",),
        "repeat_answer": ("repeat the answer",),
        "show_paragraph": ("show the paragraph",),
        "normal_speed": ("normal speed",),
        "slower": ("slower",),
        "faster": ("faster",),
        "open_note": ("open the note",),
        "diagnose": ("diagnostics", "system status"),
        "help": ("help", "list commands"),
        "stop_voice": ("stop your voice",),
        "mute_voice": ("text replies",),
        "enable_voice": ("voice replies",),
        "mic_off": ("turn off the microphone",),
    },
    "fr": {
        "pause": ("pause", "arrête la lecture", "arrête"),
        "play": ("continue", "reprends", "reprends la lecture", "lis"),
        "save": ("enregistre ce paragraphe", "surligne ce paragraphe"),
        "save_previous": ("enregistre le paragraphe précédent", "surligne le paragraphe précédent"),
        "save_pause": ("enregistre et mets en pause",),
        "next": ("phrase suivante",),
        "previous": ("phrase précédente",),
        "explain": ("explique ce paragraphe", "explique"),
        "summarize": ("résume ce paragraphe", "résume"),
        "example": ("donne un exemple",),
        "keywords": ("concepts clés",),
        "quiz": ("pose-moi une question",),
        "repeat_answer": ("répète la réponse",),
        "show_paragraph": ("montre le paragraphe",),
        "normal_speed": ("vitesse normale",),
        "slower": ("plus lentement",),
        "faster": ("plus vite",),
        "open_note": ("ouvre la note",),
        "diagnose": ("diagnostic", "état du système"),
        "help": ("aide", "liste des commandes"),
        "stop_voice": ("arrête ta voix",),
        "mute_voice": ("réponds par écrit",),
        "enable_voice": ("réponds à voix haute",),
        "mic_off": ("coupe le microphone",),
    },
    "pt": {
        "pause": ("pausa", "pare a leitura", "pare"),
        "play": ("continue", "retome", "continue lendo", "leia"),
        "save": ("salve este parágrafo", "destaque este parágrafo"),
        "save_previous": ("salve o parágrafo anterior", "destaque o parágrafo anterior"),
        "save_pause": ("salve e pause",),
        "next": ("próxima frase",),
        "previous": ("frase anterior",),
        "explain": ("explique este parágrafo", "explique"),
        "summarize": ("resuma este parágrafo", "resuma"),
        "example": ("me dê um exemplo",),
        "keywords": ("conceitos principais",),
        "quiz": ("faça uma pergunta",),
        "repeat_answer": ("repita a resposta",),
        "show_paragraph": ("mostre o parágrafo",),
        "normal_speed": ("velocidade normal",),
        "slower": ("mais devagar",),
        "faster": ("mais rápido",),
        "open_note": ("abra a nota",),
        "diagnose": ("diagnóstico", "estado do sistema"),
        "help": ("ajuda", "listar comandos"),
        "stop_voice": ("pare sua voz",),
        "mute_voice": ("responda por escrito",),
        "enable_voice": ("responda com voz",),
        "mic_off": ("desligue o microfone",),
    },
}


LANGUAGE_NAMES = {"es": "Español", "en": "English", "fr": "Français", "pt": "Português"}


def normalize(text):
    text = "".join(
        c
        for c in unicodedata.normalize("NFD", text.lower())
        if not unicodedata.combining(c)
    )
    return " ".join(re.sub(r"[^\w\s]", " ", text).split())


def _catalog(language="es"):
    return COMMANDS.get(language, COMMANDS["es"])


def parse_command(text, language="es"):
    lookup = {
        normalize(phrase): key
        for key, phrases in _catalog(language).items()
        for phrase in phrases
    }
    return lookup.get(normalize(text), "question")


def voice_phrases(language="es"):
    return [phrase for phrases in _catalog(language).values() for phrase in phrases]
