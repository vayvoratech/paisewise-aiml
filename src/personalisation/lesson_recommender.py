# ============================================================
# PAISEWISE PERSONALISATION
# DAILY PERSONALISED LESSON RECOMMENDER
# ============================================================

from .learning_dna import build_learning_dna


# ------------------------------------------------------------
# Sample lesson catalog
# ------------------------------------------------------------
# This is development/sample data for Task 5.
# Later, this can be replaced with lessons from the database.
# ------------------------------------------------------------

LESSON_CATALOG = {
    "mutual_funds": [
        {
            "title": "Understanding Mutual Fund Categories",
            "description": (
                "Learn about equity, debt, hybrid and other "
                "mutual fund categories."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "How Mutual Funds Work",
            "description": (
                "Understand how mutual funds collect and "
                "invest money from investors."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "Mutual Fund Risk and Returns",
            "description": (
                "Learn how risk and returns differ across "
                "different mutual fund investments."
            ),
            "difficulty": "intermediate"
        }
    ],

    "sip": [
        {
            "title": "Introduction to SIP",
            "description": (
                "Learn how Systematic Investment Plans work "
                "and how regular investing builds discipline."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "SIP vs Lump Sum Investing",
            "description": (
                "Understand the basic differences between "
                "SIP and lump sum investing."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "SIP and Compounding",
            "description": (
                "Learn how regular investments can benefit "
                "from long-term compounding."
            ),
            "difficulty": "intermediate"
        }
    ],

    "diversification": [
        {
            "title": "Understanding Portfolio Diversification",
            "description": (
                "Learn why spreading investments across "
                "different assets can reduce concentration."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "Diversification Across Sectors",
            "description": (
                "Learn how investments can be distributed "
                "across different sectors."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "Portfolio Concentration Risk",
            "description": (
                "Understand the risks of having too much "
                "money invested in one area."
            ),
            "difficulty": "intermediate"
        }
    ],

    "stocks": [
        {
            "title": "Introduction to Stocks",
            "description": (
                "Learn the basics of stocks and how stock "
                "markets work."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "Understanding Stock Market Risk",
            "description": (
                "Learn about common risks associated with "
                "stock market investing."
            ),
            "difficulty": "intermediate"
        },
        {
            "title": "Reading Basic Stock Information",
            "description": (
                "Learn how to understand basic information "
                "about a company and its stock."
            ),
            "difficulty": "intermediate"
        }
    ],

    "risk": [
        {
            "title": "Understanding Investment Risk",
            "description": (
                "Learn the basics of investment risk and "
                "why risk matters."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "Risk and Return",
            "description": (
                "Understand the relationship between risk "
                "and potential returns."
            ),
            "difficulty": "intermediate"
        }
    ],

    "portfolio": [
        {
            "title": "Portfolio Basics",
            "description": (
                "Learn what an investment portfolio is and "
                "how different assets can be combined."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "Building a Balanced Portfolio",
            "description": (
                "Learn the basic principles of creating a "
                "diversified portfolio."
            ),
            "difficulty": "intermediate"
        }
    ],

    "saving": [
        {
            "title": "Building a Saving Habit",
            "description": (
                "Learn simple principles for developing "
                "a consistent saving habit."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "Short-Term and Long-Term Savings",
            "description": (
                "Understand how saving goals can differ "
                "based on time horizon."
            ),
            "difficulty": "beginner"
        }
    ],

    "budgeting": [
        {
            "title": "Budgeting Basics",
            "description": (
                "Learn how to plan income and expenses "
                "using a simple budget."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "Creating a Monthly Budget",
            "description": (
                "Learn how to organise monthly income, "
                "expenses and savings."
            ),
            "difficulty": "beginner"
        }
    ],

    "emergency_fund": [
        {
            "title": "Understanding Emergency Funds",
            "description": (
                "Learn why an emergency fund is important "
                "for unexpected expenses."
            ),
            "difficulty": "beginner"
        },
        {
            "title": "Planning Your Emergency Fund",
            "description": (
                "Learn the basic steps for planning an "
                "emergency savings fund."
            ),
            "difficulty": "intermediate"
        }
    ]
}


def find_lesson_for_user(top_topic, difficulty):
    """
    Find a lesson matching the user's main topic
    and preferred difficulty.
    """

    if not top_topic:
        top_topic = "saving"

    lessons = LESSON_CATALOG.get(top_topic, [])

    if not lessons:
        return {
            "title": "Personal Finance Basics",
            "description": (
                "Learn a useful personal finance concept "
                "to improve your financial knowledge."
            ),
            "difficulty": difficulty
        }

    # First try to match the user's preferred difficulty.
    for lesson in lessons:
        if lesson["difficulty"] == difficulty:
            return lesson

    # If exact difficulty is not available,
    # return the first lesson for that topic.
    return lessons[0]


def recommend_daily_lesson(user_id: str):

    learning_dna = build_learning_dna(user_id)

    if not learning_dna:
        return None

    interests = learning_dna.get(
        "interests",
        {}
    )

    activity = learning_dna.get(
        "learning_activity",
        {}
    )

    preference = learning_dna.get(
        "learning_preference",
        {}
    )

    top_topic = interests.get(
        "top_topic"
    )

    completed_lessons = activity.get(
        "completed_lessons",
        0
    )

    difficulty = preference.get(
        "difficulty",
        "beginner"
    )

    lesson = find_lesson_for_user(
        top_topic,
        difficulty
    )

    topic_name = (
        top_topic.replace("_", " ")
        if top_topic
        else "personal finance"
    )

    return {
        "user_id": user_id,

        "recommendation": {
            "title": lesson["title"],
            "description": lesson["description"],
            "topic": topic_name,
            "difficulty": lesson["difficulty"]
        },

        "personalisation_reason": (
            f"This lesson is recommended because "
            f"{topic_name} is the user's main learning "
            f"interest and their preferred difficulty "
            f"is {difficulty}."
        ),

        "learning_history": {
            "completed_lessons": completed_lessons,
            "top_topic": top_topic,
            "preferred_difficulty": difficulty
        },

        "message": (
            "Today's lesson just for you."
        )
    }