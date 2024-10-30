import pytest
import json
from base64 import b64encode
from App2 import App as flask_app, db, User  # Adjust the import path according to your project structure

@pytest.fixture
def app():
    """Configure the Flask application for testing."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "mysql+pymysql://root:root@localhost/testdb",  # Adjust for testing
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })
    with flask_app.app_context():
        db.create_all()
        yield flask_app  # this allows for teardown after tests run
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

def register_user(client, email, password, first_name, last_name):
    return client.post('/v1/user', json={
        'email': email,
        'password': password,
        'first_name': first_name,
        'last_name': last_name
    })

def authenticate_user(client, email, password):
    credentials = b64encode(f"{email}:{password}".encode('utf-8')).decode('utf-8')
    return client.get('/v1/user/self', headers={'Authorization': f'Basic {credentials}'})

def test_create_and_validate_account(client):
    email = 'testcreate@example.com'
    password = 'testpassword'
    first_name = 'TestCreate'
    last_name = 'User'
    response = register_user(client, email, password, first_name, last_name)
    assert response.status_code == 201

    user = User.query.filter_by(email=email).first()
    user.isverified = True
    db.session.commit()

    auth_response = authenticate_user(client, email, password)
    assert auth_response.status_code == 200
    user_data = json.loads(auth_response.data)
    assert user_data['email'] == email
    assert user_data['first_name'] == first_name
    assert user_data['last_name'] == last_name

def test_update_and_validate_account(client):
    email = 'testupdate@example.com'
    password = 'testpassword'
    first_name = 'TestUpdate'
    last_name = 'User'
    # Create user first
    register_user(client, email, password, first_name, last_name)

    user = User.query.filter_by(email=email).first()
    user.isverified = True
    db.session.commit()
    # Update user
    update_response = client.put('/v1/user/self', headers={'Authorization': 'Basic ' + b64encode(f"{email}:{password}".encode('utf-8')).decode('utf-8')}, json={'first_name': 'UpdatedName', 'last_name': 'UpdatedUser'})
    assert update_response.status_code == 200

    # Validate update
    auth_response = authenticate_user(client, email, password)
    user_data = json.loads(auth_response.data)
    assert user_data['first_name'] == 'UpdatedName'
    assert user_data['last_name'] == 'UpdatedUser'
