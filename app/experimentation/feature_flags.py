"""
PaiseWise AI Feature Flag Management

Allows AI features to be enabled/disabled for specific user segments
without changing the application code.

Supported segments:
- free
- premium
- all

Example:
    is_feature_enabled("U001", "portfolio_diversification")
"""

from typing import Dict, List


# ============================================================
# FEATURE FLAG CONFIGURATION
# ============================================================

FEATURE_FLAGS: Dict[str, Dict[str, object]] = {
    "jargon": {
        "enabled": True,
        "segments": ["free", "premium"],
    },

    "portfolio_diversification": {
        "enabled": True,
        "segments": ["free", "premium"],
    },

    "market_context": {
        "enabled": True,
        "segments": ["premium"],
    },

    "news": {
        "enabled": True,
        "segments": ["free", "premium"],
    },

    "news_classify": {
        "enabled": True,
        "segments": ["premium"],
    },

    "churn_prediction": {
        "enabled": True,
        "segments": ["premium"],
    },
}


# ============================================================
# USER SEGMENT CONFIGURATION
# ============================================================

USER_SEGMENTS: Dict[str, str] = {
    "U001": "premium",
    "U002": "free",
    "U003": "premium",
}


# ============================================================
# GET USER SEGMENT
# ============================================================

def get_user_segment(user_id: str) -> str:
    """
    Return the segment assigned to a user.

    Unknown users are treated as free users by default.
    """

    return USER_SEGMENTS.get(user_id, "free")


# ============================================================
# CHECK FEATURE FLAG
# ============================================================

def is_feature_enabled(
    user_id: str,
    feature_name: str
) -> bool:
    """
    Check whether a feature is enabled for a specific user.

    Returns:
        True  -> feature is available
        False -> feature is disabled
    """

    feature = FEATURE_FLAGS.get(feature_name)

    # Feature does not exist
    if feature is None:
        return False

    # Feature globally disabled
    if not feature.get("enabled", False):
        return False

    user_segment = get_user_segment(user_id)

    allowed_segments = feature.get("segments", [])

    # "all" allows every segment
    if "all" in allowed_segments:
        return True

    return user_segment in allowed_segments


# ============================================================
# ENABLE / DISABLE FEATURE
# ============================================================

def set_feature_status(
    feature_name: str,
    enabled: bool
) -> bool:
    """
    Enable or disable a feature globally.

    Returns:
        True if the feature exists and was updated.
        False if the feature does not exist.
    """

    if feature_name not in FEATURE_FLAGS:
        return False

    FEATURE_FLAGS[feature_name]["enabled"] = enabled

    return True


# ============================================================
# UPDATE FEATURE SEGMENTS
# ============================================================

def set_feature_segments(
    feature_name: str,
    segments: List[str]
) -> bool:
    """
    Change which user segments can access a feature.

    Example:
        set_feature_segments(
            "portfolio_diversification",
            ["premium"]
        )
    """

    if feature_name not in FEATURE_FLAGS:
        return False

    FEATURE_FLAGS[feature_name]["segments"] = segments

    return True


# ============================================================
# GET ALL FEATURE FLAGS
# ============================================================

def get_all_feature_flags() -> Dict[str, Dict[str, object]]:
    """
    Return the current feature flag configuration.
    """

    return FEATURE_FLAGS


# ============================================================
# GET FEATURE STATUS FOR A USER
# ============================================================

def get_user_feature_status(
    user_id: str
) -> Dict[str, bool]:
    """
    Return the enabled/disabled status of every feature
    for a specific user.
    """

    return {
        feature_name: is_feature_enabled(
            user_id,
            feature_name
        )
        for feature_name in FEATURE_FLAGS
    }