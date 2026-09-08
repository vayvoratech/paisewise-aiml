
import csv
import logging
from pathlib import Path

from cache.redis_cache import RedisCache
from services.jargon_service import get_jargon

logger = logging.getLogger("ai-service.cache-warming")
cache = RedisCache()
TOP_N = 100


def _top_terms():
    path = Path(__file__).resolve().parent.parent / "data" / "financial_terms.csv"
    if not path.exists():
        return ["Mutual Fund", "SIP", "NAV"]
    with path.open(newline="", encoding="utf-8") as handle:
        return [row["term"].strip() for row in csv.DictReader(handle) if row.get("term")][:TOP_N]


def warm_cache():
    warmed = 0
    for term in _top_terms():
        key = f"jargon:en:{term.lower()}"
        try:
            if cache.get(key):
                continue
            # Pre-generate through the same cache-first service path used by the API.
            get_jargon(term, "en")
            warmed += 1
        except Exception as error:
            # One failed warm-up must not prevent the service from starting.
            logger.warning("Could not warm jargon term %r: %s", term, error)
    logger.info("Jargon cache warming complete: %s terms generated", warmed)
