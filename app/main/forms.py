import re
from flask import session
from datetime import datetime

from app.user_model.user_model import User

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, ValidationError, SelectField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


GENDERS = ['male', 'female']
PREFERENCES = ['bi-sexual', 'straight', 'homosexual']

class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    passwd = PasswordField('passwd', validators=[DataRequired()])
    
    
class RegistrationForm(FlaskForm):
    login = StringField('login')
    
    email = StringField('email')
    birth_date = StringField('birth_date')
    first_name = StringField('first_name')
    last_name = StringField('last_name')
    passwd = PasswordField('passwd')
    passwd_repeat = PasswordField('passwd_repeat')
    acept = BooleanField('acept')


    def validate_login(self, field):
        if re.fullmatch('^[a-z_\-A-Z0-9]{3,80}$', field.data) is None:
            raise ValidationError('Login should be between 3-80 characters long. Allowed characters are letters, numbers, "-", "_".')
        if User.login_exists(field.data):
            raise ValidationError('login occupied')
    
    def validate_email(self, field):
        if re.fullmatch('^[a-zA-Z0-9\-._]+@[a-zA-Z0-9._\-]+\.[a-zA-Z0-9_\-]+$', field.data) is None:
            raise ValidationError('Not a valid email address')
        if User.email_exists(field.data):
            raise ValidationError('email occupied')

    def validate_birth_date(self, field):
        date = datetime.strptime(field.data, '%d/%m/%Y')
        if (datetime.now().year - date.year) < 18:
            raise ValidationError('You are to young to enter this site. Ha-Ha-Ha!')

    def validate_first_name(self, field):
        if re.fullmatch('^[a-zA-Z\-]{1,80}$', field.data) is None:
            raise ValidationError('Is not a valid first name')

    def validate_last_name(self, field):
        if re.fullmatch('^[a-zA-Z\-]{1,80}$', field.data) is None:
            raise ValidationError('Is not a valid last name')
        
    def validate_passwd(self, field):
        if re.fullmatch('^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d\W]{8,30}$', field.data) is None:
            raise ValidationError('Password should be at least 8 characters long, contain at '
                                  'least one number and one letter')
    
    def validate_passwd_repeat(self, field):
        if self.passwd_repeat.data != self.passwd.data:
            raise ValidationError('Entered passwords does not match')

    def validate_acept(self, field):
        if field.data == False:
            raise ValidationError('Do you accept terms and conditions?')


class ProfileForm(FlaskForm):
    gender = SelectField(choices=[('male', 'male'), ('female', 'female')])
    preferences = SelectField(choices=[('bi-sexual', 'bi-sexual'), ('straight', 'straight'), ('homosexual', 'homosexual')])
    biography = StringField(widget=TextArea())
    interests = StringField(widget=TextArea())
    city = StringField(widget=TextArea())
    show_location = BooleanField()
    
    def validate_gender(self, field):
        if field.data not in GENDERS:
            raise ValidationError('Such kind of gender does not exist in our list')
        
    def validate_preferences(self, field):
        if field.data not in PREFERENCES:
            raise ValidationError('Such preferences does not exist in our list')
        
    def validate_biography(self, field):
        if re.match('.+', field.data) is None:
            raise ValidationError('At least a few words about who you are...')

    def validate_interests(self, field):
        if re.fullmatch('.*(#[\w]+).*', field.data) is None:
            raise ValidationError('Interests tags should begin with #')

    def validate_city(self, field):
        if re.fullmatch('.*[\w]+.*', field.data) is None:
            raise ValidationError('Zimbabwe?')


class EditProfileForm(FlaskForm):
    login = StringField('login')
    email = StringField('email')
    first_name = StringField('first_name')
    last_name = StringField('last_name')
    birth_date = StringField('birth_date')
    gender = SelectField(choices=[('male', 'male'), ('female', 'female')])
    preferences = SelectField(choices=[('bi-sexual', 'bi-sexual'), ('straight', 'straight'), ('homosexual', 'homosexual')])
    biography = StringField(widget=TextArea())
    interests = StringField(widget=TextArea())
    city = StringField(widget=TextArea())
    show_location = BooleanField()
    passwd = PasswordField('passwd')
    passwd_repeat = PasswordField('passwd_repeat')

    def validate_login(self, field):
        if re.fullmatch('^[a-z_\-A-Z0-9]{3,80}$', field.data) is None:
            raise ValidationError(
                'Login should be between 3-80 characters long. Allowed characters are letters, numbers, "-", "_".')
        if User.login_exists(field.data) and field.data != session['login']:
            raise ValidationError('login occupied')

    def validate_email(self, field):
        if re.fullmatch('^[a-zA-Z0-9\-._]+@[a-zA-Z0-9._\-]+\.[a-zA-Z0-9_\-]+$', field.data) is None:
            raise ValidationError('Not a valid email address')
        if User.email_exists(field.data) and field.data != User.get_email(session['id']):
            raise ValidationError('email occupied')

    def validate_birth_date(self, field):
        date = datetime.strptime(field.data, '%d/%m/%Y')
        if (datetime.now().year - date.year) < 18:
            raise ValidationError('You are to young to enter this site. Ha-Ha-Ha!')

    def validate_first_name(self, field):
        if re.fullmatch('^[a-zA-Z\-]{1,80}$', field.data) is None:
            raise ValidationError('Is not a valid first name')

    def validate_last_name(self, field):
        if re.fullmatch('^[a-zA-Z\-]{1,80}$', field.data) is None:
            raise ValidationError('Is not a valid last name')

    def validate_passwd(self, field):
        if field.data != '':
            if re.fullmatch('^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d\W]{8,30}$', field.data) is None:
                raise ValidationError('Password should be at least 8 characters long, contain at '
                                    'least one number and one letter')

    def validate_passwd_repeat(self, field):
        if self.passwd_repeat.data != self.passwd.data:
            raise ValidationError('Entered passwords does not match')

    def validate_gender(self, field):
        if field.data not in GENDERS:
            raise ValidationError('Such kind of gender does not exist in our list')

    def validate_preferences(self, field):
        if field.data not in PREFERENCES:
            raise ValidationError('Such preferences does not exist in our list')

    def validate_biography(self, field):
        if re.match('.+', field.data) is None:
            raise ValidationError('At least a few words about who you are...')

    def validate_interests(self, field):
        if re.fullmatch('.*(#[\w]+).*', field.data) is None:
            raise ValidationError('Interests tags should begin with #')

    def validate_city(self, field):
        if re.fullmatch('.*[\w]+.*', field.data) is None:
            raise ValidationError('Zimbabwe?')


class EditNotificationsForm(FlaskForm):
    likes_me = BooleanField()
    unlikes_me = BooleanField()
    likes_me_back = BooleanField()
    viewed_my_profile = BooleanField()
    incoming_massage = BooleanField()
    

class SendPasswordEmailForm(FlaskForm):
    email = StringField('email')
    
    def validate_email(self, field):
        if not User.email_exists(field.data):
            raise ValidationError('No such email in the database')


class NewPasswdForm(FlaskForm):
    passwd = PasswordField('passwd')

    def validate_passwd(self, field):
        if re.fullmatch('^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d\W]{8,30}$', field.data) is None:
            raise ValidationError('Password should be at least 8 characters long, contain at '
                                  'least one number and one letter')