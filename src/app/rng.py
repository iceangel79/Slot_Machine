"""Random sources for the stop positions (decision 0008).

Every source is a function that takes the lengths of the reel strips and
returns one stop position per reel (0 <= position < length).

random.org and the fallback to Python follow in step 8.
"""

import secrets

PYTHON = "python"


def python_stop_positions(strip_lengths):
    """Draw the stop positions with Python's secure random generator."""
    return [secrets.randbelow(length) for length in strip_lengths]
