from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms import ValidationError
from ..models import Cctv

class AddCctvForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password =  StringField('password', validators=[DataRequired()])
    submit = SubmitField('create')

class EditCctvForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    submit = SubmitField('save')

class AddCameraForm(FlaskForm):
    label = StringField('Label', validators=[DataRequired()])
    url = StringField('Url', validators=[DataRequired()])
    submit = SubmitField('save')

class EditCameraForm(FlaskForm):
    channel = StringField('Camera channel', validators=[DataRequired()])
    submit = SubmitField('save')

class AddPlaceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('save')

class EditPlaceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('save')

class CoordinateForm(FlaskForm):
    x1 = StringField('X1', validators=[DataRequired()])
    y1 = StringField('Y1', validators=[DataRequired()])
    x2 = StringField('X2', validators=[DataRequired()])
    y2 = StringField('Y2', validators=[DataRequired()])
    submit = SubmitField('save')

class DateForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('save')




