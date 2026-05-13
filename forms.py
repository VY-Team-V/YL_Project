from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import datetime

# Форма регистрации нового аккаунта
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

# Форма авторизации
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Форма добавления или редактирования информации о книге
class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    year = IntegerField('Year', validators=[Optional(), NumberRange(min=0, max=datetime.now().year)])
    author = SelectField('Author', choices=[], coerce=int, validators=[Optional()])
    new_author = StringField('Or add new author', validators=[Optional()])
    genre = SelectField('Genre', choices=[], coerce=int, validators=[Optional()])
    new_genre = StringField('Or add new genre', validators=[Optional()])
    cover = FileField('Cover image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Save')

# Форма оформления выдачи книги читателю
class LoanForm(FlaskForm):
    borrower_name = StringField('Borrower name', validators=[DataRequired()])
    submit = SubmitField('Loan out')