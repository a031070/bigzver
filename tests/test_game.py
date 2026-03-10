"""
Comprehensive tests for the bigzver console magic battle game.

Modules under test:
  sprites.py   — Unit class
  spells.py    — Spell class and spells catalogue
  game_input.py — player_input() (enemy_upgrade is a stub, not tested)
"""

import pytest
from unittest.mock import patch

from sprites import Unit
from spells import Spell, spells
from game_input import player_input


# ---------------------------------------------------------------------------
# Helpers / shared factories
# ---------------------------------------------------------------------------

def make_unit(name="Hero"):
    """Return a freshly initialised Unit."""
    return Unit(name)


def make_spell(name="Test Bolt", type_spell="attack", price=5, grade=3):
    """Return a Spell with the given parameters."""
    return Spell(name, type_spell, price, grade)


# ---------------------------------------------------------------------------
# 1. Unit initialisation
# ---------------------------------------------------------------------------

class TestUnitInit:
    """Unit starts with the correct default attributes."""

    def test_name_is_stored(self):
        u = Unit("Merlin")
        assert u.name == "Merlin"

    def test_hp_starts_at_10(self):
        u = make_unit()
        assert u.hp == 10

    def test_defense_starts_at_10(self):
        u = make_unit()
        assert u.defense == 10

    def test_mana_starts_at_0(self):
        u = make_unit()
        assert u.mana == 0

    def test_different_names_are_independent(self):
        a = Unit("Alice")
        b = Unit("Bob")
        assert a.name != b.name


# ---------------------------------------------------------------------------
# 2. take_damage
# ---------------------------------------------------------------------------

class TestTakeDamage:
    """take_damage absorbs damage with defense before touching hp."""

    def test_damage_fully_absorbed_by_defense(self):
        u = make_unit()
        u.take_damage(5)
        assert u.defense == 5
        assert u.hp == 10

    def test_damage_exactly_equals_defense(self):
        u = make_unit()
        u.take_damage(10)
        assert u.defense == 0
        assert u.hp == 10

    def test_damage_overflows_into_hp(self):
        u = make_unit()
        u.take_damage(15)  # 10 absorbed, 5 overflow
        assert u.defense == 0
        assert u.hp == 5

    def test_defense_zeroed_on_overflow(self):
        u = make_unit()
        u.defense = 3
        u.take_damage(8)  # 3 absorbed, 5 overflow
        assert u.defense == 0
        assert u.hp == 5

    def test_zero_damage_changes_nothing(self):
        u = make_unit()
        u.take_damage(0)
        assert u.defense == 10
        assert u.hp == 10

    def test_damage_greater_than_defense_plus_hp(self):
        u = make_unit()
        u.take_damage(30)  # 10 defense absorbed, 20 overflow, hp = 10 - 20 = -10
        assert u.defense == 0
        assert u.hp == -10

    def test_no_defense_damage_goes_directly_to_hp(self):
        u = make_unit()
        u.defense = 0
        u.take_damage(4)
        assert u.hp == 6
        assert u.defense == 0

    def test_multiple_hits_accumulate_correctly(self):
        u = make_unit()
        u.take_damage(6)   # defense: 10 -> 4, hp: 10
        u.take_damage(6)   # defense: 4 -> 0, hp: 10 - 2 = 8
        assert u.defense == 0
        assert u.hp == 8


# ---------------------------------------------------------------------------
# 3. mana_up
# ---------------------------------------------------------------------------

class TestManaUp:
    """mana_up adds 10 mana each call."""

    def test_mana_up_increments_by_10(self):
        u = make_unit()
        u.mana_up()
        assert u.mana == 10

    def test_mana_up_twice(self):
        u = make_unit()
        u.mana_up()
        u.mana_up()
        assert u.mana == 20

    def test_mana_up_ten_times(self):
        u = make_unit()
        for _ in range(10):
            u.mana_up()
        assert u.mana == 100


# ---------------------------------------------------------------------------
# 4. is_alive
# ---------------------------------------------------------------------------

class TestIsAlive:
    """is_alive returns True when hp > 0, False when hp <= 0."""

    def test_alive_at_full_health(self):
        u = make_unit()
        assert u.is_alive() is True

    def test_alive_at_hp_1(self):
        u = make_unit()
        u.hp = 1
        assert u.is_alive() is True

    def test_dead_at_hp_0(self):
        u = make_unit()
        u.hp = 0
        assert u.is_alive() is False

    def test_dead_at_negative_hp(self):
        u = make_unit()
        u.hp = -5
        assert u.is_alive() is False

    def test_alive_transitions_to_dead_after_lethal_damage(self):
        u = make_unit()
        u.defense = 0
        assert u.is_alive() is True
        u.take_damage(10)
        assert u.is_alive() is False


# ---------------------------------------------------------------------------
# 5. defense_up
# ---------------------------------------------------------------------------

class TestDefenseUp:
    """defense_up increases defense by grade."""

    def test_defense_up_increases_defense(self):
        u = make_unit()
        u.defense_up(5)
        assert u.defense == 15

    def test_defense_up_by_zero(self):
        u = make_unit()
        u.defense_up(0)
        assert u.defense == 10

    def test_defense_up_multiple_times(self):
        u = make_unit()
        u.defense_up(3)
        u.defense_up(7)
        assert u.defense == 20

    def test_defense_up_on_depleted_defense(self):
        u = make_unit()
        u.defense = 0
        u.defense_up(8)
        assert u.defense == 8


# ---------------------------------------------------------------------------
# 6. dev_heal
# ---------------------------------------------------------------------------

class TestDevHeal:
    """dev_heal increases hp by grade."""

    def test_heal_increases_hp(self):
        u = make_unit()
        u.hp = 3
        u.dev_heal(5)
        assert u.hp == 8

    def test_heal_by_zero_changes_nothing(self):
        u = make_unit()
        u.dev_heal(0)
        assert u.hp == 10

    def test_heal_on_full_hp_goes_above_10(self):
        # There is no cap in the implementation.
        u = make_unit()
        u.dev_heal(5)
        assert u.hp == 15

    def test_heal_revives_unit_with_negative_hp(self):
        u = make_unit()
        u.hp = -5
        u.dev_heal(10)
        assert u.hp == 5


# ---------------------------------------------------------------------------
# 7–10. Spell.cast
# ---------------------------------------------------------------------------

class TestSpellCastAttack:
    """cast with type_spell='attack' damages the target unit."""

    def test_attack_spell_deals_damage_to_enemy(self):
        caster = make_unit("Caster")
        caster.mana = 20
        enemy = make_unit("Enemy")
        spell = make_spell(type_spell="attack", price=5, grade=8)
        spell.cast(caster, enemy)
        # grade=8, enemy.defense=10 -> defense absorbs all, no hp loss
        assert enemy.defense == 2
        assert enemy.hp == 10

    def test_attack_spell_overflow_reduces_enemy_hp(self):
        caster = make_unit("Caster")
        caster.mana = 30
        enemy = make_unit("Enemy")
        enemy.defense = 3
        spell = make_spell(type_spell="attack", price=10, grade=10)
        spell.cast(caster, enemy)
        # grade=10, enemy.defense=3 -> defense 0, hp = 10 - 7 = 3
        assert enemy.defense == 0
        assert enemy.hp == 3

    def test_attack_spell_does_not_modify_caster_hp(self):
        caster = make_unit("Caster")
        caster.mana = 20
        enemy = make_unit("Enemy")
        spell = make_spell(type_spell="attack", price=5, grade=5)
        spell.cast(caster, enemy)
        assert caster.hp == 10

    def test_attack_spell_does_not_modify_caster_defense(self):
        caster = make_unit("Caster")
        caster.mana = 20
        enemy = make_unit("Enemy")
        spell = make_spell(type_spell="attack", price=5, grade=5)
        spell.cast(caster, enemy)
        assert caster.defense == 10


class TestSpellCastDefense:
    """cast with type_spell='defense' boosts the caster's defense."""

    def test_defense_spell_increases_caster_defense(self):
        caster = make_unit("Caster")
        caster.mana = 20
        enemy = make_unit("Enemy")
        spell = make_spell(type_spell="defense", price=5, grade=7)
        spell.cast(caster, enemy)
        assert caster.defense == 17

    def test_defense_spell_does_not_modify_enemy(self):
        caster = make_unit("Caster")
        caster.mana = 20
        enemy = make_unit("Enemy")
        spell = make_spell(type_spell="defense", price=5, grade=7)
        spell.cast(caster, enemy)
        assert enemy.defense == 10
        assert enemy.hp == 10

    def test_defense_spell_does_not_modify_caster_hp(self):
        caster = make_unit("Caster")
        caster.mana = 20
        enemy = make_unit("Enemy")
        spell = make_spell(type_spell="defense", price=5, grade=7)
        spell.cast(caster, enemy)
        assert caster.hp == 10


class TestSpellCastHeal:
    """cast with type_spell='heal' restores caster's hp."""

    def test_heal_spell_increases_caster_hp(self):
        caster = make_unit("Caster")
        caster.hp = 4
        caster.mana = 20
        enemy = make_unit("Enemy")
        spell = make_spell(type_spell="heal", price=5, grade=6)
        spell.cast(caster, enemy)
        assert caster.hp == 10

    def test_heal_spell_does_not_modify_enemy(self):
        caster = make_unit("Caster")
        caster.hp = 4
        caster.mana = 20
        enemy = make_unit("Enemy")
        spell = make_spell(type_spell="heal", price=5, grade=6)
        spell.cast(caster, enemy)
        assert enemy.hp == 10
        assert enemy.defense == 10

    def test_heal_spell_does_not_modify_caster_defense(self):
        caster = make_unit("Caster")
        caster.hp = 4
        caster.mana = 20
        enemy = make_unit("Enemy")
        spell = make_spell(type_spell="heal", price=5, grade=6)
        spell.cast(caster, enemy)
        assert caster.defense == 10


class TestSpellCastDeductsMana:
    """cast always deducts price from caster.mana regardless of spell type."""

    def test_attack_deducts_mana(self):
        caster = make_unit()
        caster.mana = 30
        spell = make_spell(type_spell="attack", price=10, grade=3)
        spell.cast(caster, make_unit("Dummy"))
        assert caster.mana == 20

    def test_defense_deducts_mana(self):
        caster = make_unit()
        caster.mana = 30
        spell = make_spell(type_spell="defense", price=10, grade=3)
        spell.cast(caster, make_unit("Dummy"))
        assert caster.mana == 20

    def test_heal_deducts_mana(self):
        caster = make_unit()
        caster.mana = 30
        spell = make_spell(type_spell="heal", price=10, grade=3)
        spell.cast(caster, make_unit("Dummy"))
        assert caster.mana == 20

    def test_mana_goes_negative_when_insufficient(self):
        # The implementation does not guard against negative mana.
        caster = make_unit()
        caster.mana = 5
        spell = make_spell(type_spell="heal", price=10, grade=3)
        spell.cast(caster, make_unit("Dummy"))
        assert caster.mana == -5

    def test_exact_mana_cost_leaves_zero(self):
        caster = make_unit()
        caster.mana = 25
        spell = make_spell(type_spell="attack", price=25, grade=5)
        spell.cast(caster, make_unit("Dummy"))
        assert caster.mana == 0


# ---------------------------------------------------------------------------
# Spells catalogue
# ---------------------------------------------------------------------------

class TestSpellsCatalogue:
    """The spells dict contains expected categories and entries."""

    def test_spells_has_attack_category(self):
        assert "attack" in spells

    def test_spells_has_defense_category(self):
        assert "defense" in spells

    def test_spells_has_heal_category(self):
        assert "heal" in spells

    def test_attack_category_has_three_entries(self):
        assert len(spells["attack"]) == 3

    def test_defense_category_has_two_entries(self):
        assert len(spells["defense"]) == 2

    def test_heal_category_has_three_entries(self):
        assert len(spells["heal"]) == 3

    def test_avada_kedavra_attributes(self):
        spell = spells["attack"]["1"]
        assert spell.name == "Avada Kedavra"
        assert spell.type_spell == "attack"
        assert spell.price == 25
        assert spell.grade == 25

    def test_all_spells_are_spell_instances(self):
        for category in spells.values():
            for spell in category.values():
                assert isinstance(spell, Spell)


# ---------------------------------------------------------------------------
# game_input.player_input  (builtins.input mocked)
# ---------------------------------------------------------------------------

class TestPlayerInput:
    """player_input() returns the Spell chosen by the simulated user."""

    def test_returns_spell_instance(self):
        # Choose type 1 (attack), then spell 1 (Avada Kedavra)
        with patch("builtins.input", side_effect=["1", "1"]):
            result = player_input()
        assert isinstance(result, Spell)

    def test_attack_type_1_returns_avada_kedavra(self):
        with patch("builtins.input", side_effect=["1", "1"]):
            result = player_input()
        assert result.name == "Avada Kedavra"
        assert result.type_spell == "attack"

    def test_attack_type_spell_2_returns_furore_ignis(self):
        with patch("builtins.input", side_effect=["1", "2"]):
            result = player_input()
        assert result.name == "Furore Ignis"

    def test_defense_type_1_returns_amplexus(self):
        # Type 2 = defense in the iteration order of spells dict
        with patch("builtins.input", side_effect=["2", "1"]):
            result = player_input()
        assert result.name == "Amplexus"
        assert result.type_spell == "defense"

    def test_heal_type_1_returns_reformatio_status(self):
        # Type 3 = heal
        with patch("builtins.input", side_effect=["3", "1"]):
            result = player_input()
        assert result.name == "Reformatio Status"
        assert result.type_spell == "heal"

    def test_invalid_type_then_valid_type_retries(self):
        # First type choice is invalid ("9"), second is valid ("1")
        # Then spell choice is "1"
        with patch("builtins.input", side_effect=["9", "1", "1"]):
            result = player_input()
        assert result.type_spell == "attack"

    def test_invalid_spell_then_valid_spell_retries(self):
        # Type 1 = attack, first spell choice invalid ("9"), second is "2"
        with patch("builtins.input", side_effect=["1", "9", "2"]):
            result = player_input()
        assert result.name == "Furore Ignis"

    def test_multiple_invalid_inputs_before_valid(self):
        # Two bad type choices, then valid; one bad spell choice, then valid
        with patch("builtins.input", side_effect=["x", "0", "1", "z", "3"]):
            result = player_input()
        assert result.name == "Импетус"
