import io
import pathlib

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.util.pdf_formatter import PDFFormatter


class PDFWriterOptions:
    def __init__(self, template_path, secondary_color, header_scale, text_scale, header_x, header_y, text_x, text_y,
                 header_text):
        self.template_path = template_path
        self.secondary_color = secondary_color
        self.header_scale = header_scale
        self.text_scale = text_scale
        self.header_x = header_x
        self.header_y = header_y
        self.text_x = text_x
        self.text_y = text_y
        self.header_text = header_text


class PDFWriter:
    def __init__(self, pdf_formatter: PDFFormatter, options: PDFWriterOptions):
        self.options = options
        self.pdf_formatter = pdf_formatter

    def write_pdf(self, write_path: pathlib.Path):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        can.setFillColorRGB(0, 0, 0, 1)

        x = self.options.text_x
        y = self.options.text_y

        line_spacing = 11 * self.options.text_scale

        before_green_spacing = 8 * self.options.text_scale

        text_object = can.beginText(self.options.header_x, self.options.header_y)

        text_object.setFont("Helvetica-Bold", 18 * self.options.header_scale)
        can.setFillColorRGB(*self.options.secondary_color)

        if not self.options.header_text:
            text_object.textLine(self.pdf_formatter.month + " performances " + u"\u2013" + " each lasting 60 minutes")
        else:
            text_object.textLine(self.options.header_text)

        can.drawText(text_object)

        text_object = can.beginText(x, y)
        text_object.setFont("Helvetica-Bold", 14 * self.options.text_scale)
        can.setFillColorRGB(*self.options.secondary_color)
        text_object.textLine("Fountain Court")
        can.drawText(text_object)
        y -= line_spacing
        y -= before_green_spacing

        for performance in self.pdf_formatter.fountain_court_performances():
            text_object = can.beginText(x, y)

            text_object.setFont("Helvetica", 9 * self.options.text_scale)
            can.setFillColorRGB(0, 0, 0)

            text_object.textOut(performance.output_heavy())
            text_object.setFillColorRGB(0.4, 0.4, 0.4)
            text_object.textOut(performance.output_light())

            can.drawText(text_object)
            y -= line_spacing

        y -= line_spacing
        text_object = can.beginText(x, y)
        text_object.setFont("Helvetica-Bold", 14 * self.options.text_scale)
        can.setFillColorRGB(*self.options.secondary_color)
        text_object.textLine("Westland House")
        can.drawText(text_object)
        y -= line_spacing
        y -= before_green_spacing

        for performance in self.pdf_formatter.westland_house_performances():
            text_object = can.beginText(x, y)

            text_object.setFont("Helvetica", 9 * self.options.text_scale)
            can.setFillColorRGB(0, 0, 0)

            text_object.textOut(performance.output_heavy())
            text_object.setFillColorRGB(0.4, 0.4, 0.4)
            text_object.textOut(performance.output_light())

            can.drawText(text_object)
            y -= line_spacing

        can.save()

        packet.seek(0)
        new_pdf = PdfReader(packet)

        existing_pdf = PdfReader(self.options.template_path)

        output = PdfWriter()
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        output_stream = open(write_path, "wb")

        output.write(output_stream)
        output_stream.close()
