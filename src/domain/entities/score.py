from dataclasses import dataclass
from typing import Optional


@dataclass()
class Score:
    """Represents a score metric, which is a value object.

    It includes a numerical score and an optional descriptive label.
    """

    points: float
    label: Optional[str] = None

    