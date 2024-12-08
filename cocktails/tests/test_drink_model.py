from dataclasses import asdict
import requests
from contextlib import contextmanager
from unittest.mock import patch
import re
import sqlite3

import pytest
from unittest.mock import MagicMock

from cocktail_maker.models.drink_model import (
    Drink,
    in_memory_data
)

@pytest.fixture
def mock_fetch_drinks_by_alcoholic(mocker):
    """Fixture to mock fetch_drinks_by_alcoholic API calls."""
    return mocker.patch("cocktail_maker.models.drink_model.fetch_drinks_by_alcoholic")

@pytest.fixture
def mock_fetch_random_drink_data(mocker):
    """
    Mock the fetch_random_drink_data function.
    """
    mock = mocker.patch("cocktail_maker.models.drink_model.fetch_random_drink_data")
    return mock

@pytest.fixture
def mock_requests_get(mocker):
    """
    Mock the requests.get function.
    """
    mock = mocker.patch("requests.get")
    return mock

@pytest.fixture(autouse=True)
def clear_in_memory_data():
    """Ensure in_memory_data is cleared before each test."""
    in_memory_data.clear()

################# Get Drinks #################

from unittest.mock import patch

@patch("cocktail_maker.models.drink_model.fetch_random_drink_data")
def test_get_random_drink_success(mock_fetch_random_drink_data):
    """Test get_random_drink with a successful API call."""
    # Mock API response
    mocked_drink = {
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
        "strIngredient6": None,
        "strIngredient7": None,
        "strIngredient8": None,
        "strIngredient9": None,
        "strIngredient10": None,
        "strIngredient11": None,
        "strIngredient12": None,
        "strIngredient13": None,
        "strIngredient14": None,
        "strIngredient15": None,
        "strMeasure1": "1 1/2 oz",
        "strMeasure2": "1/2 oz",
        "strMeasure3": "1 oz",
        "strMeasure4": None,
        "strMeasure5": None,
        "strMeasure6": None,
        "strMeasure7": None,
        "strMeasure8": None,
        "strMeasure9": None,
        "strMeasure10": None,
        "strMeasure11": None,
        "strMeasure12": None,
        "strMeasure13": None,
        "strMeasure14": None,
        "strMeasure15": None,
        "strDrinkThumb": "https://www.example.com/margarita.jpg",
    }
    mock_fetch_random_drink_data.return_value = {"drinks": [mocked_drink]}

    # Call the method
    drink_data = Drink.get_random_drink()

    # Expected ingredients and measures
    expected_ingredients = [mocked_drink.get(f"strIngredient{i}") for i in range(1, 16)]
    expected_measures = [mocked_drink.get(f"strMeasure{i}") for i in range(1, 16)]

    # Assert the length matches the 15 slots
    assert len(drink_data["ingredients"]) == 15
    assert len(drink_data["measures"]) == 15

    # Assert the drink data matches expected values
    assert drink_data["name"] == mocked_drink["strDrink"]
    assert drink_data["ingredients"] == expected_ingredients
    assert drink_data["measures"] == expected_measures

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

    # Print the call arguments of requests.get
    print(mock_requests_get.call_args)

    # Call the method
    drink_data = Drink.get_drink_by_name("Margarita")

    # Assert the data is processed correctly
    assert drink_data["name"] == "Margarita"
    assert drink_data["ingredients"] == [
        "Tequila",
        "Triple sec",
        "Lime juice",
        "Salt",
        None, None, None, None, None, None,
        None, None, None, None, None,
    ]
    assert drink_data["measures"] == [
        "1 1/2 oz",
        "1/2 oz",
        "1 oz",
        None, None, None, None, None, None,
        None, None, None, None, None, None,
    ]
    assert drink_data["thumbnail"] == "https://www.thecocktaildb.com/images/media/drink/5noda61589575158.jpg"

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


#####################################################################################
# tests for checking alcoholic
##########################################################################################################

def test_is_drink_alcoholic_true(mock_fetch_drinks_by_alcoholic):
    """Test that a drink is correctly identified as alcoholic."""
    # Mock API response for alcoholic drinks
    mock_fetch_drinks_by_alcoholic.side_effect = lambda alcoholic: [
        {"strDrink": "Margarita"}, {"strDrink": "Old Fashioned"}
    ] if alcoholic else []

    result = Drink.is_drink_alcoholic("Margarita")
    assert result is True


def test_is_drink_alcoholic_false(mock_fetch_drinks_by_alcoholic):
    """Test that a drink is correctly identified as non-alcoholic."""
    # Mock API response for non-alcoholic drinks
    mock_fetch_drinks_by_alcoholic.side_effect = lambda alcoholic: [
        {"strDrink": "Fruit Punch"}, {"strDrink": "Cranberry Punch"}
    ] if not alcoholic else []

    result = Drink.is_drink_alcoholic("Fruit Punch")
    assert result is False


def test_is_drink_alcoholic_not_found(mock_fetch_drinks_by_alcoholic):
    """Test the case when a drink is not found."""
    # Mock API response: no drinks
    mock_fetch_drinks_by_alcoholic.return_value = []

    with pytest.raises(ValueError, match="not found"):
        Drink.is_drink_alcoholic("Unknown Drink")
