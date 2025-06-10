from pathlib import Path
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Указываем путь до папки src
BASE_DIR = Path(__file__).parent.parent.parent
FONT_DIR = BASE_DIR / "assets" / "ttf"

# Регистрируем Regular и Bold
pdfmetrics.registerFont(TTFont("DejaVuSans",       str(FONT_DIR / "DejaVuLGCSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(FONT_DIR / "DejaVuLGCSans-Bold.ttf")))

def create_personality_pdf(profile: dict) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    # Перепривязываем Heading1 на DejaVuSans-Bold
    styles["Heading1"].fontName = "DejaVuSans-Bold"
    styles["Heading1"].fontSize = 18
    styles["Heading1"].leading  = 22

    # Переопределяем BodyText
    styles.add(ParagraphStyle(
        name="Body", parent=styles["BodyText"],
        fontName="DejaVuSans", fontSize=12, leading=14
    ))

    story = []
    # Заголовок
    story.append(Paragraph(
        f"Ваш тип личности: <b>{profile['type_code']} — {profile['type_name']}</b>",
        styles["Heading1"]
    ))
    story.append(Spacer(1, 0.5*cm))

    # Описание
    blocks = [
        profile["description"],
        f"<b>Сильные стороны:</b> {profile['strengths']}",
        f"<b>Слабые стороны:</b> {profile['weaknesses']}",
        f"<b>Профессиональные качества:</b> {profile['professional_qualities']}",
        f"<b>Уровень соответствия:</b> {profile['percentage']}%"
    ]
    for blk in blocks:
        text = blk.replace("\n", "<br/>")
        story.append(Paragraph(text, styles["Body"]))
        story.append(Spacer(1, 0.3*cm))

    doc.build(story)
    buffer.seek(0)
    return buffer
