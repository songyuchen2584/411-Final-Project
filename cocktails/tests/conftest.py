import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app import create_app
from cocktail_maker.db import db
from config import TestConfig

@pytest.fixture
def app():
    """Create a Flask app configured for testing."""
    app = create_app(config_class=TestConfig)
    with app.app_context():
        db.create_all()  # Create tables in in-memory database
        yield app
        db.session.remove()
        db.drop_all()  # Cleanup database after tests

@pytest.fixture
def client(app):
    """Provide a test client for the Flask app."""
    return app.test_client()

@pytest.fixture
def session(app):
    """Provide a database session for tests."""
    with app.app_context():
        yield db.session
