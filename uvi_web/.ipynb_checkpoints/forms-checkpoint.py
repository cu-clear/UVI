#uvi_web/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class SomeForm(FlaskForm):
	name = StringField('name_x', validators=[DataRequired()])