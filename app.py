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

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def ensure_upload_folder():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def save_cover(cover_file, book_id=None):
    if not cover_file:
        return None
    ext = cover_file.filename.rsplit('.', 1)[1].lower()
    if book_id:
        filename = f"cover_{book_id}_{uuid.uuid4().hex[:8]}.{ext}"
    else:
        filename = f"cover_temp_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cover_file.save(filepath)
    return filename

def delete_cover(cover_path):
    if cover_path:
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_path)
        if os.path.exists(full_path):
            os.remove(full_path)

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html', books=None, authors=[], genres=[])
    query = Book.query.filter_by(user_id=current_user.id)
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
    search = request.args.get('search', '')
    if search:
        query = query.filter(Book.title.ilike(f'%{search}%'))
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
    return render_template('index.html', books=books, authors=authors, genres=genres,
                           selected_author=author_id, selected_genre=genre_id, selected_status=status,
                           search_query=search, current_sort=sort)

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/book/add', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    form.author.choices = [(0, '-- Select author --')] + [(a.id, a.name) for a in Author.query.filter_by(user_id=current_user.id).order_by(Author.name)]
    form.genre.choices = [(0, '-- Select genre --')] + [(g.id, g.name) for g in Genre.query.filter_by(user_id=current_user.id).order_by(Genre.name)]

    if form.validate_on_submit():
        author_id = form.author.data
        if form.new_author.data:
            new_author_name = form.new_author.data.strip()
            if new_author_name:
                author = Author.query.filter_by(user_id=current_user.id, name=new_author_name).first()
                if not author:
                    author = Author(name=new_author_name, user_id=current_user.id)
                    db.session.add(author)
                    db.session.flush()
                author_id = author.id
        genre_id = form.genre.data
        if form.new_genre.data:
            new_genre_name = form.new_genre.data.strip()
            if new_genre_name:
                genre = Genre.query.filter_by(user_id=current_user.id, name=new_genre_name).first()
                if not genre:
                    genre = Genre(name=new_genre_name, user_id=current_user.id)
                    db.session.add(genre)
                    db.session.flush()
                genre_id = genre.id

        if author_id == 0 or genre_id == 0:
            flash('Please select or add a valid author and genre.', 'danger')
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

        if cover_filename and 'temp' in cover_filename:
            new_name = f"cover_{book.id}_{uuid.uuid4().hex[:8]}.{cover_filename.split('.')[-1]}"
            old_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_filename)
            new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
            os.rename(old_path, new_path)
            book.cover_path = new_name
            db.session.commit()

        flash('Book added successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('add_book.html', form=form)

@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()
    form = BookForm(obj=book)
    form.author.choices = [(a.id, a.name) for a in Author.query.filter_by(user_id=current_user.id).order_by(Author.name)]
    form.genre.choices = [(g.id, g.name) for g in Genre.query.filter_by(user_id=current_user.id).order_by(Genre.name)]
    form.author.data = book.author_id
    form.genre.data = book.genre_id

    if form.validate_on_submit():
        author_id = form.author.data
        if form.new_author.data:
            new_author_name = form.new_author.data.strip()
            if new_author_name:
                author = Author.query.filter_by(user_id=current_user.id, name=new_author_name).first()
                if not author:
                    author = Author(name=new_author_name, user_id=current_user.id)
                    db.session.add(author)
                    db.session.flush()
                author_id = author.id
        genre_id = form.genre.data
        if form.new_genre.data:
            new_genre_name = form.new_genre.data.strip()
            if new_genre_name:
                genre = Genre.query.filter_by(user_id=current_user.id, name=new_genre_name).first()
                if not genre:
                    genre = Genre(name=new_genre_name, user_id=current_user.id)
                    db.session.add(genre)
                    db.session.flush()
                genre_id = genre.id

        if author_id == 0 or genre_id == 0:
            flash('Please select or add a valid author and genre.', 'danger')
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

@app.route('/book/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.filter_by(id=book_id, user_id=current_user.id).first_or_404()
    delete_cover(book.cover_path)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'success')
    return redirect(url_for('index'))

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

# API
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_upload_folder()
    app.run(debug=True)