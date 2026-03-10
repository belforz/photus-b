from dataclasses import dataclass


@dataclass()
class Tag:
    """Represents a single tag identified in a text.

    It is a value object defined by its entity, label, and the corresponding text.
    """
    entity: str
    label: str
    text: str

    