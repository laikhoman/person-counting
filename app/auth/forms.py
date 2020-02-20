from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1, 64), \
											 Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Keep me Logged in')
	submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(), Length(1, 64)])
	email = StringField('Email', validators=[DataRequired(), Length(1, 64), \
											 Email()])
	password = PasswordField('Password', validators=[DataRequired(), \
													 EqualTo('confirmPassword', message='Passwords must be match with password confirmation.')])
	confirmPassword = PasswordField('Confirm Password', validators=[DataRequired()])
	submit = SubmitField('Register')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data.lower()).first():
			raise ValidationError('Email already registered.')