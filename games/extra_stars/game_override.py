"""Extra Stars game state overrides."""

from game_executables import GameExecutables


class GameStateOverride(GameExecutables):
    """Reset and repeat logic for Extra Stars."""

    def reset_book(self):
        super().reset_book()
        self.locked_reels = []

    def assign_special_sym_function(self):
        self.special_symbol_functions = {}

    def check_repeat(self):
        super().check_repeat()
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
            if win_criteria is None and self.final_win == 0:
                self.repeat = True

    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Draw board, optionally forcing wild respin or wincap outcomes."""
        conditions = self.get_current_distribution_conditions()
        if conditions.get("force_wincap"):
            self.create_board_reelstrips()
            for reel in range(self.config.num_reels):
                for row in range(self.config.num_rows[reel]):
                    self.board[reel][row] = self.create_symbol("septar")
            self.get_special_symbols_on_board()
        elif conditions.get("force_wild_respin"):
            self.create_board_reelstrips()
            attempts = 0
            while not self.detect_wild_reels() and attempts < 100:
                self.create_board_reelstrips()
                attempts += 1
        else:
            self.create_board_reelstrips()

        if emit_event:
            from src.events.events import reveal_event

            reveal_event(self)
