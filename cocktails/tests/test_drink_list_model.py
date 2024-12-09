import pytest
from flask.testing import FlaskClient
from unittest.mock import MagicMock, patch

from cocktail_maker.models.drink_list_model import DrinkListModel
from app import create_app
from cocktail_maker.db import db

@pytest.fixture
def mock_drink_list(mocker):
    """Mock the DrinkListModel instance."""
    mock = mocker.patch.object(DrinkListModel, 'fetch_drink_by_name')
    return mock

@pytest.fixture
def client():
    app = create_app(config_class=TestConfig)  # Pass the TestingConfig
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Set up the test database
        yield client

@pytest.fixture
def mock_fetch_drinks_by_alcoholic(mocker):
    """Fixture to mock fetch_drinks_by_alcoholic API calls."""
    return mocker.patch('cocktail_maker.utils.random_utils.fetch_drinks_by_alcoholic')


def test_add_drink(client, mock_drink_list):
    """Test the add drink API."""
    mock_drink_list.return_value = MagicMock(name='Margarita', id=1, ingredients=["Rum", "Mint", "Sugar"])

    response = client.post('/api/create-drink', json={'name': 'Margarita'})

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['status'] == 'Drink added'
    assert json_data['drink']['name'] == 'Margarita'

def test_add_drink_invalid_name(client):
    """Test the error case when drink name is not provided."""
    response = client.post('/api/create-drink', json={})
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['error'] == 'Drink name is required.'

def test_add_drink_not_found(client, mock_drink_list):
    """Test the error case when the drink is not found in the external API."""
    mock_drink_list.return_value = None

    response = client.post('/api/create-drink', json={'name': 'NonExistingDrink'})
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['error'] == 'Drink not found in the external API.'




def test_remove_drink(client, mocker):
    """Test the remove drink API."""
    drink_list = DrinkListModel()
    drink_list.add_drink("Margarita")  

    mock_remove = mocker.patch.object(drink_list, 'remove_drink')
    mock_remove.return_value = "Drink removed"

    response = client.post('/api/remove-drink', json={'name': 'Margarita'})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'Drink removed'
    assert json_data['id'] == 'Margarita'

def test_remove_drink_not_found(client):
    """Test the error case when trying to remove a non-existent drink."""
    response = client.post('/api/remove-drink', json={'name': 'NonExistingDrink'})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == 'Drink not found in the list.'

def test_remove_drink_missing_name(client):
    """Test the error case when drink name is not provided."""
    response = client.post('/api/remove-drink', json={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == 'Drink name is required.'



def test_list_drinks(client, mocker):
    """Test listing drinks in alphabetical order."""
    drink_list = DrinkListModel()
    drink_list.add_drink("Margarita")
    drink_list.add_drink("Martini")

    mock_list = mocker.patch.object(drink_list, 'list_drinks_in_alphabetical_order', return_value=['Martini', 'Margarita'])

    response = client.get('/api/list-drinks')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == ['Martini', 'Margarita']

def test_list_drinks_empty(client, mocker):
    """Test the case when there are no drinks in the list."""
    mock_list = mocker.patch.object(DrinkListModel, 'list_drinks_in_alphabetical_order', return_value=[])

    response = client.get('/api/list-drinks')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data == []


def test_list_drinks_error(client, mocker):
    """Test the case when an exception is raised while listing drinks."""
    mock_list = mocker.patch.object(DrinkListModel, 'list_drinks_in_alphabetical_order', side_effect=Exception("Error"))

    response = client.get('/api/list-drinks')

    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['error'] == 'Failed to retrieve drinks'

#################################################################################################
# tests for counting alcoholic drinks
#################################################################################################
def test_count_alcoholic_drinks(mock_fetch_drinks_by_alcoholic):
    """Test counting the number of alcoholic drinks in a list."""
    # Mock API response for alcoholic drinks
    mock_fetch_drinks_by_alcoholic.return_value = [{"strDrink": "Margarita"}, {"strDrink": "Old Fashioned"}]

    drink_list = ["Margarita", "Fruit Punch", "Old Fashioned", "Cranberry Punch", "Mojito"]

    # Mock `Drink.is_drink_alcoholic`
    with patch('cocktail_maker.models.drink_model.Drink.is_drink_alcoholic') as mock_is_alcoholic:
        mock_is_alcoholic.side_effect = lambda name: name in ["Margarita", "Old Fashioned"]

        result = DrinkListModel.count_alcoholic_drinks(drink_list)
        assert result == 2


def test_count_alcoholic_drinks_with_errors(mock_fetch_drinks_by_alcoholic):
    """Test counting alcoholic drinks when some drinks are not found."""
    # Mock `Drink.is_drink_alcoholic` to raise errors for unknown drinks
    with patch('cocktail_maker.models.drink.Drink.is_drink_alcoholic') as mock_is_alcoholic:
        def mock_side_effect(name):
            if name == "Unknown Drink":
                raise ValueError("Drink not found")
            return name in ["Margarita", "Old Fashioned"]

        mock_is_alcoholic.side_effect = mock_side_effect

        drink_list = ["Margarita", "Unknown Drink", "Old Fashioned", "Cranberry Punch"]
        result = DrinkListModel.count_alcoholic_drinks(drink_list)
        assert result == 2


def test_count_alcoholic_drinks_empty_list():
    """Test counting alcoholic drinks when the drink list is empty."""
    result = DrinkListModel.count_alcoholic_drinks([])
    assert result == 0

#################################################################################################
