from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DecisionForm(FlaskForm):
    title = StringField('Decision Title', validators=[DataRequired(), Length(max=200)])
    context = TextAreaField('Context / Problem Statement', validators=[DataRequired()])
    alternatives = TextAreaField('Alternatives Considered', validators=[Optional()])
    chosen_option = TextAreaField('Chosen Option', validators=[DataRequired()])
    rationale = TextAreaField('Rationale', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Draft', 'Draft'),
        ('Recorded', 'Recorded'),
        ('Implemented', 'Implemented'),
        ('Under Review', 'Under Review'),
        ('Closed', 'Closed')
    ], default='Recorded')
    tags = StringField('Tags (comma separated)', validators=[Optional()])
    project = StringField('Related Project / Module', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Save Decision')

class OutcomeForm(FlaskForm):
    result = SelectField('Outcome Result', choices=[
        ('Good', 'Good'),
        ('Neutral', 'Neutral'),
        ('Bad', 'Bad')
    ], validators=[DataRequired()])
    impact = TextAreaField('Impact / Results Observed', validators=[Optional()])
    lessons_learned = TextAreaField('Lessons Learned', validators=[Optional()])
    submit = SubmitField('Save Outcome')

class CommentForm(FlaskForm):
    content = TextAreaField('Add a Comment', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Post Comment')