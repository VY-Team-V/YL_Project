import bcrypt
import pytest
from app import app, db
from models import User, Book, Author, Genre

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            hashed = bcrypt.hashpw('testpass'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user = User(username='testuser', password=hashed)
            db.session.add(user)
            db.session.commit()
            author = Author(name='Test Author', user_id=user.id)
            genre = Genre(name='Fiction', user_id=user.id)
            db.session.add_all([author, genre])
            db.session.commit()
            book = Book(title='Test Book', user_id=user.id, author_id=author.id, genre_id=genre.id)
            db.session.add(book)
            db.session.commit()
        yield client

def test_api_unauthorized(client):
    response = client.get('/api/books')
    assert response.status_code == 401

def test_api_authorized(client):
    client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    response = client.get('/api/books')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['title'] == 'Test Book'
    assert 'author' in data[0]
    assert 'is_loaned' in data[0]