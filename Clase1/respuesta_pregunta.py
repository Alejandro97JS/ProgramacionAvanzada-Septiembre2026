class Character:
    def __init__(self, hitpoints, num_lives, damage_per_attack):
            self.hitpoints = hitpoints
            self.num_lives = num_lives
            self.damage_per_attack = damage_per_attack

class Wizard(Character):
    def __init__(self, hitpoints, num_lives, damage_per_attack, mana):
        # Llamo al constructor, y además tengo un atributo extra:
        super().__init__(hitpoints, num_lives, damage_per_attack)
        self.mana = mana

class Warrior(Character):
       pass # Aunque herede, para el ejemplo lo dejo igual que el Character.
        

def main():
    wizard1 = Wizard(
        hitpoints=100,
        num_lives=3,
        damage_per_attack=20,
        mana=100
    )
    warrior1 = Warrior(
        hitpoints=50,
        num_lives=1,
        damage_per_attack=10
    )
    generic_character = Character(
        hitpoints=20,
        num_lives=1,
        damage_per_attack=2
    )
    my_characters_list = [
        wizard1,
        warrior1,
        generic_character
    ]
    # Para referirme al mago, puedo seguir usando my_character_list[0]
    # o puedo seguir usando wizard1.

if __name__ == 'main':
    main()
