import requests
from cocktail_maker.models.drink_model import Drink
from typing import Optional, List

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
    