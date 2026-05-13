import os
import uuid
from datetime import date, datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import bcrypt
from config import Config
from models import db, User, Author, Genre, Book, Loan
from forms import RegistrationForm, LoginForm, BookForm, LoanForm

# Инициализация Flask-приложения
app = Flask(__name__)
# Загрузка конфигурации из внешнего модуля
app.config.from_object(Config)
# Инициализация расширения базы данных
db.init_app(app)
# Настройка менеджера аутентификации
login_manager = LoginManager()
login_manager.init_app(app)
# Маршрут для перенаправления неавторизованных пользователей
login_manager.login_view = 'login'

# Загрузка объекта пользователя по его ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Создание директории для загрузки обложек, если она отсутствует
def ensure_upload_folder():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Сохранение загруженного файла обложки с уникальным именем
def save_cover(cover_file, book_id=None):
    if not cover_file:
        return None
    ext = cover_file.filename.rsplit('.', 1)[1].lower()
    if book_id:
        filename = f"cover_{book_id}{uuid.uuid4().hex[:8]}.{ext}"
    else:
        filename = f"cover_temp{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cover_file.save(filepath)
    return filename

# Удаление файла обложки по указанному пути
def delete_cover(cover_path):
    if cover_path:
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_path)
        if os.path.exists(full_path):
            os.remove(full_path)

# Главная страница: фильтрация, поиск и сортировка книг
@app.route('/')
def index():
    # Показываем пустую страницу гостям
    if not current_user.is_authenticated:
        return render_template('index.html', books=None, authors=[], genres=[], borrowers=[])
    
    # Базовый запрос: только книги текущего пользователя
    query = Book.query.filter_by(user_id=current_user.id)
    
    # Применение фильтров из GET-параметров
    author_id = request.args.get('author', type=int)
    if author_id:
        query = query.filter_by(author_id=author_id)

    genre_id = request.args.get('genre', type=int)
    if genre_id:
        query = query.filter_by(genre_id=genre_id)

    status = request.args.get('status')
    if status == 'loaned':
        query = query.filter_by(is_loaned=True)
    elif status == 'available':
        query = query.filter_by(is_loaned=False)

    borrower_filter = request.args.get('borrower', '')
    if borrower_filter:
        query = query.join(Loan, Book.id == Loan.book_id).filter(
            Loan.return_date == None,
            Loan.borrower_name.ilike(f'%{borrower_filter}%')
        )

    search = request.args.get('search', '')
    if search:
        query = query.filter(Book.title.ilike(f'%{search}%'))

    # Сортировка результатов
    sort = request.args.get('sort', 'added_date')
    if sort == 'title':
        query = query.order_by(Book.title)
    elif sort == 'author_name':
        query = query.join(Author).order_by(Author.name)
    elif sort == 'added_date':
        query = query.order_by(Book.added_date.desc())
    else:
        query = query.order_by(Book.added_date.desc())

    books = query.all()
    authors = Author.query.filter_by(user_id=current_user.id).order_by(Author.name).all()
    genres = Genre.query.filter_by(user_id=current_user.id).order_by(Genre.name).all()

    # Сбор уникальных имён активных заемщиков
    active_loans = Loan.query.join(Book).filter(
        Book.user_id == current_user.id,
        Loan.return_date == None
    ).distinct(Loan.borrower_name).all()
    borrowers = sorted(set(loan.borrower_name for loan in active_loans))

    return render_template('index.html', 
                           books=books, 
                           authors=authors, 
                           genres=genres,
                           borrowers=borrowers,
                           selected_author=author_id, 
                           selected_genre=genre_id, 
                           selected_status=status,
                           selected_borrower=borrower_filter,
                           search_query=search, 
                           current_sort=sort)

# Регистрация нового аккаунта
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(username=form.username.data, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Авторизация пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

# Выход из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Добавление новой книги в библиотеку
@app.route('/book/add', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    form.author.choices = [(0, '-- Select author --')] + [(a.id, a.name) for a in Author.query.filter_by(user_id=current_user.id).order_by(Author.name)]
    form.genre.choices = [(0, '-- Select genre --')] + [(g.id, g.name) for g in Genre.query.filter_by(user_id=current_user.id).order_by(Genre.name)]
    
    if form.validate_on_submit():
        author_id = form.author.data
        # Создание нового автора, если указано имя
        if form.new_author.data and form.new_author.data.strip():
            new_author_name = form.new_author.data.strip()
            author = Author.query.filter_by(user_id=current_user.id, name=new_author_name).first()
            if not author:
                author = Author(name=new_author_name, user_id=current_user.id)
                db.session.add(author)
                db.session.flush()
            author_id = author.id

        genre_id = form.genre.data
        # Создание нового жанра, если указано имя
        if form.new_genre.data and form.new_genre.data.strip():
            new_genre_name = form.new_genre.data.strip()
            genre = Genre.query.filter_by(user_id=current_user.id, name=new_genre_name).first()
            if not genre:
                genre = Genre(name=new_genre_name, user_id=current_user.id)
                db.session.add(genre)
                db.session.flush()
            genre_id = genre.id

        if not author_id or author_id == 0:
            flash('Please select an author from the list or add a new one using the "Or add new author" field.', 'danger')
            return redirect(url_for('add_book'))
        if not genre_id or genre_id == 0:
            flash('Please select a genre from the list or add a new one using the "Or add new genre" field.', 'danger')
            return redirect(url_for('add_book'))

        cover_filename = None
        if form.cover.data:
            cover_filename = save_cover(form.cover.data)

        book = Book(
            title=form.title.data,
            year=form.year.data,
            user_id=current_user.id,
            author_id=author_id,
            genre_id=genre_id,
            cover_path=cover_filename
        )
        db.session.add(book)
        db.session.commit()

        # Переименование временного файла после получения ID книги
        if cover_filename and 'temp' in cover_filename:
            ext = cover_filename.split('.')[-1]
            new_name = f"cover_{book.id}_{uuid.uuid4().hex[:8]}.{ext}"
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)
            new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
            os.rename(old_path, new_path)
            book.cover_path = new_name
            db.session.commit()

        flash('Book added successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('add_book.html', form=form)

# Редактирование существующей книги
@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()
    form = BookForm(obj=book)
    form.author.choices = [(0, '-- Select author --')] + [(a.id, a.name) for a in Author.query.filter_by(user_id=current_user.id).order_by(Author.name)]
    form.genre.choices = [(0, '-- Select genre --')] + [(g.id, g.name) for g in Genre.query.filter_by(user_id=current_user.id).order_by(Genre.name)]
    form.author.data = book.author_id
    form.genre.data = book.genre_id
    
    if form.validate_on_submit():
        author_id = form.author.data
        if form.new_author.data and form.new_author.data.strip():
            new_author_name = form.new_author.data.strip()
            author = Author.query.filter_by(user_id=current_user.id, name=new_author_name).first()
            if not author:
                author = Author(name=new_author_name, user_id=current_user.id)
                db.session.add(author)
                db.session.flush()
            author_id = author.id

        genre_id = form.genre.data
        if form.new_genre.data and form.new_genre.data.strip():
            new_genre_name = form.new_genre.data.strip()
            genre = Genre.query.filter_by(user_id=current_user.id, name=new_genre_name).first()
            if not genre:
                genre = Genre(name=new_genre_name, user_id=current_user.id)
                db.session.add(genre)
                db.session.flush()
            genre_id = genre.id

        if not author_id or author_id == 0:
            flash('Please select an author or add a new one.', 'danger')
            return redirect(url_for('edit_book', book_id=book_id))
        if not genre_id or genre_id == 0:
            flash('Please select a genre or add a new one.', 'danger')
            return redirect(url_for('edit_book', book_id=book_id))

        book.title = form.title.data
        book.year = form.year.data
        book.author_id = author_id
        book.genre_id = genre_id

        if form.cover.data:
            delete_cover(book.cover_path)
            new_cover = save_cover(form.cover.data, book.id)
            book.cover_path = new_cover

        db.session.commit()
        flash('Book updated successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('edit_book.html', form=form, book=book)

# Удаление книги и её обложки
@app.route('/book/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()
    delete_cover(book.cover_path)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'success')
    return redirect(url_for('index'))

# Оформление выдачи книги
@app.route('/book/<int:book_id>/loan', methods=['GET', 'POST'])
@login_required
def loan_book(book_id):
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()
    if book.is_loaned:
        flash('This book is already loaned out.', 'warning')
        return redirect(url_for('index'))
    form = LoanForm()
    if form.validate_on_submit():
        loan = Loan(
            borrower_name=form.borrower_name.data,
            loan_date=date.today(),
            book_id=book.id
        )
        book.is_loaned = True
        db.session.add(loan)
        db.session.commit()
        flash(f'Book loaned to {form.borrower_name.data}.', 'success')
        return redirect(url_for('index'))
    return render_template('loan_book.html', form=form, book=book)

# Возврат книги в библиотеку
@app.route('/book/<int:book_id>/return', methods=['POST'])
@login_required
def return_book(book_id):
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()
    if not book.is_loaned:
        flash('This book is not currently loaned.', 'info')
        return redirect(url_for('index'))
    loan = Loan.query.filter_by(book_id=book.id, return_date=None).first()
    if loan:
        loan.return_date = date.today()
        book.is_loaned = False
        db.session.commit()
        flash('Book returned.', 'success')
        return redirect(url_for('index'))

# REST API для получения списка книг в формате JSON
@app.route('/api/books')
def api_books():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    books = Book.query.filter_by(user_id=current_user.id).all()
    result = []
    for b in books:
        result.append({
            'id': b.id,
            'title': b.title,
            'year': b.year,
            'author': b.author.name,
            'genre': b.genre.name,
            'is_loaned': b.is_loaned,
            'cover_path': b.cover_path
        })
    return jsonify(result)

# Запуск сервера разработки
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_upload_folder()
    app.run(debug=True)