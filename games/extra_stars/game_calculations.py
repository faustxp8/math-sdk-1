"""Bidirectional line-win calculations for Extra Stars."""

from copy import deepcopy

from src.executables.executables import Executables
from src.calculations.lines import Lines


class GameCalculations(Executables):
    """Game-specific calculation helpers."""

    @staticmethod
    def get_lines_bidirectional(board, config, global_multiplier: int = 1) -> dict:
        """Evaluate all paylines left-to-right and right-to-left."""
        ltr = Lines.get_lines(
            board,
            config,
            wild_key="wild",
            wild_sym="stea",
            global_multiplier=global_multiplier,
        )
        for win in ltr["wins"]:
            win["meta"]["direction"] = "ltr"

        reversed_board = [board[i] for i in range(len(board) - 1, -1, -1)]
        rtl_raw = Lines.get_lines(
            reversed_board,
            config,
            wild_key="wild",
            wild_sym="stea",
            global_multiplier=global_multiplier,
        )

        num_reels = len(board)
        rtl_wins = []
        for win in rtl_raw["wins"]:
            mapped_win = deepcopy(win)
            for pos in mapped_win["positions"]:
                pos["reel"] = num_reels - 1 - pos["reel"]
            mapped_win["meta"]["direction"] = "rtl"
            rtl_wins.append(mapped_win)

        return {
            "totalWin": ltr["totalWin"] + rtl_raw["totalWin"],
            "wins": ltr["wins"] + rtl_wins,
        }
