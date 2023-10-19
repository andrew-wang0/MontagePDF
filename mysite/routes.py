import io
import re
from io import StringIO
from pathlib import Path

from PIL import ImageColor
from PyPDF2 import PdfReader, PdfWriter
from flask import Blueprint, render_template, send_file
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .forms import ToolForm

views = Blueprint('routes', __name__)


def pdf_parse_text(pdf_path):
    def is_date(s):
        return any([s.startswith(day) for day in ["Satu", "Sund", "Mond", "Tues", "Wedn", "Thur", "Frid"]])

    def convert_pdf_to_txt(path):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()

        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                      check_extractable=True):
            interpreter.process_page(page)

        text = retstr.getvalue()

        fp.close()
        device.close()
        retstr.close()
        return text

    def reformat_text(text):
        text = re.sub(r'\x0C+', '', text)

        lines = re.split("\n+", text)

        linesc = []
        for l in lines:
            if len(l.strip()) > 8:
                linesc.append(l)

        fc = []
        wh = []

        date = ""

        for i, l in enumerate(linesc):
            if is_date(l):
                date = ",".join(l.split(",")[0:2])

            if "Location" in l:
                loc = l.split()[1]
                time = " ".join(linesc[i - 1].split()[2:4])

                time = time.replace(":00", "")
                time = time.replace("PM", "p.m.")
                time = time.replace("AM", "a.m.")

                namestrument = re.sub(r"\(.*?\)", "", linesc[i - 2])
                namestrument = namestrument.replace(" -", ",")

                if loc == "CHOMP":
                    fc.append(f"{date}, {time} - {namestrument}")
                elif loc == "WEHO":
                    wh.append(f"{date}, {time} - {namestrument}")
                else:
                    exit(1)

        reformatted = ""
        reformatted += "Fountain Court\n"
        reformatted += "\n".join(fc) + "\n"
        reformatted += "\nWestland House\n"
        reformatted += "\n".join(wh) + "\n"

        return reformatted

    text = convert_pdf_to_txt(pdf_path)
    reformatted = reformat_text(text)

    return reformatted


def add_text_to_template(text, template_path,
                         secondary_color, header_scale, text_scale, header_x, header_y, text_x, text_y, header_text):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    can.setFillColorRGB(0, 0, 0, 1)

    x = text_x  # X-coordinate
    y = text_y  # Starting Y-coordinate

    line_spacing = 11 * text_scale  # Default line spacing

    before_green_spacing = 8 * text_scale  # Spacing before the green text

    textobject = can.beginText(header_x, header_y)

    textobject.setFont("Helvetica-Bold", 18 * header_scale)  # Larger font size
    can.setFillColorRGB(*secondary_color)  # Specific green color

    month = text.splitlines()[1].split(' ')[1]
    if not header_text:
        textobject.textLine(month + " performances " + u"\u2013" + " each lasting 60 minutes")
    else:
        textobject.textLine(header_text)

    can.drawText(textobject)

    for line in text.splitlines(False):
        textobject = can.beginText(x, y)

        if "Fountain Court" in line or "Westland House" in line:
            textobject.setFont("Helvetica-Bold", 14 * text_scale)  # Larger font size
            can.setFillColorRGB(*secondary_color)  # Specific green color

            textobject.textLine(line.rstrip())
            can.drawText(textobject)
            y -= line_spacing

            y -= before_green_spacing

        else:
            textobject.setFont("Helvetica", 9 * text_scale)  # Regular font size
            can.setFillColorRGB(0, 0, 0)  # Black color
            parts = str(line).split("-")
            if len(parts) > 1:
                textobject.setFillColorRGB(0.0, 0.0, 0.0)
                textobject.textOut(parts[0])
                textobject.setFillColorRGB(0.5, 0.5, 0.5)
                textobject.textOut(u"\u2013" + parts[1])

            can.drawText(textobject)
            y -= line_spacing

    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)

    existing_pdf = PdfReader(template_path)

    output = PdfWriter()
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)
    output_stream = open(Path(views.root_path, 'files', 'output.pdf'), "wb")

    output.write(output_stream)
    output_stream.close()


def save_calendar_pdf(pdf):
    save_path = Path(views.root_path, 'files', 'calendar.pdf')
    pdf.save(save_path)
    return save_path


def save_custom_template_pdf(pdf):
    save_path = Path(views.root_path, 'files', 'base', 'custom_base.pdf')
    pdf.save(save_path)
    return save_path


@views.route('/', methods=['GET', 'POST'])
def pdf_tool():
    form = ToolForm()

    if form.validate_on_submit():
        save_path = save_calendar_pdf(form.calendar_pdf.data)
        pdf_text = pdf_parse_text(save_path)

        if not form.template_pdf.data:
            template_path = Path(views.root_path, 'files', 'base', 'base.pdf')
        else:
            template_path = save_custom_template_pdf(form.template_pdf.data)

        secondary_color_rgb = ImageColor.getrgb(form.secondary_color.data)
        secondary_color_floats = [val / 255 for val in secondary_color_rgb]
        text_scale = float(form.text_scale.data)

        header_text = form.header_text.data
        header_x = form.header_x.data
        header_y = form.header_y.data
        text_x = form.text_x.data
        text_y = form.text_y.data
        header_scale = float(form.header_scale.data)

        add_text_to_template(pdf_text,
                             template_path=template_path,
                             secondary_color=secondary_color_floats,
                             header_scale=header_scale,
                             text_scale=text_scale,
                             header_x=header_x,
                             header_y=header_y,
                             text_x=text_x,
                             text_y=text_y,
                             header_text=header_text)

        return send_file(Path(views.root_path, 'files', 'output.pdf'))

    return render_template('pdf_tool.html', form=form)