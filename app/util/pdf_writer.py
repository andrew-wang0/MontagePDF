import io
from dataclasses import dataclass
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from app.util.pdf_formatter import PDFFormatter


@dataclass
class PDFWriterOptions:
    title_text: str
    title_scale: float
    title_x: int
    title_y: int
    template_path: Path
    secondary_color: list[float]
    text_x: int
    text_y: int
    text_scale: float
    text_auto_scale: bool


class PDFWriter:
    def __init__(self, pdf_formatter: PDFFormatter, options: PDFWriterOptions):
        self.options = options

        self.curr_x = self.options.text_x
        self.curr_y = self.options.text_y
        self.pdf_formatter = pdf_formatter

        if self.options.text_auto_scale:
            self._set_auto_scale()

        self.line_spacing = 11 * self.options.text_scale
        self.before_header_spacing = 8 * self.options.text_scale

        self.packet = io.BytesIO()
        self.canvas = canvas.Canvas(self.packet, pagesize=LETTER)

    def _set_auto_scale(self):
        self.options.text_auto_scale = False
        temp_writer = PDFWriter(self.pdf_formatter, self.options)
        temp_writer.draw()

        page_height = LETTER[1]
        margin = 25

        if temp_writer.curr_y < margin:
            self.options.text_scale = (page_height - margin) / (page_height + (-1 * temp_writer.curr_y))

    def write_pdf(self, write_path: Path):
        self.packet.seek(0)
        new_pdf = PdfReader(self.packet)

        existing_pdf = PdfReader(self.options.template_path)

        output = PdfWriter()
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        output_stream = open(write_path, "wb")

        output.write(output_stream)
        output_stream.close()

    def draw(self):
        self.canvas.setFillColorRGB(0, 0, 0, 1)

        text_object = self.canvas.beginText(self.options.title_x, self.options.title_y)
        text_object.setFont("Helvetica-Bold", 18 * self.options.text_scale)
        self.canvas.setFillColorRGB(*self.options.secondary_color)

        text_object.textLine(self._title_text())
        self.canvas.drawText(text_object)

        locations = ["Fountain Court", "Westland House"]

        for i, location in enumerate(locations):
            performances = self.pdf_formatter.performances_for_location(location)

            if not performances:
                continue

            self._draw_header(location)
            for performance in performances:
                self._write_performance(performance)

            if i < len(locations) - 1:
                self.curr_y -= self.line_spacing

        self.canvas.save()

    def _write_performance(self, performance):
        text_object = self.canvas.beginText(self.curr_x, self.curr_y)

        text_object.setFont("Helvetica", 9 * self.options.text_scale)
        self.canvas.setFillColorRGB(0, 0, 0)

        text_object.textOut(performance.output_heavy())
        text_object.setFillColorRGB(0.4, 0.4, 0.4)
        text_object.textOut(performance.output_light())

        self.canvas.drawText(text_object)

        self.curr_y -= self.line_spacing

    def _title_text(self):
        if not self.options.title_text:
            return self.pdf_formatter.month + " performances " + u"\u2013" + " each lasting 60 minutes"

        return self.options.title_text

    def _draw_header(self, header_text, scale_header: bool = False):
        header_size = 14 * self.options.text_scale if scale_header else 14

        text_object = self.canvas.beginText(self.curr_x, self.curr_y)
        text_object.setFont("Helvetica-Bold", header_size)
        self.canvas.setFillColorRGB(*self.options.secondary_color)
        text_object.textLine(header_text)
        self.canvas.drawText(text_object)
        self.curr_y -= (self.line_spacing + self.before_header_spacing)
