from pathlib import Path
import json
from typing import Optional, Dict, Tuple


PROMPTS_DIR = Path(__file__).resolve().parent


def _find_file(name: str) -> Optional[Path]:
    # look for .md, .txt, .json (in that order)
    for suf in (".md", ".txt", ".json"):
        p = PROMPTS_DIR / f"{name}{suf}"
        if p.exists():
            return p
    return None


def _parse_front_matter_md(text: str) -> Tuple[Dict[str, str], str]:
    if text.lstrip().startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1].strip()
            body = parts[2].lstrip()
            meta: Dict[str, str] = {}
            for line in fm.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            return meta, body
    return {}, text


def load_prompt(name: str, **kwargs) -> str:
    """Load a prompt by name. Supports .md (with optional YAML front-matter), .txt and .json.

    Returns the prompt body as a formatted string (applies simple str.format).
    """
    p = _find_file(name)
    if p is None:
        raise FileNotFoundError(f"Prompt file not found: {name}")

    text = p.read_text(encoding="utf-8")
    if p.suffix == ".json":
        try:
            data = json.loads(text)
            template = data.get("template") or data.get("content") or text
        except Exception:
            template = text
    elif p.suffix == ".md":
        _, body = _parse_front_matter_md(text)
        template = body
    else:
        template = text

    try:
        return template.format(**kwargs)
    except Exception:
        return template
