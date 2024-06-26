from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, ColorField, DecimalField, IntegerField, StringField, BooleanField
from wtforms.validators import ValidationError, DataRequired


def FileSizeLimit(max_size_in_mb):
    max_bytes = max_size_in_mb * 1024 * 1024

    def file_length_check(_form, field):
        if not field.data:
            return

        if len(field.data.read()) > max_bytes:
            raise ValidationError(f'File size is too large. Max allowed: {max_size_in_mb} MB')
        field.data.seek(0)

    return file_length_check


class ToolForm(FlaskForm):
    calendar_pdf = FileField('Upload Calendar PDF',
                             validators=[FileRequired(), FileAllowed(['pdf']), FileSizeLimit(1)])

    template_pdf = FileField('Upload Template PDF (optional, leave blank for default background)',
                             validators=[FileAllowed(['pdf']), FileSizeLimit(1)])

    secondary_color = ColorField(label='Secondary Color', default='#c3d924')

    title_scale = DecimalField(default=Decimal(1.0))
    text_scale = DecimalField(default=Decimal(1.0), label='Text Scale (leave 1 for auto scaling)')

    title_text = StringField(label='Title Text (Optional)')

    title_x = IntegerField(default=40, validators=[DataRequired()])
    title_y = IntegerField(default=578, validators=[DataRequired()])

    text_x = IntegerField(default=40, validators=[DataRequired()])
    text_y = IntegerField(default=530, validators=[DataRequired()])

    submit = SubmitField('Submit')
