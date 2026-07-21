"""Extra Stars game configuration."""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "extra_stars"
        self.provider_number = 0
        self.working_name = "Extra Stars"
        self.wincap = 2000.0
        self.win_type = "lines"
        self.rtp = 0.9578
        self.construct_paths()

        self.num_reels = 5
        self.num_rows = [3] * self.num_reels

        self.paytable = {
            (5, "septar"): 100,
            (4, "septar"): 50,
            (3, "septar"): 10,
            (5, "banane"): 50,
            (4, "banane"): 20,
            (3, "banane"): 5,
            (5, "lubenita"): 20,
            (4, "lubenita"): 5,
            (3, "lubenita"): 2,
            (5, "struguri"): 20,
            (4, "struguri"): 5,
            (3, "struguri"): 2,
            (5, "portocala"): 15,
            (4, "portocala"): 3,
            (3, "portocala"): 1,
            (5, "pruna"): 15,
            (4, "pruna"): 3,
            (3, "pruna"): 1,
            (5, "lamaie"): 10,
            (4, "lamaie"): 2,
            (3, "lamaie"): 1,
            (5, "cireasa"): 10,
            (4, "cireasa"): 2,
            (3, "cireasa"): 1,
        }

        self.paylines = {
            1: [1, 1, 1, 1, 1],
            2: [0, 0, 0, 0, 0],
            3: [2, 2, 2, 2, 2],
            4: [0, 1, 2, 1, 0],
            5: [2, 1, 0, 1, 2],
            6: [0, 0, 1, 0, 0],
            7: [2, 2, 1, 2, 2],
            8: [1, 1, 0, 1, 1],
            9: [0, 1, 0, 1, 0],
            10: [2, 1, 2, 1, 2],
        }

        self.wild_reels = [1, 2, 3]
        self.include_padding = True
        self.special_symbols = {"wild": ["stea"]}

        self.freespin_triggers = {self.basegame_type: {}, self.freegame_type: {}}
        self.anticipation_triggers = {self.basegame_type: 0, self.freegame_type: 0}

        reels = {"BR0": "BR0.csv", "WCAP": "WCAP.csv"}
        self.reels = {}
        for reel_id, filename in reels.items():
            self.reels[reel_id] = self.read_reels_csv(os.path.join(self.reels_path, filename))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]

        basegame_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "force_wincap": False,
        }

        zerowin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "force_wincap": False,
        }

        wincap_condition = {
            "reel_weights": {self.basegame_type: {"WCAP": 1}},
            "force_wincap": True,
        }

        respin_condition = {
            "reel_weights": {self.basegame_type: {"BR0": 1}},
            "force_wincap": False,
            "force_wild_respin": True,
        }

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions=wincap_condition,
                    ),
                    Distribution(
                        criteria="respin",
                        quota=0.05,
                        conditions=respin_condition,
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.35,
                        win_criteria=0.0,
                        conditions=zerowin_condition,
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.599,
                        conditions=basegame_condition,
                    ),
                ],
            ),
        ]
