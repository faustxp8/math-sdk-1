"""Extra Stars game state and spin flow."""

from game_override import GameStateOverride
from game_events import expanding_wild_event, respin_trigger_event
from src.events.events import reveal_event


class GameState(GameStateOverride):
    """Handles game logic and events for a single simulation round."""

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board(emit_event=False)

            locked_reels = self.process_initial_wilds()
            if locked_reels:
                expanding_wild_event(self, locked_reels)
            reveal_event(self)
            self.evaluate_bidirectional_board()

            if locked_reels:
                while True:
                    respin_trigger_event(self, locked_reels)
                    self.draw_respin_board(locked_reels)

                    new_wild_reels = self.detect_wild_reels(exclude_reels=locked_reels)
                    if new_wild_reels:
                        self.expand_wild_reels(new_wild_reels)
                        expanding_wild_event(self, new_wild_reels)
                        locked_reels = sorted(set(locked_reels + new_wild_reels))

                    reveal_event(self)
                    self.evaluate_bidirectional_board()

                    if not new_wild_reels:
                        break

            self.win_manager.update_gametype_wins(self.gametype)
            self.evaluate_finalwin()
            self.check_repeat()
        self.imprint_wins()

    def run_freespin(self):
        """Extra Stars has no free-spin feature."""
        pass
