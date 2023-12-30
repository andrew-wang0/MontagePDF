from pathlib import Path

from PIL import ImageColor
from flask import Blueprint, render_template, send_file

from .forms import ToolForm
from .util.pdf_formatter import PDFFormatter
from .util.pdf_writer import PDFWriterOptions, PDFWriter

views = Blueprint('routes', __name__)


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

        if not form.template_pdf.data:
            template_path = Path(views.root_path, 'files', 'base', 'base.pdf')
        else:
            template_path = save_custom_template_pdf(form.template_pdf.data)

        options = PDFWriterOptions(
            header_text=form.header_text.data,
            template_path=template_path,
            secondary_color=[val / 255 for val in ImageColor.getrgb(form.secondary_color.data)],
            header_scale=float(form.header_scale.data),
            text_scale=float(form.text_scale.data),
            header_x=form.header_x.data,
            header_y=form.header_y.data,
            text_x=form.text_x.data,
            text_y=form.text_y.data,
        )

        write_path = Path(views.root_path, 'files', 'output.new.pdf')

        PDFWriter(PDFFormatter(save_path), options).write_pdf(write_path)

        return send_file(write_path)

    return render_template('pdf_tool.html', form=form)
