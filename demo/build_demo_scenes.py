"""Build original 16:9 graphic scenes for the VCFR video demonstration."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent / "frames"
W, H = 1920, 1080
BG = "#0b1220"
PANEL = "#121d2e"
PANEL2 = "#17263b"
TEXT = "#f8fafc"
MUTED = "#9fb0c7"
BLUE = "#60a5fa"
MINT = "#34d399"
PURPLE = "#c4b5fd"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
REG = ImageFont.truetype(str(FONT_DIR / "DejaVuSans.ttf"), 38)
MED = ImageFont.truetype(str(FONT_DIR / "DejaVuSans-Bold.ttf"), 40)
H1 = ImageFont.truetype(str(FONT_DIR / "DejaVuSans-Bold.ttf"), 86)
H2 = ImageFont.truetype(str(FONT_DIR / "DejaVuSans-Bold.ttf"), 58)
SMALL = ImageFont.truetype(str(FONT_DIR / "DejaVuSans.ttf"), 27)


def base(index, section):
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw.ellipse((1470, -390, 2200, 340), fill="#132744")
    draw.ellipse((-340, 800, 210, 1350), fill="#102a31")
    draw.rounded_rectangle((90, 70, 330, 124), radius=26, fill="#17263b")
    draw.text((116, 78), section.upper(), font=SMALL, fill=BLUE)
    draw.text((1670, 78), f"{index:02d} / 07", font=SMALL, fill=MUTED)
    return image, draw


def text(draw, xy, value, font, fill=TEXT, spacing=12):
    draw.multiline_text(xy, value, font=font, fill=fill, spacing=spacing)


def card(draw, xy, fill=PANEL, outline="#263950", radius=28):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=2)


def save(image, name):
    OUT.mkdir(parents=True, exist_ok=True)
    image.save(OUT / name, quality=95)


def logo(draw, x=145, y=300, scale=1):
    # Open book with a voice waveform at its center.
    lw = int(7 * scale)
    draw.arc((x, y, x + 128 * scale, y + 118 * scale), 188, 352, fill=BLUE, width=lw)
    draw.arc((x + 120 * scale, y, x + 248 * scale, y + 118 * scale), 188, 352, fill=MINT, width=lw)
    draw.line((x + 124 * scale, y + 34 * scale, x + 124 * scale, y + 132 * scale), fill=PURPLE, width=lw)
    heights = [19, 44, 29, 63, 36, 52, 21]
    for i, height in enumerate(heights):
        px = x + (84 + i * 13) * scale
        draw.line((px, y + 70 * scale - height / 2, px, y + 70 * scale + height / 2), fill=BLUE if i < 3 else MINT, width=max(3, int(6 * scale)))


def build():
    frames = []

    image, d = base(1, "Presentación")
    logo(d, 180, 265, 1.25)
    text(d, (590, 270), "VCFR", H1)
    text(d, (598, 385), "VOICE COMMAND FOR READEST", MED, BLUE)
    text(d, (600, 490), "Tu lector. Tus notas.\nTu forma de hablarle.", H2, TEXT, 22)
    card(d, (590, 720, 1740, 824), fill="#142b3e", outline="#1c4f52")
    text(d, (632, 746), "Una app compañera, ligera y de código abierto", SMALL, MINT)
    frames.append(image)

    image, d = base(2, "Lectura fluida")
    text(d, (150, 205), "Guarda sin\ninterrumpir la lectura", H2)
    card(d, (150, 480, 1040, 740), fill=PANEL2)
    text(d, (205, 530), "«Guarda este párrafo»", H2, BLUE)
    text(d, (210, 635), "La narración conserva su estado.", REG, MUTED)
    card(d, (1140, 260, 1710, 740))
    d.ellipse((1345, 360, 1510, 525), outline=MINT, width=14)
    d.arc((1290, 305, 1565, 580), 205, 335, fill=BLUE, width=14)
    d.line((1370, 645, 1480, 645), fill=BLUE, width=12)
    d.line((1418, 520, 1418, 645), fill=BLUE, width=12)
    frames.append(image)

    image, d = base(3, "Conexiones")
    text(d, (150, 195), "Un puente entre\ntu lector y tus notas", H2)
    nodes = [
        ((160, 490, 630, 700), "READEST", "Texto y narración", BLUE),
        ((720, 490, 1200, 700), "VCFR", "Órdenes y capturas", MINT),
        ((1290, 490, 1760, 700), "OBSIDIAN", "Nota Markdown", PURPLE),
    ]
    for box, title, sub, accent in nodes:
        card(d, box, fill=PANEL2)
        text(d, (box[0] + 40, box[1] + 55), title, MED, accent)
        text(d, (box[0] + 40, box[1] + 122), sub, REG, MUTED)
    for x in (645, 1220):
        d.line((x, 595, x + 55, 595), fill=MINT, width=8)
        d.polygon([(x + 55, 580), (x + 78, 595), (x + 55, 610)], fill=MINT)
    d.text((170, 790), "Readest usa el control multimedia del escritorio cuando está disponible.", font=SMALL, fill=MUTED)
    frames.append(image)

    image, d = base(4, "Varios idiomas")
    text(d, (150, 205), "Habla en el idioma\nque prefieras", H2)
    languages = [("ES", "Español", BLUE), ("EN", "English", MINT), ("FR", "Français", PURPLE), ("PT", "Português", "#fbbf24")]
    for i, (code, name, accent) in enumerate(languages):
        x = 150 + (i % 2) * 830
        y = 500 + (i // 2) * 225
        card(d, (x, y, x + 760, y + 170), fill=PANEL2)
        d.ellipse((x + 32, y + 36, x + 135, y + 139), fill=accent)
        text(d, (x + 56, y + 64), code, MED, BG)
        text(d, (x + 175, y + 44), name, H2)
        text(d, (x + 178, y + 112), "Modelo de voz local", SMALL, MUTED)
    frames.append(image)

    image, d = base(5, "IA opcional")
    text(d, (150, 205), "Las órdenes no necesitan\nun modelo generativo", H2)
    card(d, (150, 505, 680, 770), fill="#12312d", outline="#1f6653")
    text(d, (205, 555), "SIN IA", H2, MINT)
    text(d, (205, 635), "Pausar · seguir\ny guardar", SMALL)
    card(d, (760, 505, 1240, 770), fill=PANEL2)
    text(d, (810, 560), "LM STUDIO", MED, BLUE)
    text(d, (810, 635), "Local\nPreguntar / resumir", SMALL, MUTED)
    card(d, (1320, 505, 1770, 770), fill=PANEL2)
    text(d, (1370, 560), "OLLAMA", MED, PURPLE)
    text(d, (1370, 635), "Local\nPreguntar / resumir", SMALL, MUTED)
    text(d, (160, 840), "No hacen falta claves de servicio para usar modelos locales.", SMALL, MUTED)
    frames.append(image)

    image, d = base(6, "A tu manera")
    text(d, (150, 205), "Elige cómo llamarlo", H2)
    text(d, (153, 325), "La frase de activación es configurable.", REG, MUTED)
    card(d, (160, 490, 880, 715), fill=PANEL2)
    text(d, (220, 535), "«Oye, lector…»", H2, BLUE)
    text(d, (220, 625), "«Bibliotecaria, pausa»", REG, MINT)
    card(d, (1030, 455, 1730, 770))
    text(d, (1090, 510), "PAUSA  ·  CONTINÚA\nGUARDA  ·  EXPLICA\nRESUME  ·  MÁS LENTO", MED, TEXT, 28)
    frames.append(image)

    image, d = base(7, "Proyecto abierto")
    logo(d, 165, 300, 1.0)
    text(d, (500, 250), "VCFR", H1)
    text(d, (510, 370), "MIT  ·  OPEN SOURCE", MED, MINT)
    text(d, (510, 480), "Lee. Habla. Guarda.\nY sigue donde ibas.", H2)
    text(d, (170, 850), "Readest · Calibre · LM Studio · Ollama · Obsidian", SMALL, MUTED)
    frames.append(image)

    for i, frame in enumerate(frames, start=1):
        save(frame, f"scene-{i:02d}.png")
    print(f"Created {len(frames)} VCFR scenes in {OUT}")


if __name__ == "__main__":
    build()
