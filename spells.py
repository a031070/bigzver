class Spell:
    def __init__(self, name, type_spell, price, grade):
        self.name = name
        self.type_spell = type_spell
        self.price = price
        self.grade = grade

    def info(self):
        print(f"{self.name}: Type={self.type_spell}, Price={self.price}, Level={self.grade}")

    def cast(self, unit1, unit2):
        unit1.mana -= self.price
        if self.type_spell == "attack":
            unit2.take_damage(self.grade)
        elif self.type_spell == "defense":
            unit1.defense_up(self.grade)
        elif self.type_spell == "heal":
            unit1.dev_heal(self.grade)

spells = {
    "attack": {
        "1": Spell("Avada Kedavra", "attack", 25, 25),
        "2": Spell("Furore Ignis", "attack", 15, 10),
        "3": Spell("Импетус", "attack", 6, 3)
    },
    "defense": {
        "1": Spell("Amplexus", "defense", 10, 10),
        "2": Spell("Spirit", "defense", 5, 5)
    },
    "heal": {
        "1": Spell("Reformatio Status", "heal", 20, 12),
        "2": Spell("Spiritum", "heal", 10, 5),
        "3": Spell("Examiner", "heal", 4, 2)
    }
}
