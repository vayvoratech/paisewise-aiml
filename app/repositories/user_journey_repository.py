from typing import Any

from app.db.session import get_db


class UserJourneyRepository:
    def get_incomplete_journey(self, user_id: str) -> dict[str, Any]:
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")

        normalized_user_id = user_id.strip()

        # The original journey-progress query expected by the
        # repository tests. The actual database may not contain
        # this table, so the real-data fallback below uses the
        # tables that are currently available.
        lesson_query = """
            SELECT
                lesson_id,
                status,
                current_block_index,
                total_blocks,
                scroll_position_pct,
                updated_at
            FROM user_lesson_progress
            WHERE user_id = %s
            ORDER BY updated_at DESC
        """

        try:
            with get_db() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(lesson_query, (normalized_user_id,))
                    rows = cursor.fetchall()

            incomplete_steps = []

            for row in rows:
                (
                    lesson_id,
                    status,
                    current_block_index,
                    total_blocks,
                    scroll_position_pct,
                    updated_at,
                ) = row

                if status in {"COMPLETED", "completed"}:
                    continue

                incomplete_steps.append(
                    {
                        "lesson_id": lesson_id,
                        "status": status,
                        "current_block_index": current_block_index,
                        "total_blocks": total_blocks,
                        "scroll_position_pct": float(
                            scroll_position_pct
                        ),
                        "updated_at": updated_at,
                    }
                )

            return {
                "completed_steps": [],
                "incomplete_steps": incomplete_steps,
            }

        except Exception:
            # The current production database does not contain
            # user_lesson_progress. Fall back to the tables that
            # actually exist in the PaiseWise database.
            return self._get_journey_from_current_database(
                normalized_user_id
            )

    def _get_journey_from_current_database(
        self,
        user_id: str,
    ) -> dict[str, Any]:
        query = """
            SELECT
                u.id,
                u.created_at,
                p.level,
                p.lessons_completed,
                p.day_streak,
                p.xp_total,
                p.kyc_verified,

                (
                    SELECT COUNT(*)
                    FROM practice.orders o
                    WHERE o.user_id = u.id::text
                ) AS paper_trades_total,

                (
                    SELECT COUNT(*)
                    FROM practice.orders o
                    WHERE o.user_id = u.id::text
                      AND o.created_at >= NOW() - INTERVAL '7 days'
                ) AS paper_trades_7d,

                (
                    SELECT COUNT(*)
                    FROM portfolio.holdings h
                    WHERE h.user_id = u.id::text
                ) AS holdings_count,

                (
                    SELECT MAX(o.created_at)
                    FROM practice.orders o
                    WHERE o.user_id = u.id::text
                ) AS last_paper_trade_at

            FROM auth.users u
            LEFT JOIN profile.profiles p
                ON p.user_id = u.id::text
            WHERE u.id = %s
        """

        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()

        if row is None:
            return {
                "completed_steps": [],
                "incomplete_steps": [],
            }

        (
            user_id_value,
            created_at,
            level,
            lessons_completed,
            day_streak,
            xp_total,
            kyc_verified,
            paper_trades_total,
            paper_trades_7d,
            holdings_count,
            last_paper_trade_at,
        ) = row

        completed_steps = []
        incomplete_steps = []

        # Learning
        if lessons_completed and lessons_completed > 0:
            completed_steps.append(
                {
                    "step": "learning",
                    "lessons_completed": lessons_completed,
                }
            )
        else:
            incomplete_steps.append(
                {
                    "step": "learning",
                    "status": "not_started",
                }
            )

        # KYC
        if kyc_verified:
            completed_steps.append(
                {
                    "step": "kyc",
                    "status": "completed",
                }
            )
        else:
            incomplete_steps.append(
                {
                    "step": "kyc",
                    "status": "pending",
                }
            )

        # Paper trading
        if paper_trades_total and paper_trades_total > 0:
            completed_steps.append(
                {
                    "step": "paper_trading",
                    "paper_trades_total": paper_trades_total,
                }
            )

            if paper_trades_7d == 0:
                incomplete_steps.append(
                    {
                        "step": "paper_trading",
                        "status": "inactive_last_7_days",
                    }
                )
        else:
            incomplete_steps.append(
                {
                    "step": "paper_trading",
                    "status": "not_started",
                }
            )

        # Real investment
        if holdings_count and holdings_count > 0:
            completed_steps.append(
                {
                    "step": "real_investment",
                    "holdings_count": holdings_count,
                }
            )
        else:
            incomplete_steps.append(
                {
                    "step": "real_investment",
                    "status": "not_started",
                }
            )

        return {
            "user_id": str(user_id_value),
            "completed_steps": completed_steps,
            "incomplete_steps": incomplete_steps,
            "profile": {
                "level": level,
                "lessons_completed": lessons_completed or 0,
                "day_streak": day_streak or 0,
                "xp_total": xp_total or 0,
                "kyc_verified": bool(kyc_verified),
            },
            "activity": {
                "paper_trades_total": paper_trades_total or 0,
                "paper_trades_7d": paper_trades_7d or 0,
                "holdings_count": holdings_count or 0,
                "last_paper_trade_at": last_paper_trade_at,
                "registered_at": created_at,
            },
        }