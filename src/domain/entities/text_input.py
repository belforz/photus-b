from dataclasses import dataclass


@dataclass()
class TextInput:
    """Represents a text input for processing.

    Attributes:
        role: The role of the message author (e.g., "user", "system").
        content: The text content of the message.
    """
    role: str
    content: str
