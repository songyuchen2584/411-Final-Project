import logging
import requests
from cocktail_maker.models.drink_model import Drink
from typing import Optional, List

from cocktail_maker.utils.logger import configure_logger
logger = logging.getLogger(__name__)
configure_logger(logger)

class DrinkListModel:
    def __init__(self):
        self.drinks = []

    def fetch_drink_by_name(self, drink_name: str) -> Optional[Drink]:
        url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={drink_name}"
        response = requests.get(url)
        data = response.json()
        if data["drinks"]:
            drink_data = data["drinks"][0]
            ingredients = [
                drink_data[f"strIngredient{i}"]
                for i in range(1, 16)
                if drink_data.get(f"strIngredient{i}")
            ]
            measures = [
                drink_data[f"strMeasure{i}"]
                for i in range(1, 16)
                if drink_data.get(f"strMeasure{i}")
            ]
            return Drink(
                id=int(drink_data["idDrink"]),
                name=drink_data["strDrink"],
                ingredients=ingredients,
                measures=measures,
                category=drink_data["strCategory"],
                alcoholic=drink_data["strAlcoholic"],
                glass=drink_data["strGlass"],
                instructions=drink_data["strInstructions"],
                thumbnail=drink_data["strDrinkThumb"],
            )
        return None
    
    def add_drink(self, drink_name: str) -> str:
        drink = self.fetch_drink_by_name(drink_name)
        if drink:
            self.drinks.append(drink)
            return f"Added {drink.name} to your list."
        return "Drink not found."
    
    def remove_drink(self, drink_name: str) -> str:
        for drink in self.drinks:
            if drink.name.lower() == drink_name.lower():
                self.drinks.remove(drink)
                return f"Removed {drink.name} from your list."
        return "Drink not found in the list."
    
    def list_drinks_in_alphabetical_order(self) -> List[str]:
        sorted_drinks = sorted(self.drinks, key=lambda x: x.name.lower())
        drink_names = []

        for drink in sorted_drinks:
            drink_names.append(drink.name)

        return drink_names
    
    def count_alcoholic_drinks(drink_names: List[str]) -> int:
        """
        Count the number of alcoholic drinks in a list of drink names.

        Args:
            drink_names (List[str]): A list of drink names to check.

        Returns:
            int: The count of alcoholic drinks.

        Raises:
            RuntimeError: If there is an error checking drink data.
        """
        try:
            # Use the Drink class's is_drink_alcoholic function for each drink
            count = 0
            for name in drink_names:
                try:
                    if Drink.is_drink_alcoholic(name):
                        count += 1
                except ValueError:
                    logger.warning("Skipping drink '%s' as it was not found.", name)
                except Exception as e:
                    logger.error("Error checking drink '%s': %s", name, e)
                    raise RuntimeError(f"Error checking drink '{name}': {e}")
            
            logger.info(
                "Counted %d alcoholic drinks in the provided list of %d drinks.",
                count, len(drink_names)
            )
            return count

        except Exception as e:
            logger.error("Error counting alcoholic drinks: %s", e)
            raise RuntimeError(f"Error counting alcoholic drinks: {e}")