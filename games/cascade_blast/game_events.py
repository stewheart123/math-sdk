"""Events for bonus-area highlights, forced pairs, and SA+SB explosions."""

from src.events.events import json_ready_sym

BONUS_AREA_REVEAL = "bonusAreaReveal"
BONUS_AREA_UPDATE = "bonusAreaUpdate"
FORCE_PAIR = "forcePair"
EXPLOSION = "explosion"


def _pad_row(gamestate, row: int) -> int:
    if gamestate.config.include_padding:
        return row + 1
    return row


def _client_positions(gamestate, cells):
    return [{"reel": reel, "row": _pad_row(gamestate, row)} for reel, row in cells]


def bonus_area_reveal_event(gamestate) -> None:
    """Highlight bonus-area cells on the existing 7x7 frame."""
    event = {
        "index": len(gamestate.book.events),
        "type": BONUS_AREA_REVEAL,
        "positions": _client_positions(
            gamestate, [(pos["reel"], pos["row"]) for pos in gamestate.bonus_areas]
        ),
    }
    gamestate.book.add_event(event)


def bonus_area_update_event(gamestate) -> None:
    """Move a bonus-area highlight (used when forcing FS books)."""
    event = {
        "index": len(gamestate.book.events),
        "type": BONUS_AREA_UPDATE,
        "positions": _client_positions(
            gamestate, [(pos["reel"], pos["row"]) for pos in gamestate.bonus_areas]
        ),
    }
    gamestate.book.add_event(event)


def force_pair_event(gamestate, sa_reel: int, row: int) -> None:
    """Show a forced SA+SB pair for the volatile bonus buy."""
    special_attributes = list(gamestate.config.special_symbols.keys())
    event = {
        "index": len(gamestate.book.events),
        "type": FORCE_PAIR,
        "positions": [
            {
                "reel": sa_reel,
                "row": _pad_row(gamestate, row),
                "symbol": json_ready_sym(gamestate.board[sa_reel][row], special_attributes),
            },
            {
                "reel": sa_reel + 1,
                "row": _pad_row(gamestate, row),
                "symbol": json_ready_sym(gamestate.board[sa_reel + 1][row], special_attributes),
            },
        ],
    }
    gamestate.book.add_event(event)


def explosion_event(gamestate, pairs: list, cells: list, volatile: bool) -> None:
    """Emit SA+SB blast details before the tumble."""
    event = {
        "index": len(gamestate.book.events),
        "type": EXPLOSION,
        "mode": "volatile" if volatile else "normal",
        "pairs": [
            {
                "sa": {"reel": sa_reel, "row": _pad_row(gamestate, row)},
                "sb": {"reel": sa_reel + 1, "row": _pad_row(gamestate, row)},
            }
            for sa_reel, row in pairs
        ],
        "positions": _client_positions(gamestate, cells),
    }
    gamestate.book.add_event(event)
