from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class MainForm(FlaskForm):
    text = TextAreaField('Запрос', validators=[DataRequired()])
    submit = SubmitField('Запромптить')
