from dataclasses import asdict, dataclass
import logging
import requests
from typing import Any, List


from cocktail_maker.db import db
from cocktail_maker.utils.logger import configure_logger
from cocktail_maker.utils.random_utils import fetch_random_drink_data

logger = logging.getLogger(__name__)
configure_logger(logger)

# In-memory storage for drinks
in_memory_data = {}

@dataclass
class Drink():
    __tablename__ = 'cocktails'
    
    id: int
    name: str
    category: str
    alcoholic: str
    glass: str
    instructions: str
    ingredients: List[str]
    measures: List[str]
    thumbnail: str

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "alcoholic": self.alcoholic,
            "glass": self.glass,
            "instructions": self.instructions,
            "ingredients": self.ingredients,
            "measures": self.measures,
            "thumbnail": self.thumbnail
        }

    VALID_CATEGORIES = [
        "Cocktail",
        "Ordinary Drink",
        "Punch / Party Drink",
        "Shake",
        "Other / Unknown",
        "Cocoa",
        "Shot",
        "Coffee / Tea",
        "Homemade Liqueur",
        "Beer",
        "Soft Drink",
    ]

    def __post_init__(self):
        if self.category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{self.category}'. Must be one of {', '.join(self.VALID_CATEGORIES)}."
            )

    def get_random_drink() -> dict:
        """
        Fetch a random cocktail from the API and return it as a Drink object.
    
        Returns:
            Drink: A Drink dictionary representation containing the cocktail details.
    
        Raises:
            Exception: If the API call fails or the response is invalid.
        """
        try:
            # Fetch data from the API
            cocktail_data = fetch_random_drink_data() # API call for getting random drink is made in the fetch_random_drink_data() in random_utils
            logger.debug("API response received: %s", cocktail_data)
    
            # Parse the drink data from the API response
            drink_data = cocktail_data["drinks"][0]
            logger.info("Successfully fetched drink data: %s", drink_data.get("strDrink"))
    
            # Extract ingredients and measures
            ingredients = [
                drink_data[f"strIngredient{i}"]
                for i in range(1, 16) if drink_data[f"strIngredient{i}"]
            ]
            measures = [
                drink_data[f"strMeasure{i}"]
                for i in range(1, 16) if drink_data[f"strMeasure{i}"]
            ]
    
            # Log mismatches in ingredients and measures if any
            if len(ingredients) != len(measures):
                logger.warning(
                    "Mismatch between ingredients and measures. Ingredients: %d, Measures: %d. "
                    "Filling missing values with None.",
                    len(ingredients),
                    len(measures),
                )
    
                # Align the lengths of ingredients and measures
                if len(ingredients) > len(measures):
                    measures.extend([None] * (len(ingredients) - len(measures)))
                elif len(measures) > len(ingredients):
                    ingredients.extend([None] * (len(measures) - len(ingredients)))
    
            # Create a Drink object
            drink = Drink(
                id=int(drink_data["idDrink"]),
                name=drink_data["strDrink"],
                category=drink_data["strCategory"],
                alcoholic=drink_data["strAlcoholic"],
                glass=drink_data["strGlass"],
                instructions=drink_data["strInstructions"],
                ingredients=ingredients,
                measures=measures,
                thumbnail=drink_data["strDrinkThumb"],
            )
            logger.info("Successfully created Drink object: %s", drink.name)
    
            # Store the drink in memory
            in_memory_data[drink.name] = drink.to_dict()
            logger.info("Stored drink '%s' in memory.", drink.name)

            # Returns a dictionary representation of the Drink
            return drink.to_dict()
    
        except Exception as e:
            logger.error("Error fetching random drink: %s", e)
            raise RuntimeError(f"Error fetching random drink: {e}")

    
    def get_drink_by_name(name: str) -> dict:
        """
        Fetches drinks by name from the CocktailDB API and returns a dictionary representation of a Drink.
    
        Args:
            name (str): The name of the drink to search for.
    
        Returns:
            Retrieve a drink by name. If the drink is not already stored in memory, fetch it from the API,
            store it in memory, and return its details.

        Args:
            name (str): The name of the drink to retrieve.
    
        Returns:
            dict: A dictionary containing the details of the drink
        
        Raises:
            ValueError: If no drinks are found for the given name or if the name input is invalid.
            RuntimeError: If the API request fails or returns an invalid response.
        """
        # Check if the drink exists in memory
        if name in in_memory_data:
            return in_memory_data[name]
    
        try:
            # Fetch from the API
            api_url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}"
            response = requests.get(api_url)
            response.raise_for_status()
            cocktail_data = response.json()
    
            drinks = cocktail_data.get("drinks")
            if not drinks:
                raise ValueError(f"Drink with name '{name}' not found")
    
            drink_data = drinks[0]  # Assume the first drink matches
    
            # Extract ingredients and measures
            ingredients = [
                drink_data[f"strIngredient{i}"]
                for i in range(1, 16) if drink_data[f"strIngredient{i}"]
            ]
            measures = [
                drink_data[f"strMeasure{i}"]
                for i in range(1, 16) if drink_data[f"strMeasure{i}"]
            ]
    
            # Create a Drink object
            drink = Drink(
                id=int(drink_data["idDrink"]),
                name=drink_data["strDrink"],
                category=drink_data["strCategory"],
                alcoholic=drink_data["strAlcoholic"],
                glass=drink_data["strGlass"],
                instructions=drink_data["strInstructions"],
                ingredients=ingredients,
                measures=measures,
                thumbnail=drink_data["strDrinkThumb"],
            )
    
            # Store the drink in memory
            in_memory_data[drink.name] = drink.to_dict()
            # Returns a dictionary representation of the Drink
            return drink.to_dict()
    
        except requests.RequestException as e:
            logger.error("Failed to fetch drink by name '%s': %s", name, e)
            raise RuntimeError(f"Failed to fetch drink by name '{name}': {e}")
    
        except ValueError as e:
            logger.warning("Drink not found: %s", e)
            raise
    
        except Exception as e:
            logger.error("Unexpected error fetching drink by name: %s", e)
            raise RuntimeError(f"Unexpected error fetching drink by name: {e}")

    def is_drink_alcoholic(drink_name: str) -> bool:
        """
        Check if a drink is alcoholic based on its name by fetching its details from the CocktailDB API.

        Args:
            drink_name (str): The name of the drink to check.

        Returns:
            bool: True if the drink is alcoholic, False if it is non-alcoholic.

        Raises:
            ValueError: If the drink is not found or invalid data is returned.
            RuntimeError: If there is an issue with the API request.
        """
        from cocktail_maker.utils.random_utils import fetch_drinks_by_alcoholic

        try:
            # Fetch alcoholic drinks and check if the drink name is in the list
            alcoholic_drinks = fetch_drinks_by_alcoholic(alcoholic=True)
            non_alcoholic_drinks = fetch_drinks_by_alcoholic(alcoholic=False)

            alcoholic_names = {drink["strDrink"].lower() for drink in alcoholic_drinks}
            non_alcoholic_names = {drink["strDrink"].lower() for drink in non_alcoholic_drinks}

            # Standardize the drink name for comparison
            drink_name_lower = drink_name.lower()

            if drink_name_lower in alcoholic_names:
                return True  # It's alcoholic
            elif drink_name_lower in non_alcoholic_names:
                return False  # It's non-alcoholic
            else:
                raise ValueError(f"Drink '{drink_name}' not found in the API data.")

        except Exception as e:
            logger.error("Error determining if drink '%s' is alcoholic: %s", drink_name, e)
            raise RuntimeError(f"Error determining if drink '{drink_name}' is alcoholic: {e}")