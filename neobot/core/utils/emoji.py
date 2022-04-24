"""Utilities for using common emojis without polluting the source"""
import logging

logger = logging.getLogger(__name__)

emoji_map = {
    "YES": "✅✔☑",
    "NO": "❎❌",
    "SUCCESS": "✅",
    "FAILURE": "❎",
    "SMILE": "😀😁😄😊🙂",
    "SAD": "☹😞😔😢😟😖😭",
    "UP": "👆☝🆙👍⬆🔝🔼",
    "DOWN": "👇👎⏬⬇🔽",
    "THUMBS_UP": "👍",
    "THUMBS_DOWN": "👎",
    "+1": "👍",
    "-1": "👎",
    "STOP": "🤚✋",
    "STONKS_UP": "📈💹",
    "STONKS_DOWN": "📉",
    "ILLUMINATI": "👽👾",
    "NSFW": "🔞🚫",
    "DENIED": "🚫",
    "IMP": "❗❕⚠‼",
    "CAUTION": "⚠",
    "FAST": ("🚗💨", "🏃💨"),
    "PUZZLED": "😕"
}

def get_emoji(emoji: str, degree: int = 0) -> str:
    """Gets an emoji

    Parameters
    ----------
    emoji : int
        The name of the emoji
    degree : Optional[int]
        The degree of choice, 0th emojis are recommended, by default 0

    Returns
    -------
    str
        The emoji, An empty string if not found.
    """
    try:
        res = emoji_map[emoji][degree] # type: str
    except IndexError:
        # Try to be cyclic
        res = emoji_map[emoji][(degree % len(emoji_map[emoji]))]
        # logging because obviously this is a mistake in the code
        logger.info(f"❗ | Degree {degree} for emoji {emoji} not available")
    except KeyError:
        logger.exception(f"❗ | Emoji {emoji} not found!")
        res = ""
    return res
