from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Инициализация ORM для работы с базой данных
db = SQLAlchemy()

# Модель пользователя с интеграцией Flask-Login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    books = db.relationship('Book', backref='user', lazy=True, cascade='all, delete-orphan')
    authors = db.relationship('Author', backref='user', lazy=True, cascade='all, delete-orphan')
    genres = db.relationship('Genre', backref='user', lazy=True, cascade='all, delete-orphan')

# Модель автора книги
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    books = db.relationship('Book', backref='author', lazy=True)

# Модель жанра книги
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    books = db.relationship('Book', backref='genre', lazy=True)

# Модель книги
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer)
    cover_path = db.Column(db.String(300))
    is_loaned = db.Column(db.Boolean, default=False)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)
    loans = db.relationship('Loan', backref='book', lazy=True, cascade='all, delete-orphan')

    # Свойство для получения имени текущего читателя
    @property
    def current_borrower(self):
        if self.is_loaned:
            active_loan = Loan.query.filter_by(book_id=self.id, return_date=None).first()
            return active_loan.borrower_name if active_loan else None
        return None

# Модель записи о выдаче книги читателю
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    borrower_name = db.Column(db.String(100), nullable=False)
    loan_date = db.Column(db.Date, default=datetime.utcnow)
    return_date = db.Column(db.Date, nullable=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)