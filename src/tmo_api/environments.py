"""Environment configurations for The Mortgage Office SDK."""

from enum import Enum
from typing import Final


class Environment(Enum):
    """Supported API environments."""

    US = "https://api.themortgageoffice.com"
    CANADA = "https://api-ca.themortgageoffice.com"
    AUSTRALIA = "https://api-aus.themortgageoffice.com"


# Default environment
DEFAULT_ENVIRONMENT: Final[Environment] = Environment.US
