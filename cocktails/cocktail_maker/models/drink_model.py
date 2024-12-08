from dataclasses import dataclass
from typing import List

@dataclass
class Drink:
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