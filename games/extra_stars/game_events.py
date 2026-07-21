"""Extra Stars specific game events."""

EXPANDING_WILDS = "expandingWilds"
RESPIN_TRIGGER = "respinTrigger"


def expanding_wild_event(gamestate, reels: list[int]) -> None:
    """Emit event when wild reels expand to full column."""
    wild_details = []
    for reel in reels:
        detail = {"reel": reel, "row": 0}
        if gamestate.config.include_padding:
            detail["row"] = 1
        wild_details.append(detail)

    event = {
        "index": len(gamestate.book.events),
        "type": EXPANDING_WILDS,
        "wildReels": wild_details,
    }
    gamestate.book.add_event(event)


def respin_trigger_event(gamestate, locked_reels: list[int]) -> None:
    """Emit event before a respin with locked wild reels."""
    event = {
        "index": len(gamestate.book.events),
        "type": RESPIN_TRIGGER,
        "lockedReels": sorted(locked_reels),
    }
    gamestate.book.add_event(event)
