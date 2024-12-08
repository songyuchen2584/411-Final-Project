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
        # Log the API request
        logger.info("Fetching random drink from API: %s", api_url)

        # Send the API request with a timeout
        response = requests.get(api_url, timeout=5)

        # Check if the request was successful
        response.raise_for_status()

        # Parse the response JSON
        try:
            cocktail_data = response.json()
        except ValueError:
            raise ValueError("Invalid JSON response from API")

        # Validate the "drinks" field in the response
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
