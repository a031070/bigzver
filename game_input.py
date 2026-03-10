from spells import spells

def player_input():
    n_types = {}
    print("Выберите тип заклинания:")
    for i, t in enumerate(spells):
        print(f"{i + 1} - {t}")
        n_types[str(i + 1)] = t

    player_choice = input()
    while player_choice not in n_types:
        print("Неверный ввод")
        player_choice = input()

    type_spell = n_types[player_choice]

    n_spells = {}
    print(f"Выберите заклинание из {type_spell}:")
    for i, t in enumerate(spells[type_spell]):
        print(f"{i + 1} - {spells[type_spell][t].name}")
        n_spells[str(i + 1)] = t

    spell_choice = input()
    while spell_choice not in n_spells:
        print("Неверный ввод")
        spell_choice = input()

    spell = spells[type_spell][n_spells[spell_choice]]
    return spell

def enemy_upgrade():
    pass
