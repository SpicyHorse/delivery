from flaskext.wtf import Form, TextField, Required, BooleanField, PasswordField, HiddenField, SelectField, validators
import re

strict_name_validators = [
	validators.Required(),
	validators.Regexp(r'[a-zA-Z0-9]{1,128}', re.IGNORECASE, "Require to be [a-zA-Z0-9]{1,128}")
]

class UserRegistrationForm(Form):
	name		= TextField('Name', [ validators.Required() ])
	email		= TextField('Email', [ validators.Email() ])
	password	= PasswordField('Password', [ validators.Required(), validators.EqualTo('confirm', message='Passwords must match') ])
	confirm		= PasswordField('Repeat Password')
	invite		= TextField('Invite code', [ validators.Required() ])

class UserEmailForm(Form):
	email		= TextField('Email', [ validators.Email() ])

class UserPasswordForm(Form):
	password	= PasswordField('Password', [ validators.Required(), validators.EqualTo('confirm', message='Passwords must match') ])
	confirm		= PasswordField('Repeat Password')

class UserLoginForm(Form):
	email		= TextField('Email', [ validators.Email() ])
	password	= PasswordField('Password', [ validators.Required() ])
	remember	= BooleanField('Remember for 1 month')
	next		= HiddenField('next', [ validators.Required() ], default="/")

class ChannelForm(Form):
	name		= TextField('Name', strict_name_validators)
	description	= TextField('Description')

class GameForm(Form):
	name		= TextField('Name', strict_name_validators)
	url			= TextField('Url', [ validators.Required() ])
	description	= TextField('Description')

class BuildForm(Form):
	name		= TextField('Name', strict_name_validators)
	description	= TextField('Description')
	platform	= SelectField('Platform', choices=[('WIN','Windows'), ('MAC','MacOS'), ('LIN', 'Linux')])