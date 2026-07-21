"""Unit tests for Extra Stars bidirectional lines and wild mechanics."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "games" / "extra_stars"))

from game_config import GameConfig
from game_calculations import GameCalculations
from game_executables import GameExecutables
from tests.win_calculations.game_test_config import create_blank_board


class ExtraStarsTestState(GameExecutables):
    """Minimal gamestate for unit testing Extra Stars logic."""

    def __init__(self, config):
        self.config = config
        self.global_multiplier = 1
        self.gametype = config.basegame_type
        self.special_symbol_functions = {}
        self.special_syms_on_board = {"wild": [], "scatter": [], "multiplier": []}

    def assign_special_sym_function(self):
        self.special_symbol_functions = {}

    def create_symbol(self, name: str):
        if name not in self.symbol_storage.symbol_defs.keys():
            raise ValueError(f"Symbol '{name}' is not registered.")
        sym_object = self.symbol_storage.create_symbol(name)
        return sym_object

    def refresh_special_syms(self):
        self.special_syms_on_board = {"wild": [], "scatter": [], "multiplier": []}

    def get_special_symbols_on_board(self):
        for reel, _ in enumerate(self.board):
            for row, _ in enumerate(self.board[reel]):
                if self.board[reel][row].check_attribute("wild"):
                    self.special_syms_on_board["wild"].append({"reel": reel, "row": row})

    def get_current_distribution_conditions(self):
        return {"reel_weights": {self.gametype: {"BR0": 1}}}

    def run_spin(self, sim, simulation_seed=None):
        pass

    def run_freespin(self):
        pass


def create_extra_stars_gamestate():
    config = GameConfig()
    gamestate = ExtraStarsTestState(config)
    gamestate.create_symbol_map()
    gamestate.assign_special_sym_function()
    gamestate.board = create_blank_board(config.num_reels, config.num_rows)
    for reel in range(config.num_reels):
        for row in range(config.num_rows[reel]):
            gamestate.board[reel][row] = gamestate.create_symbol("cireasa")
    gamestate.reel_positions = [0] * config.num_reels
    gamestate.top_symbols = [gamestate.create_symbol("cireasa") for _ in range(config.num_reels)]
    gamestate.bottom_symbols = [gamestate.create_symbol("cireasa") for _ in range(config.num_reels)]
    gamestate.padding_position = [0] * config.num_reels
    gamestate.reelstrip_id = "BR0"
    gamestate.reelstrip = config.reels["BR0"]
    return gamestate


@pytest.fixture
def gamestate():
    return create_extra_stars_gamestate()


def test_bidirectional_pay_middle_line(gamestate):
    """Middle line 5-kind pays in both directions."""
    for reel in range(5):
        for row in range(3):
            gamestate.board[reel][row] = gamestate.create_symbol("cireasa")
        gamestate.board[reel][1] = gamestate.create_symbol("septar")

    windata = GameCalculations.get_lines_bidirectional(gamestate.board, gamestate.config)
    line1_wins = [w for w in windata["wins"] if w["meta"]["lineIndex"] == 1]
    assert len(line1_wins) == 2
    assert {w["meta"]["direction"] for w in line1_wins} == {"ltr", "rtl"}
    assert sum(w["win"] for w in line1_wins) == gamestate.config.paytable[(5, "septar")] * 2


def test_expand_wild_reel(gamestate):
    """stea on reel 2 expands all rows on that reel."""
    gamestate.board[1][0] = gamestate.create_symbol("stea")
    gamestate.expand_wild_reels([1])

    for row in range(3):
        assert gamestate.board[1][row].name == "stea"
        assert gamestate.board[1][row].check_attribute("wild")


def test_detect_wild_reels_only_middle(gamestate):
    """Wild detection ignores reels 1 and 5."""
    gamestate.board[0][1] = gamestate.create_symbol("stea")
    gamestate.board[4][1] = gamestate.create_symbol("stea")
    assert gamestate.detect_wild_reels() == []

    gamestate.board[2][0] = gamestate.create_symbol("stea")
    assert gamestate.detect_wild_reels() == [2]


def test_respin_preserves_locked_reel(gamestate):
    """Locked wild reel stays expanded after respin."""
    gamestate.expand_wild_reels([1])

    gamestate.draw_respin_board([1])

    for row in range(3):
        assert gamestate.board[1][row].name == "stea"
    assert gamestate.board[0][0].name in gamestate.config.reels["BR0"][0]


def test_wild_substitution(gamestate):
    """Expanded wild helps form a 3-kind line."""
    gamestate.board[0][1] = gamestate.create_symbol("banane")
    gamestate.expand_wild_reels([1])
    gamestate.board[2][1] = gamestate.create_symbol("banane")

    windata = GameCalculations.get_lines_bidirectional(gamestate.board, gamestate.config)
    assert windata["totalWin"] > 0
