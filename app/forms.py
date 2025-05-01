from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    sales_file = FileField('Sales Data File', validators=[DataRequired()])
    stock_file = FileField('Stock Data File', validators=[DataRequired()])
    submit = SubmitField('Upload')