class Unit:
    def __init__(self, name):
        self.name = name
        self.hp = 10
        self.defense = 10
        self.mana = 0

    def info(self):
        print(f"{self.name}: HP={self.hp}, Defense={self.defense}, Mana={self.mana}")

    def is_alive(self):
        return self.hp > 0

    def mana_up(self):
        self.mana += 10

    def take_damage(self, dmg):
        if self.defense >= dmg:
            self.defense -= dmg
        else:
            self.hp -= (dmg - self.defense)
            self.defense = 0

    def defense_up(self, grade):
        self.defense += grade

    def dev_heal(self, grade):
        self.hp += grade
