from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Item(ABC):
    name: str
    price: float
    description: str

    @abstractmethod
    def use(self, character):
        raise NotImplementedError


@dataclass
class SizePotion(Item):
    size_change_ratio: float

    def use(self, character):
        character.sizeRatio *= self.size_change_ratio


class Inventory:
    def __init__(self):
        self.items = []

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def __contains__(self, item):
        return item in self.items

    def __add__(self, item: Item):
        self.items.append(item)

    def __str__(self):
        return str(self.items)

    def __repr__(self):
        return str(self.items)


doublePotion = SizePotion("A size potion", 2, "A size potion that doubles your size", 2)
quaterPotion = SizePotion("A size potion", 2, "A size potion that doubles your size", 1 / 4)
