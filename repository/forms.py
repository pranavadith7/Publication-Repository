from os import access
import unicodedata
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, \
    FileField, TextAreaField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from wtforms.widgets import TextArea
from repository.models import Department, DepartmentAreas, PaperType, PublishPaper, User, Role, Institution, PaperAccessEnum
from datetime import datetime


class RegistrationForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Create Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    role = SelectField('You are a', choices=[('student', 'Student'), ('faculty', 'Faculty')], validators=[DataRequired()])
    institution = SelectField('You belong to', \
        choices=[(institution.id, institution.name) for institution in Institution.query.all()], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please use a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class EditProfileForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('You are a', choices=[('student', 'Student'), ('faculty', 'Faculty')], validators=[DataRequired()])
    institution = SelectField('You belong to', \
        choices=[(institution.id, institution.name) for institution in Institution.query.all()], validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_role(self, role):
        if role.data == 'student':
            if Institution.query.filter_by(student_email_server=self.email.data.split('@')[1]).first() is None:
                raise ValidationError('University email does not exist')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')

class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account for this email. Register first')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

def getDepartmentAreaChoices():
    choices = list()
    for department in Department.query.all():
        choices.append((department.name, tuple([(department_area.id, department_area.name) for department_area in department.department_areas])))
    return choices

class PublishPaperForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=255)])
    abstract = TextAreaField('Abstract', widget=TextArea(), validators=[DataRequired()])
    paper_type = SelectField('Paper Type',
        choices=[(paper_type.id, paper_type.name) for paper_type in PaperType.query.all()], validators=[DataRequired()])
    department_area = SelectField('Department Area Collection',
        choices=[(str(department_area.id), department_area.name) for department_area in DepartmentAreas.query.all()], validators=[DataRequired()])
    authors = SelectMultipleField(choices=[(str(user.id), user.fname + " " + user.lname + " @" + user.email[:user.email.index('@')]) for user in User.getWhoCanPublish()],
        validators=[DataRequired()])
    citations = SelectMultipleField('Citations',
        choices=[(str(pub_paper.id), pub_paper.title + " #" + pub_paper.unique_paper_id) for pub_paper in PublishPaper.query.all()])
    publisher = StringField('Publisher', validators=[DataRequired(), Length(min=1, max=255)])
    published_year = IntegerField('Publishing Year', validators=[DataRequired(), NumberRange(min=1950, max=datetime.utcnow().year)])
    access = SelectField('Access', choices=PaperAccessEnum.fetch_fields(), validators=[DataRequired()])
    paper_file = FileField('Upload file', validators=[FileAllowed(['pdf', 'csv', 'tsv', 'json', 'xlsx'])])
    submit = SubmitField('Publish Paper')

class EditPublishPaperForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=255)])
    abstract = TextAreaField('Abstract', widget=TextArea(), validators=[DataRequired()])
    paper_type = SelectField('Paper Type',
        choices=[(paper_type.id, paper_type.name) for paper_type in PaperType.query.all()], validators=[DataRequired()])
    department_area = SelectField('Department Area Collection',
        choices=[(str(department_area.id), department_area.name) for department_area in DepartmentAreas.query.all()], validators=[DataRequired()])
    authors = SelectMultipleField(choices=[(str(user.id), user.fname + " " + user.lname + " @" + user.email[:user.email.index('@')]) for user in User.getWhoCanPublish()],
        validators=[DataRequired()])
    citations = SelectMultipleField('Citations',
        choices=[(str(pub_paper.id), pub_paper.title + " #" + pub_paper.unique_paper_id) for pub_paper in PublishPaper.query.all()])
    publisher = StringField('Publisher', validators=[DataRequired(), Length(min=1, max=255)])
    published_year = IntegerField('Publishing Year', validators=[DataRequired(), NumberRange(min=1950, max=datetime.utcnow().year)])
    access = SelectField('Access', choices=PaperAccessEnum.fetch_fields(), validators=[DataRequired()])
    paper_file = FileField('Upload file', validators=[FileAllowed(['pdf', 'csv', 'tsv', 'json', 'xlsx'])])
    submit = SubmitField('Update Paper')

class EditFacultyProfileForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=20)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    # role = SelectField('You are a', choices=[('student', 'Student'), ('faculty', 'Faculty')], validators=[DataRequired()])
    institution = SelectField('You belong to', \
        choices=[(institution.id, institution.name) for institution in Institution.query.all()], validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    address = StringField('Address', validators=[Length(max=100)])
    phone_number = StringField('Phone Number', validators=[Length(max=15)])
    work_exp = StringField('Work Experience', validators=[DataRequired(), Length(min=1, max=255)])
    about_me = TextAreaField('Abstract', widget=TextArea(), render_kw={"rows": 5, "cols": 50}, validators=[DataRequired()])
    designation = StringField('Designation', validators=[DataRequired(), Length(min=1, max=100)])
    department = StringField('Department', validators=[DataRequired(), Length(min=1, max=100)])
    github = StringField('GitHub Link', validators=[Length(max=150)])
    linkedin = StringField('Linkedin Link', validators=[Length(max=150)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_role(self, role):
        if role.data == 'student':
            if Institution.query.filter_by(student_email_server=self.email.data.split('@')[1]).first() is None:
                raise ValidationError('University email does not exist')
