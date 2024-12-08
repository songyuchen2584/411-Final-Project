import pytest
from cocktail_maker.models.user_model import Users

@pytest.fixture
def sample_user():
    """Provide sample user data for tests."""
    return {
        "username": "testuser",
        "password": "securepassword123"
    }


##########################################################
# Create Account
##########################################################

def test_create_account_success(client, session, sample_user):
    """Test creating an account successfully."""
    response = client.post("/create-account", json=sample_user)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["message"] == "Account created successfully"

    # Verify user is stored in the database
    user = session.query(Users).filter_by(username=sample_user["username"]).first()
    assert user is not None
    assert len(user.salt) == 32  # Salt should be 32 characters
    assert len(user.password) == 64  # Password hash should be 64 characters


def test_create_account_duplicate_user(client, session, sample_user):
    """Test creating an account with a duplicate username."""
    response1 = client.post("/create-account", json=sample_user)
    assert response1.status_code == 201

    response2 = client.post("/create-account", json=sample_user)
    assert response2.status_code == 400
    json_data = response2.get_json()
    assert json_data["error"] == f"User with username '{sample_user['username']}' already exists"

def test_create_account_rollback_on_error(client, session, sample_user):
    """Test that the database rolls back properly on account creation errors."""
    # Create a valid user
    client.post("/create-account", json=sample_user)
    
    # Try creating the same user again
    response = client.post("/create-account", json=sample_user)
    assert response.status_code == 400

    # Verify that no duplicate users exist in the database
    users = session.query(Users).filter_by(username=sample_user["username"]).all()
    assert len(users) == 1, "There should be only one user in the database after rollback"

def test_create_account_missing_fields(client):
    """Test creating an account with missing fields."""
    response = client.post("/create-account", json={"username": "incompleteuser"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "Username and password are required"


##########################################################
# Login
##########################################################

def test_login_success(client, session, sample_user):
    """Test logging in with valid credentials."""
    client.post("/create-account", json=sample_user)
    response = client.post("/login", json=sample_user)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["message"] == "Login successful"


def test_login_invalid_password(client, session, sample_user):
    """Test logging in with an incorrect password."""
    client.post("/create-account", json=sample_user)
    response = client.post("/login", json={"username": sample_user["username"], "password": "wrongpassword"})
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["error"] == "Invalid credentials"


def test_login_user_not_found(client):
    """Test logging in with a non-existent user."""
    response = client.post("/login", json={"username": "nonexistentuser", "password": "password"})
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data["error"] == "User nonexistentuser not found"


##########################################################
# Update Password
##########################################################

def test_update_password_success(client, session, sample_user):
    """Test updating the password for an existing user."""
    client.post("/create-account", json=sample_user)
    old_user = session.query(Users).filter_by(username=sample_user["username"]).first()

    new_password = "newsecurepassword123"
    response = client.post("/update-password", json={"username": sample_user["username"], "new_password": new_password})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["message"] == "Password updated successfully"

    # Verify the new password works
    assert Users.check_password(sample_user["username"], new_password) is True

    # Ensure the old password no longer works
    assert Users.check_password(sample_user["username"], sample_user["password"]) is False

    # Verify the salt is updated
    updated_user = session.query(Users).filter_by(username=sample_user["username"]).first()
    assert updated_user.salt != old_user.salt, "Salt should change after password update"
    assert updated_user.password != old_user.password, "Password hash should change after password update"


def test_update_password_user_not_found(client):
    """Test updating the password for a non-existent user."""
    response = client.post("/update-password", json={"username": "nonexistentuser", "new_password": "newpassword"})
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data["error"] == "User nonexistentuser not found"


def test_update_password_missing_fields(client):
    """Test updating the password with missing fields."""
    response = client.post("/update-password", json={"username": "incompleteuser"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "Username and new password are required"
