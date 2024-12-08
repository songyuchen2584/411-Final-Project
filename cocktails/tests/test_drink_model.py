from dataclasses import asdict
from contextlib import contextmanager
from unittest.mock import patch
import re
import sqlite3

import pytest
from unittest.mock import MagicMock

from cocktail_maker.models.drink_model import (
    Drink,
    #######ADD FUNCTIONS##########
    in_memory_data,
    get_random_drink,
    get_drink_by_name,
)

@pytest.fixture
def mock_fetch_random_drink_data(mocker):
    """
    Mock the fetch_random_drink_data function.
    """
    mock = mocker.patch("cocktail_maker.utils.random_utils.fetch_random_drink_data")
    return mock

@pytest.fixture
def mock_requests_get(mocker):
    """
    Mock the requests.get function.
    """
    mock = mocker.patch("requests.get")
    return mock

def test_get_random_drink_success(mock_fetch_random_drink_data):
    """Test get_random_drink with a successful API call."""
    # Mock API response
    mock_fetch_random_drink_data.return_value = {
        "drinks": [
            {
                "idDrink": "11007",
                "strDrink": "Margarita",
                "strCategory": "Ordinary Drink",
                "strAlcoholic": "Alcoholic",
                "strGlass": "Cocktail glass",
                "strInstructions": "Rub the rim of the glass...",
                "strIngredient1": "Tequila",
                "strIngredient2": "Triple sec",
                "strIngredient3": "Lime juice",
                "strIngredient4": "Salt",
                "strIngredient5": None,
                "strMeasure1": "1 1/2 oz",
                "strMeasure2": "1/2 oz",
                "strMeasure3": "1 oz",
                "strMeasure4": None,
                "strMeasure5": None,
                "strDrinkThumb": "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg",
            }
        ]
    }

    # Call the method
    drink_data = Drink.get_random_drink()

    # Assert the data is processed correctly
    assert drink_data["name"] == "Margarita"
    assert drink_data["ingredients"] == ["Tequila", "Triple sec", "Lime juice", "Salt"]
    assert drink_data["measures"] == ["1 1/2 oz", "1/2 oz", "1 oz", None]
    assert drink_data["thumbnail"] == "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg"

    # Assert the drink is stored in memory
    assert "Margarita" in in_memory_data
    assert in_memory_data["Margarita"]["name"] == "Margarita"

def test_get_random_drink_api_failure(mock_fetch_random_drink_data):
    """Test get_random_drink when the API call fails."""
    # Simulate API failure
    mock_fetch_random_drink_data.side_effect = RuntimeError("API error")

    # Call the method and assert an exception is raised
    with pytest.raises(RuntimeError, match="Error fetching random drink: API error"):
        Drink.get_random_drink()

def test_get_drink_by_name_success(mock_requests_get):
    """Test get_drink_by_name with a successful API call."""
    # Mock API response
    mock_requests_get.return_value.json.return_value = {
        "drinks": [
            {
                "idDrink": "11007",
                "strDrink": "Margarita",
                "strCategory": "Ordinary Drink",
                "strAlcoholic": "Alcoholic",
                "strGlass": "Cocktail glass",
                "strInstructions": "Rub the rim of the glass...",
                "strIngredient1": "Tequila",
                "strIngredient2": "Triple sec",
                "strIngredient3": "Lime juice",
                "strIngredient4": "Salt",
                "strIngredient5": None,
                "strMeasure1": "1 1/2 oz",
                "strMeasure2": "1/2 oz",
                "strMeasure3": "1 oz",
                "strMeasure4": None,
                "strMeasure5": None,
                "strDrinkThumb": "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg",
            }
        ]
    }

    # Call the method
    drink_data = Drink.get_drink_by_name("Margarita")

    # Assert the data is processed correctly
    assert drink_data["name"] == "Margarita"
    assert drink_data["ingredients"] == ["Tequila", "Triple sec", "Lime juice", "Salt"]
    assert drink_data["measures"] == ["1 oz", "0.5 oz", "1 oz", None]
    assert drink_data["thumbnail"] == "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg"

    # Assert the drink is stored in memory
    assert "Margarita" in in_memory_data
    assert in_memory_data["Margarita"]["name"] == "Margarita"


def test_get_drink_by_name_not_found(mock_requests_get):
    """Test get_drink_by_name when the drink is not found."""
    # Mock API response for not found
    mock_requests_get.return_value.json.return_value = {"drinks": None}

    # Call the method and assert an exception is raised
    with pytest.raises(ValueError, match="Drink with name 'NonexistentDrink' not found"):
        Drink.get_drink_by_name("NonexistentDrink")


def test_get_drink_by_name_api_failure(mock_requests_get):
    """Test get_drink_by_name when the API call fails."""
    # Simulate API failure
    mock_requests_get.side_effect = requests.RequestException("API error")

    # Call the method and assert an exception is raised
    with pytest.raises(RuntimeError, match="Failed to fetch drink by name 'Margarita'"):
        Drink.get_drink_by_name("Margarita")  


#######################################################################################################

def test_get_meal_by_name_cache_hit(session, mock_redis_client):
    """Test retrieving a meal by its name when the name-to-ID association is cached."""
    # Create the meal and cache the name-to-ID association
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    mock_redis_client.get.return_value = str(meal.id).encode()  # Simulate name-to-ID cache hit
    mock_redis_client.hgetall.return_value = {k.encode(): str(v).encode() for k, v in asdict(meal).items()}

    # Retrieve meal by name, expecting a cache hit for both ID and meal data
    result = Meals.get_meal_by_name("Spaghetti")
    mock_redis_client.get.assert_called_once_with("meal_name:Spaghetti")
    mock_redis_client.hgetall.assert_called_once_with(f"meal_{meal.id}")
    assert result["meal"] == "Spaghetti"

def test_get_meal_by_name_cache_miss(session, mock_redis_client):
    """Test retrieving a meal by its name when the name-to-ID association is not cached."""
    # Create the meal but simulate a cache miss for name-to-ID association
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    mock_redis_client.get.return_value = None  # Simulate cache miss for name-to-ID
    mock_redis_client.hgetall.return_value = {}  # Simulate cache miss for meal data

    # Retrieve meal by name; expect DB lookup and caching of both ID and meal data
    result = Meals.get_meal_by_name("Spaghetti")
    mock_redis_client.get.assert_called_once_with("meal_name:Spaghetti")
    mock_redis_client.set.assert_called_once_with("meal_name:Spaghetti", str(meal.id))
    mock_redis_client.hset.assert_called_once_with(f"meal_{meal.id}", mapping={k: str(v) for k, v in asdict(meal).items()})
    assert result["meal"] == "Spaghetti"

def test_get_meal_by_name_deleted(session, mock_redis_client):
    """Test retrieving a deleted meal by its name."""
    # Create and delete the meal
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.delete_meal(meal.id)

    # Cache reflects that the meal is deleted
    mock_redis_client.get.return_value = str(meal.id).encode()
    mock_redis_client.hgetall.return_value = {
        "id".encode(): "1".encode(),
        "meal".encode(): "Spaghetti".encode(),
        "cuisine".encode(): "Italian".encode(),
        "price".encode(): "12.5".encode(),
        "difficulty".encode(): "MED".encode(),
        "battles".encode(): "0".encode(),
        "wins".encode(): "0".encode(),
        "deleted".encode(): "True".encode()
    }

    # Attempt retrieval, expecting a ValueError
    with pytest.raises(ValueError, match="Meal Spaghetti not found"):
        Meals.get_meal_by_name("Spaghetti")

def test_get_meal_by_name_bad_name(session, mock_redis_client):
    """Test retrieving a meal by a name that does not exist in cache or database."""
    # Simulate a cache miss for a non-existent meal name
    mock_redis_client.get.return_value = None

    # Attempt retrieval, expecting a ValueError
    with pytest.raises(ValueError, match="Meal Motor oil not found"):
        Meals.get_meal_by_name("Motor oil")
    mock_redis_client.get.assert_called_once_with("meal_name:Motor oil")

def test_update_meal(session, mock_redis_client):
    """Test updating a meal's details."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.update_meal(meal.id, cuisine="Italian", price=15.0, difficulty="HIGH")
    updated_meal = Meals.query.one()
    assert updated_meal.cuisine == "Italian"
    assert updated_meal.price == 15.0
    assert updated_meal.difficulty == "HIGH"

def test_update_meal_triggers_cache_update(session, mock_redis_client):
    """Test that updating a meal triggers a cache update in Redis."""
    # Create and add a meal
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = session.get(Meals, 1)

    # Update the meal
    Meals.update_meal(meal.id, cuisine="Mexican", price=15.0)

    # Check that the Redis cache was updated with the new values
    mock_redis_client.hset.assert_called_once_with(
        f"meal:{meal.id}",
        mapping={
            b"id": b"1",
            b"meal": b"Spaghetti",
            b"cuisine": b"Mexican",
            b"price": b"15.0",
            b"difficulty": b"MED",
            b"battles": b"0",
            b"wins": b"0",
            b"deleted": b"False",
        }
    )

def test_update_meal_deleted(session, mock_redis_client):
    """Test updating a deleted meal."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.delete_meal(meal.id)
    with pytest.raises(ValueError, match="Meal 1 not found"):
        Meals.update_meal(meal.id, cuisine="Italian", price=15.0, difficulty="HIGH")

def test_update_meal_update_name(session):
    """Test updating a meal's name."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    with pytest.raises(ValueError, match="Cannot update meal name"):
        Meals.update_meal(meal.id, meal="Lasagna", cuisine="Italian", price=15.0, difficulty="HIGH")

def test_update_meal_bad_id(session):
    """Test updating a meal with an invalid ID."""
    with pytest.raises(ValueError, match="Meal 999 not found"):
        Meals.update_meal(999, cuisine="Italian", price=15.0, difficulty="HIGH")

def test_update_meal_bad_difficulty(session):
    """Test updating a meal with an invalid difficulty level."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    with pytest.raises(ValueError, match="Invalid difficulty level: VERY_HARD. Must be 'LOW', 'MED', or 'HIGH'."):
        Meals.update_meal(meal.id, cuisine="Italian", price=15.0, difficulty="VERY_HARD")

def test_update_meal_bad_price(session):
    """Test updating a meal with an invalid price (negative or zero)."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    with pytest.raises(ValueError, match="Invalid price: -15.0. Price must be a positive number."):
        Meals.update_meal(meal.id, cuisine="Italian", price=-15.0, difficulty="HIGH")

    session.rollback()

    with pytest.raises(ValueError, match="Invalid price: 0. Price must be a positive number."):
        Meals.update_meal(meal.id, cuisine="Italian", price=0, difficulty="HIGH")

def test_update_meal_stats_win(session, mock_redis_client):
    """Test updating the meal stats for a win."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.update_meal_stats(meal.id, 'win')
    updated_meal = Meals.query.one()
    assert updated_meal.wins == 1
    assert updated_meal.battles == 1

def test_update_meal_stats_loss(session, mock_redis_client):
    """Test updating the meal stats for a loss."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.update_meal_stats(meal.id, 'loss')
    updated_meal = Meals.query.one()
    assert updated_meal.wins == 0
    assert updated_meal.battles == 1

def test_get_leaderboard(session):
    """Test retrieving the leaderboard sorted by wins."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED", battles=10, wins=7)
    Meals.create_meal("Pizza", "Italian", 15.0, "LOW", battles=8, wins=5)

    leaderboard = Meals.get_leaderboard()
    assert leaderboard[0]["meal"] == "Spaghetti"
    assert leaderboard[1]["meal"] == "Pizza"

def test_get_leaderboard_sort_pct(session):
    """Test retrieving the leaderboard sorted by win percentage."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED", battles=10, wins=7)
    Meals.create_meal("Pizza", "Italian", 15.0, "LOW", battles=8, wins=5)

    leaderboard = Meals.get_leaderboard(sort_by="win_pct")
    assert leaderboard[0]["meal"] == "Spaghetti"
    assert leaderboard[1]["meal"] == "Pizza"

def test_get_leaderboard_bad_sort():
    """Test retrieving the leaderboard with an invalid sort option."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_sort"):
        Meals.get_leaderboard(sort_by="invalid_sort")
