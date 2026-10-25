"""Random sources for the stop positions (decisions 0008 and 0014).

Every source is a function that takes the lengths of the reel strips and
returns one stop position per reel (0 <= position < length).

 * python_stop_positions: Python's secure random generator. Used for autospin
   and mass simulation, and as fallback.
 * random_org_stop_positions: the external web service random.org. One request
   per reel, so every number lies exactly within the range of its reel.
 * manual_stop_positions: random.org with fallback to Python. Also returns the
   source that was actually used.
"""

import logging
import secrets
import urllib.request

PYTHON = "python"
RANDOM_ORG = "random.org"

# HTTP interface of random.org: no API key needed. random.org asks clients to
# send a User-Agent with a contact e-mail address.
RANDOM_ORG_URL = (
    "https://www.random.org/integers/"
    "?num=1&min=0&max={max}&col=1&base=10&format=plain&rnd=new"
)
USER_AGENT = "slot-machine-simulator (FFHS student project; adrian.wegmann@students.ffhs.ch)"
TIMEOUT_SECONDS = 3

logger = logging.getLogger(__name__)


def python_stop_positions(strip_lengths):
    """Draw the stop positions with Python's secure random generator."""
    return [secrets.randbelow(length) for length in strip_lengths]


def parse_random_org_number(text, length):
    """Convert the plain text answer of random.org into a stop position.

    Raises ValueError if the answer is not a number between 0 and length - 1.
    """
    number = int(text.strip())
    if not 0 <= number < length:
        raise ValueError(f"random.org returned {number}, expected 0..{length - 1}")
    return number


def _fetch_random_org_number(length):
    request = urllib.request.Request(
        RANDOM_ORG_URL.format(max=length - 1),
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return parse_random_org_number(response.read().decode("ascii"), length)


def random_org_stop_positions(strip_lengths):
    """Draw the stop positions from random.org, one request per reel.

    Raises OSError (network error, timeout, HTTP error such as an exhausted
    quota) or ValueError (unexpected answer).
    """
    return [_fetch_random_org_number(length) for length in strip_lengths]


def manual_stop_positions(strip_lengths):
    """Draw the stop positions for a manual spin.

    Returns (stops, source). Uses random.org; if any of the requests fails, all
    stop positions are drawn with Python instead, so a spin never mixes sources.
    """
    try:
        return random_org_stop_positions(strip_lengths), RANDOM_ORG
    except (OSError, ValueError):
        logger.warning("random.org failed, falling back to Python", exc_info=True)
        return python_stop_positions(strip_lengths), PYTHON