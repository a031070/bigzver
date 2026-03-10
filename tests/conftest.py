import sys
import os

# Project root is one level above this tests/ directory.
# All source modules (sprites, spells, settings, game_input) live there
# and use bare imports, so the root must be on sys.path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
