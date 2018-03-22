from flask_wtf import Form
from wtforms import BooleanField
from wtforms import PasswordField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length

class LoginForm(Form):
	nickname = StringField('nickname',validators=[DataRequired()])
	password = PasswordField('password',validators=[DataRequired(),Length(min=5)])

class EditForm(Form):
	nickname=StringField('nickname',validators=[DataRequired()])
	about_me=TextAreaField('about_me',validators=[Length(min=0,max=140)])

class RegisterForm(Form):
	nickname=StringField('nickname',validators=[DataRequired()])
	email=StringField('email',validators=[DataRequired(),Email()])
	password=PasswordField('password',validators=[Length(min=5),DataRequired(),EqualTo('confirm',message='Password must match')])
	confirm=PasswordField('confirm')

class PostingForm(Form):
	text=TextAreaField('text',validators=[
		DataRequired(),
		Length(max=500)
		]
	)

class SearchForm(Form):
	search=StringField('search',validators=[DataRequired()])
