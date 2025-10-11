from docx import Document
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
from xhtml2pdf import pisa

def convert_docx_to_pdf(docx_path):
    doc = Document(docx_path)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    text = c.beginText(50, 800)

    for para in doc.paragraphs:
        text.textLine(para.text)

    c.drawText(text)
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

def convert_txt_to_pdf(txt_path):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    text = c.beginText(50, 800)

    with open(txt_path, 'r', encoding='utf-8') as file:
        for line in file:
            text.textLine(line.strip())

    c.drawText(text)
    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

def convert_image_to_pdf(image_path):
    image = Image.open(image_path)
    buffer = BytesIO()
    image.convert('RGB').save(buffer, format='PDF')
    buffer.seek(0)
    return buffer

def convert_html_to_pdf(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        html = file.read()

    result = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=result)

    result.seek(0)
    return result if not pisa_status.err else None