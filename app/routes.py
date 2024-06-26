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
    save_path = Path(views.root_path, 'files', 'template', 'custom_base.pdf')
    pdf.save(save_path)
    return save_path


@views.route('/', methods=['GET', 'POST'])
def pdf_tool():
    form = ToolForm()

    if form.validate_on_submit():
        save_path = save_calendar_pdf(form.calendar_pdf.data)

        if not form.template_pdf.data:
            template_path = Path(views.root_path, 'files', 'template', 'base.pdf')
        else:
            template_path = save_custom_template_pdf(form.template_pdf.data)

        options = PDFWriterOptions(
            title_text=form.title_text.data,
            template_path=template_path,
            secondary_color=[val / 255 for val in ImageColor.getrgb(form.secondary_color.data)],
            title_scale=float(form.title_scale.data),
            text_scale=float(form.text_scale.data),
            title_x=form.title_x.data,
            title_y=form.title_y.data,
            text_x=form.text_x.data,
            text_y=form.text_y.data,
            text_auto_scale=float(form.text_scale.data) == 1.0
        )

        write_path = Path(views.root_path, 'files', 'output.pdf')

        pdf_formatted = PDFFormatter(save_path)

        pdf_writer = PDFWriter(pdf_formatted, options)
        pdf_writer.draw()
        pdf_writer.write_pdf(write_path)

        return send_file(write_path, download_name=pdf_formatted.month + ' Flier.pdf', as_attachment=True)

    return render_template('pdf_tool.html', form=form)
