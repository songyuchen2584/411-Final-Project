import pytest
from cocktail_maker.models.user_model import Users
from cocktail_maker.db import db
from app import create_app
from config import TestConfig
from flask.testing import FlaskClient

@pytest.fixture
def app():
    """Create a test app using TestConfig."""
    app = create_app(config_class=TestConfig)  # Pass TestConfig
    with app.app_context():
        db.create_all()  # Create tables in in-memory database
        yield app
        db.session.remove()
        db.drop_all()  # Drop all tables after tests

@pytest.fixture
def sample_user():
    return {
        "username": "testuser",
        "password": "securepassword123"
    }

@pytest.fixture
def client(app) -> FlaskClient:
    """Provide a test client for the Flask app."""
    return app.test_client()


##########################################################
# Create Account
##########################################################

def test_create_account_success(client: FlaskClient, sample_user):
    """Test creating an account successfully."""
    response = client.post("/create-account", json=sample_user)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["message"] == "Account created successfully"

    # Verify user is stored in the database
    with client.application.app_context():
        user = Users.query.filter_by(username=sample_user["username"]).first()
        assert user is not None
        assert len(user.salt) == 32  # Salt should be 32 characters (hex)
        assert len(user.password) == 64  # Password should be 64-character SHA-256 hash

def test_create_account_duplicate_user(client: FlaskClient, sample_user):
    """Test creating an account with a duplicate username."""
    # Create the user first
    response1 = client.post("/create-account", json=sample_user)
    assert response1.status_code == 201

    # Attempt to create the user again
    response2 = client.post("/create-account", json=sample_user)
    assert response2.status_code == 400
    json_data = response2.get_json()
    assert json_data["error"] == f"User with username '{sample_user['username']}' already exists"

def test_create_account_missing_fields(client: FlaskClient):
    """Test creating an account with missing fields."""
    response = client.post("/create-account", json={"username": "incompleteuser"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "Username and password are required"

##########################################################
# Login
##########################################################

def test_login_success(client: FlaskClient, sample_user):
    """Test logging in with valid credentials."""
    # Create the user first
    client.post("/create-account", json=sample_user)

    # Attempt to log in
    response = client.post("/login", json=sample_user)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["message"] == "Login successful"

def test_login_invalid_password(client: FlaskClient, sample_user):
    """Test logging in with an incorrect password."""
    # Create the user first
    client.post("/create-account", json=sample_user)

    # Attempt to log in with an incorrect password
    response = client.post("/login", json={"username": sample_user["username"], "password": "wrongpassword"})
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["error"] == "Invalid credentials"

def test_login_user_not_found(client: FlaskClient):
    """Test logging in with a non-existent user."""
    response = client.post("/login", json={"username": "nonexistentuser", "password": "password"})
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data["error"] == "User nonexistentuser not found"

##########################################################
# Update Password
##########################################################

def test_update_password_success(client: FlaskClient, sample_user):
    """Test updating the password for an existing user."""
    # Create the user first
    client.post("/create-account", json=sample_user)

    # Update the password
    new_password = "newsecurepassword123"
    response = client.post("/update-password", json={"username": sample_user["username"], "new_password": new_password})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["message"] == "Password updated successfully"

    # Verify the password has been updated
    with client.application.app_context():
        assert Users.check_password(sample_user["username"], new_password) is True

def test_update_password_user_not_found(client: FlaskClient):
    """Test updating the password for a non-existent user."""
    response = client.post("/update-password", json={"username": "nonexistentuser", "new_password": "newpassword"})
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data["error"] == "User nonexistentuser not found"

def test_update_password_missing_fields(client: FlaskClient):
    """Test updating the password with missing fields."""
    response = client.post("/update-password", json={"username": "incompleteuser"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "Username and new password are required"
