import random


class Dice:
    def __init__(self, sides: int):
        self.sides = sides

    def roll(self):
        return random.randint(1, self.sides)

    def __mul__(self, other:int):
        rolls = []
        for _ in range(other):
          rolls.append(self.roll())
        suma = sum(rolls)
        print(f"Rolled {other} dice and got {rolls} and a sum of {suma}")
        return suma



D6 = Dice(6)
D20 = Dice(20)
