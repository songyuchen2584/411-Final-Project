from dataclasses import asdict, dataclass
import logging
import requests
from typing import Any, List

from sqlalchemy import event
from sqlalchemy.exc import IntegrityError

from cocktail_maker.clients.redis_client import redis_client
from cocktail_maker.db import db
from cocktail_maker.utils.logger import configure_logger
from cocktail_maker.utils.random_utils import get_random

logger = logging.getLogger(__name__)
configure_logger(logger)

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
    
    def get_random_drink() -> Drink:
        """
        Fetch a random cocktail from the API and return it as a Drink object.
    
        Returns:
            Drink: A Drink object containing the cocktail details.
    
        Raises:
            Exception: If the API call fails or the response is invalid.
        """

        try:
            # Fetch random drink data using the fetch_random_drink_data function
            cocktail_data = fetch_random_drink_data()
    
            # Parse the drink information from the API response
            drink_data = cocktail_data["drinks"][0]  # The API always returns a list with one drink
    
            # Extract ingredients and measures
            ingredients = [
                drink_data[f"strIngredient{i}"]
                for i in range(1, 16) if drink_data[f"strIngredient{i}"]
            ]
            measures = [
                drink_data[f"strMeasure{i}"]
                for i in range(1, 16) if drink_data[f"strMeasure{i}"]
            ]
    
            # Ensure ingredients and measures are of the same length
            if len(ingredients) != len(measures):
                logger.warning("Mismatch between ingredients and measures. Filling missing values with None.")
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
            return drink
    
        except RuntimeError as e:
            logger.error("Error fetching or processing random drink: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error in get_random_drink: %s", e)
            raise RuntimeError(f"Unexpected error in get_random_drink: {e}")

    def update_cache_for_cocktail(mapper, connection, target):
        """
        Update the Redis cache for a cocktail entry after an update or delete operation.

        This function is intended to be used as an SQLAlchemy event listener for the
        `after_update` and `after_delete` events on the Cocktails model. When a cocktail is
        updated or deleted, this function will either update the corresponding Redis
        cache entry with the new cocktail details or remove the entry if the cocktail has
        been marked as deleted.
    
        Args:
            mapper (Mapper): The SQLAlchemy Mapper object (auto-passed by SQLAlchemy).
            connection (Connection): The SQLAlchemy Connection object used for the operation.
            target (Cocktails): The instance of the Cocktails model that was updated or deleted.
    
        Side-effects:
            - Removes the cache entry if the cocktail is marked as deleted.
            - Updates the cache entry with the current data if the cocktail is not deleted.
        """
        cache_key = f"cocktail:{target.id}"
        if target.deleted:
            # If marked as deleted, remove the cache entry
            redis_client.delete(cache_key)
        else:
            # If not deleted, update the cache entry with the latest data
            redis_client.hset(
                cache_key,
                mapping={k.encode(): str(v).encode() for k, v in asdict(target).items()}
            )

    # Register the listener for update and delete events
    event.listen(Drink, 'after_update', update_cache_for_cocktail)
    event.listen(Drink, 'after_delete', update_cache_for_cocktail)
