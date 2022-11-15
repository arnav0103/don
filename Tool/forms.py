from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField ,SubmitField , TextAreaField , FileField , IntegerField , RadioField
from wtforms.validators import DataRequired, Email , EqualTo, Length
from flask_wtf.file import FileField,FileAllowed
from wtforms import ValidationError

from flask_login import current_user
from Tool.models import User


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    name = StringField('First Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),EqualTo('pass_confirm', message='Passwords must match'), Length(min = 8, max=16)])
    pass_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    picture = FileField(' Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('The email you chose has already been registered')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username yuo chose has already been registered')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class MakeTeamForm(FlaskForm):
    team_name = StringField('Team Name', validators=[DataRequired()])
    team_password = PasswordField('Password', validators=[DataRequired(),EqualTo('team_pass_confirm', message='Passwords must match'), Length(min = 8, max=16)])
    team_pass_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    picture = FileField('Upload Team picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Make Team')



class TeamLoginForm(FlaskForm):
    randomid = StringField('Team Id', validators=[DataRequired()])
    team_password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Enter Team')

class MakeUpcoming(FlaskForm):
    title = StringField('Event Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Place Event')
class UpdateUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    username = StringField('Username', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_email(self,field):
        if field.data != current_user.email:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('The email you chose has already been registered')
    def validate_username(self,field):
        if field.data != current_user.username:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError('The username you chose has already been registered')

class UpdateTeamForm(FlaskForm):
    randomid = StringField('Team id', validators=[DataRequired()])
    name = StringField('Team Name', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_email(self,field):
        if field.data != current_user.randomid:
            if Team.query.filter_by(randomid=field.data).first():
                raise ValidationError('The id you chose has already been registered')

class Make_Rental(FlaskForm):
    thing = StringField('Product name for renting', validators=[DataRequired()])
    description = TextAreaField('Description',  validators = [DataRequired()])
    price = IntegerField('Price(in Rupees per month)' , validators=[DataRequired()])
    picture = FileField('Update A Picture', validators=[FileAllowed(['jpg', 'png']), DataRequired()])
    submit = SubmitField('Upload')

class UpdateRent(FlaskForm):
    thing = StringField('Thing', validators=[DataRequired()])
    description = TextAreaField('Deascription', validators=[DataRequired()])
    picture = FileField('Update Picture', validators=[FileAllowed(['jpg', 'png'])])
    price = IntegerField('Update Free' , validators = [DataRequired()])
    rent = RadioField('Is the object rented', choices=[('Yes','Rented'),('No','Not Until Now/it can re-rented')])
    submit = SubmitField('Update')

class KnowledgeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Upload')

class UpdateKnowledgeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Update Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
