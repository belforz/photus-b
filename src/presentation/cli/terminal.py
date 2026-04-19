import typer
from typing import List, Optional
from rich.console import Console


class CommandLineInterface:
    """Small helper for CLI-related utilities.

    This class does not register Typer commands itself; it provides a
    convenience method `args_text` that returns either the provided
    `text` (when running from a Typer command) or a supplied list of
    default texts (useful for programmatic use).
    """

    def __init__(self, default_texts: Optional[List[str]] = None):
        self.default_texts = default_texts or []
        self.console = Console()

    def args_text(self, text: Optional[List[str]] = None) -> List[str]:
        """Return list of texts to process.

        If `text` is provided (from CLI), return it as a list;
        otherwise return the `default_texts` supplied at construction.
        """
        if text:
            return text
        return self.default_texts

    def style_rich_text(self, text: str, style: str) -> str:
        return f"[{style}]{text}[/{style}]"





