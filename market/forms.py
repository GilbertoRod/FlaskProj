from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from market.models import User

class RegisterForm(FlaskForm):

  #function that checks if a username is already existing in the database
  def validate_username(self, username_to_check):
    user=User.query.filter_by(username=username_to_check.data).first()
    if user:
      raise ValidationError('Username already exists, please try a different username')

  def validate_email_address(self, email_address_to_check):
    email_address=User.query.filter_by(email_address=email_address_to_check.data).first()
    if email_address:
      raise ValidationError('Email Address already exists, please try a different username')

  username = StringField(label='Username: ', validators=[Length(min=2,max=30), DataRequired()])
  first_name = StringField(label='First Name: ', validators=[Length(max=50), DataRequired()])
  last_name = StringField(label='Last Name: ', validators=[Length(max=50), DataRequired()])
  email_address= StringField(label='Email: ', validators=[Email(), DataRequired()])
  password1 = PasswordField(label='Password: ', validators=[Length(min=6), DataRequired()])
  password2 = PasswordField(label='Confirm Password: ', validators= [EqualTo('password1'), DataRequired()])
  submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
  username = StringField(label='Username:', validators=[DataRequired()])
  password = PasswordField(label='Password: ', validators=[DataRequired()])
  submit = SubmitField(label='Sign In')

