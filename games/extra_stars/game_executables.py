"""Expanding wild and respin executables for Extra Stars."""

import random

from game_calculations import GameCalculations
from src.calculations.lines import Lines
from src.calculations.statistics import get_random_outcome


class GameExecutables(GameCalculations):
    """Wild expansion, partial respins, and bidirectional evaluation."""

    def detect_wild_reels(self, exclude_reels: list[int] | None = None) -> list[int]:
        """Return reels 2-4 that contain a stea wild (not yet locked)."""
        excluded = set(exclude_reels or [])
        wild_reels = []
        for reel in self.config.wild_reels:
            if reel in excluded:
                continue
            for row in range(self.config.num_rows[reel]):
                if self.board[reel][row].check_attribute("wild"):
                    wild_reels.append(reel)
                    break
        return wild_reels

    def expand_wild_reels(self, reels: list[int]) -> None:
        """Fill entire reel column with stea wild symbols."""
        for reel in reels:
            for row in range(self.config.num_rows[reel]):
                self.board[reel][row] = self.create_symbol("stea")

    def process_initial_wilds(self) -> list[int]:
        """Detect and expand wild reels on the initial board."""
        wild_reels = self.detect_wild_reels()
        if wild_reels:
            self.expand_wild_reels(wild_reels)
        return wild_reels

    def draw_respin_board(self, locked_reels: list[int]) -> None:
        """Re-spin unlocked reels while keeping expanded wild reels fixed."""
        locked = set(locked_reels)
        unlocked = [reel for reel in range(self.config.num_reels) if reel not in locked]

        self.refresh_special_syms()
        if not hasattr(self, "reelstrip_id") or self.reelstrip_id is None:
            self.reelstrip_id = get_random_outcome(
                self.get_current_distribution_conditions()["reel_weights"][self.gametype]
            )
        self.reelstrip = self.config.reels[self.reelstrip_id]

        for reel in unlocked:
            reel_pos = random.randrange(0, len(self.reelstrip[reel]))
            self.reel_positions[reel] = reel_pos
            for row in range(self.config.num_rows[reel]):
                sym_id = self.reelstrip[reel][(reel_pos + row) % len(self.reelstrip[reel])]
                self.board[reel][row] = self.create_symbol(sym_id)
            if self.config.include_padding:
                self.top_symbols[reel] = self.create_symbol(
                    self.reelstrip[reel][(reel_pos - 1) % len(self.reelstrip[reel])]
                )
                self.bottom_symbols[reel] = self.create_symbol(
                    self.reelstrip[reel][
                        (reel_pos + len(self.board[reel])) % len(self.reelstrip[reel])
                    ]
                )
                self.padding_position[reel] = (reel_pos + len(self.board[reel]) + 1) % len(
                    self.reelstrip[reel]
                )

        self.expand_wild_reels(list(locked))
        self.get_special_symbols_on_board()

    def evaluate_bidirectional_board(self) -> None:
        """Evaluate wins both ways and emit line-win events."""
        self.win_data = self.get_lines_bidirectional(
            self.board, self.config, global_multiplier=self.global_multiplier
        )
        Lines.record_lines_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        Lines.emit_linewin_events(self)
