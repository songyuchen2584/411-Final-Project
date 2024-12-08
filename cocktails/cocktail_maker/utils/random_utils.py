import logging
import requests

from cocktail_maker.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

def fetch_random_drink_data() -> dict:
    """
    Fetch a random cocktail from the CocktailDB API.

    Returns:
        dict: The API response as a dictionary.

    Raises:
        RuntimeError: If the request to the API fails or times out.
        ValueError: If the API response is invalid or does not contain drink data.
    """
    api_url = "https://www.thecocktaildb.com/api/json/v1/1/random.php"

    try:
        logger.info("Fetching random drink from API: %s", api_url)
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        cocktail_data = response.json()

        drinks = cocktail_data.get("drinks")
        if not drinks or not isinstance(drinks, list):
            raise ValueError("Invalid or empty 'drinks' field in API response")

        logger.info("Random drink data successfully fetched from API")
        return cocktail_data

    except requests.exceptions.Timeout:
        logger.error("Request to CocktailDB API timed out.")
        raise RuntimeError("Request to CocktailDB API timed out.")

    except requests.exceptions.RequestException as e:
        logger.error("Request to CocktailDB API failed: %s", e)
        raise RuntimeError(f"Request to CocktailDB API failed: {e}")

    except Exception as e:
        logger.error("Unexpected error while fetching random drink: %s", e)
        raise RuntimeError(f"Unexpected error while fetching random drink: {e}")

def fetch_drinks_by_alcoholic(alcoholic: bool) -> dict:
    """
    Fetch drinks filtered by their alcoholic content from the CocktailDB API.

    Args:
        alcoholic (bool): If True, fetch 'Alcoholic' drinks; if False, fetch 'Non_Alcoholic' drinks.

    Returns:
        List[dict]: A list of drinks with minimal details (idDrink, strDrink, strDrinkThumb).

    Raises:
        RuntimeError: If the API call fails or an invalid response is received.
    """
    # Determine the correct endpoint based on the input
    filter_type = "Alcoholic" if alcoholic else "Non_Alcoholic"
    api_url = f"https://www.thecocktaildb.com/api/json/v1/1/filter.php?a={filter_type}"

    try:
        # Log the API request
        logger.info("Fetching '%s' drinks from API: %s", filter_type, api_url)

        # Perform the API call
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()  # Raise an error for HTTP failures

        # Parse the JSON response
        data = response.json()
        drinks = data.get("drinks", [])

        if not drinks:
            logger.warning("No '%s' drinks found.", filter_type)
            return []

        logger.info("Successfully fetched %d '%s' drinks.", len(drinks), filter_type)
        return drinks  # List of drink dictionaries

    except requests.exceptions.RequestException as e:
        logger.error("API request failed for '%s' drinks: %s", filter_type, e)
        raise RuntimeError(f"Failed to fetch '{filter_type}' drinks: {e}")
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise RuntimeError(f"An unexpected error occurred: {e}")