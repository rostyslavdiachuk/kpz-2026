from enum import Enum, auto
from unittest import case

import dice
from Items import Inventory


class CharacterState(Enum):
    ALIVE = auto()
    DEAD = auto()


class Character:
    def __init__(self,
                 name: str,
                 strength: int,
                 agility: int,
                 vitality: int,
                 sizeRatio: int = 1,
                 inventory: Inventory = Inventory()):
        self.sizeRatio = sizeRatio
        self.vitality = vitality
        self.strength = strength
        self.agility = agility
        self._current_health = self.vitality * self.sizeRatio * 10
        self.name = name
        self.inventory = inventory

    @property
    def full_health(self):
        return self.vitality * self.sizeRatio * 10

    @property
    def base_dmg(self):
        return self.strength * self.sizeRatio * 3

    @property
    def current_health(self):
        return self._current_health

    @current_health.setter
    def current_health(self, value):
        if value > self.full_health:
            raise ValueError("Health cannot exceed full health")
        if value < 0:
            raise ValueError("Health cannot be negative")
        self._current_health = value

    def roll_initiative(self):
        print(f"{self.name} rolls initiative")
        return dice.D20 * self.agility

    def prepare_for_battle(self):
        print(f"{self.name} prepares for battle")
        for item in self.inventory:
            item.use(self)

    def __str__(self):
        return (f"{self.name} (str: {self.strength}/agi: {self.agility}/ vit: {self.vitality}) and {self.inventory=}"
                f" current health: {self.current_health}/{self.full_health} and size ratio: {self.sizeRatio} ")

    def __repr__(self):
        return str(self)

    def try_attack(self, other):
        roll = dice.D20.roll()
        print(f"{self.name} tried to attack rolls {roll}")
        match roll:
            case 20:
                print("Critical hit! X2 dmg")
                self.attack(other, 2)
            case 1:
                print("Critical miss! X1 dmg yourself")
                self.attack(self, 1)
            case _:
                print("Normal hit! X1 dmg")
                self.attack(other, 1)

    def attack(self, other, coef):
        realDmg = self.base_dmg + dice.D6.roll()
        health_after = other.current_health - realDmg
        other.current_health = max(health_after, 0)
        msg = f"{self.name} attacked {other.name} for {realDmg} damage" \
            if other.state is CharacterState.ALIVE else \
            f"{self.name} attacked {other.name} for {realDmg} damage, but {other.name} is dead"
        print(msg)

    @property
    def state(self):
        if self.current_health <= 0:
            return CharacterState.DEAD
        return CharacterState.ALIVE
