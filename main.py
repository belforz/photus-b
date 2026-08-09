"""Entry point: serves the Photus B categorization API over HTTP.

POST /v1/categorize {"text": "..."} -> category, category_code, confidence, ...
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "src")
sys.path.append(SRC_DIR)

# Reload workers spawn fresh processes that re-import by module path (not by
# re-running this file), so they need SRC_DIR on PYTHONPATH too.
existing_pythonpath = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = os.pathsep.join(p for p in (SRC_DIR, existing_pythonpath) if p)

from presentation.api.app import app  # noqa: E402  (import after sys.path setup)

__all__ = ["app"]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "presentation.api.app:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )
