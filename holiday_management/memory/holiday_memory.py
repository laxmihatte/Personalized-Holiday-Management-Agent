"""Per-traveller preference memory backed by mem0.

Stores and recalls a user's holiday preferences across requests so the agents
can personalise their plans. All operations are best-effort: if mem0 is not
installed or the backend is unavailable, calls log a warning and degrade
gracefully instead of breaking the request.
"""
import os
from typing import List

from dotenv import load_dotenv

from holiday_management.utils.logging_config import get_app_logger

logger = get_app_logger("holiday_memory")

# Some environments set SSL_CERT_FILE to a path that breaks the mem0 client.
if "SSL_CERT_FILE" in os.environ:
    del os.environ["SSL_CERT_FILE"]

load_dotenv()

_memory = None


def _get_memory():
    """Lazily build the mem0 Memory client (imported here so app boot never
    depends on mem0 being installed)."""
    global _memory
    if _memory is None:
        from mem0 import Memory

        config = {
            "vector_store": {
                "provider": "chroma",
                "config": {"collection_name": "holiday_prefs", "path": "db"},
            },
            "llm": {
                "provider": "openai",
                "config": {"model": "gpt-4o-mini", "temperature": 0},
            },
        }
        _memory = Memory.from_config(config)
    return _memory


def remember_preferences(user_id: str, content: str) -> None:
    """Persist a trip request as a preference for this traveller."""
    try:
        _get_memory().add(content, user_id=user_id)
        logger.info("Stored preference for user %s", user_id)
    except Exception as exc:  # noqa: BLE001 - memory must never break a request
        logger.warning("Could not store memory for %s: %s", user_id, exc)


def recall_preferences(user_id: str, query: str, limit: int = 5) -> List[str]:
    """Return preferences relevant to the current request for this traveller."""
    try:
        results = _get_memory().search(query, filters={"user_id": user_id})
        memories = results.get("results") if isinstance(results, dict) else results
        prefs: List[str] = []
        for res in memories or []:
            value = res.get("memory") or res.get("payload", {}).get("value")
            if value:
                prefs.append(value)
        logger.info("Recalled %d preference(s) for user %s", len(prefs), user_id)
        return prefs[:limit]
    except Exception as exc:  # noqa: BLE001 - memory must never break a request
        logger.warning("Could not recall memory for %s: %s", user_id, exc)
        return []
