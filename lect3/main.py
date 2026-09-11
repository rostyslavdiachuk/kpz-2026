# character = ("Robin hood", 12, 1, [])
import dice
import util
from Items import doublePotion
from characters import Character, CharacterState

# robinHood = {"name" :"Robin hood",
#              "hp": 12,
#              "dmg": 1 + dice.roll(6),
#              "inventory": []}
# robinNeHood = {"name" :" Robin Nehood",
#              "hp": 9,
#              "dmg": 2 + dice.roll(6),
#              "inventory": []}

robin = Character("Robin Hood", 5, 10, 5)
robin.inventory + doublePotion
robin.inventory + doublePotion
robin.inventory + doublePotion
robin.prepare_for_battle()

neRobin = Character("Robin NeHood", 10, 10, 2)
robin.inventory + doublePotion
robin.inventory + doublePotion
robin.prepare_for_battle()

def fight(ch1: Character, ch2: Character):
    util.save_character(robin, "robin.json")
    util.save_character(
        neRobin, "neRobin.json"
    )
    # print(neRobin)
    ch1Initiative = ch1.roll_initiative()
    ch2Initiative = ch2.roll_initiative()
    while (ch1.state is CharacterState.ALIVE
           and ch2.state is CharacterState.ALIVE):
        firstAtacker, secondAtacker = (ch1, ch2) if ch1Initiative > ch2Initiative else (ch2, ch1)

        firstAtacker.try_attack(secondAtacker)
        if secondAtacker.state is CharacterState.DEAD:
            print(f"{firstAtacker.name} has won the fight!")
            return
        secondAtacker.try_attack(firstAtacker)
        if firstAtacker.state is CharacterState.DEAD:
            print(f"{secondAtacker.name} has won the fight!")
            return



if __name__ == '__main__':
    fight(robin, neRobin)

