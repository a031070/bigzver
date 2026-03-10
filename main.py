from sprites import Unit
from game_input import player_input, enemy_upgrade
from settings import Settings as S

player = Unit("player")
enemy = Unit("enemy")

player.info()
enemy.info()

is_player_turn = True

while player.is_alive() and enemy.is_alive():
    print(S.turn[is_player_turn])

    player.mana_up()
    enemy.mana_up()

    if is_player_turn:
        player_spell = player_input()
        player_spell.cast(player, enemy)
    else:
        enemy_upgrade()

    is_player_turn = not is_player_turn
    input()

if player.is_alive():
    print(f"{player.name} победил!")
else:
    print(f"{enemy.name} победил!")
