from __future__ import annotations

from typing import Any


class FundRecommendationDiversityService:
    """
    Prevents repeated exposure of the same funds.

    The service is database-independent. Recent exposure history is supplied
    by RecommendationExposureRepository.
    """

    def select_diverse_funds(
        self,
        candidates: list[dict[str, Any]],
        recent_exposures: list[dict[str, Any]],
        *,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Select a diverse set of recommendations.

        Candidates are assumed to already be ordered by recommendation score.

        Previously exposed funds are skipped when enough unseen candidates
        are available. If there are not enough unseen candidates, previously
        exposed funds may be used as fallback so the response does not become
        empty unnecessarily.
        """

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

        if not candidates:
            return []

        exposed_scheme_codes = {
            str(exposure["scheme_code"]).strip()
            for exposure in recent_exposures
            if exposure.get("scheme_code")
        }

        selected: list[dict[str, Any]] = []
        selected_scheme_codes: set[str] = set()

        # First pass: prefer funds not recently exposed.
        for candidate in candidates:
            scheme_code = self._scheme_code(candidate)

            if scheme_code in selected_scheme_codes:
                continue

            if scheme_code in exposed_scheme_codes:
                continue

            selected.append(candidate)
            selected_scheme_codes.add(scheme_code)

            if len(selected) >= limit:
                return selected

        # Second pass: use previously exposed funds only if necessary.
        for candidate in candidates:
            scheme_code = self._scheme_code(candidate)

            if scheme_code in selected_scheme_codes:
                continue

            selected.append(candidate)
            selected_scheme_codes.add(scheme_code)

            if len(selected) >= limit:
                break

        return selected

    @staticmethod
    def _scheme_code(
        candidate: dict[str, Any],
    ) -> str:
        scheme_code = candidate.get("scheme_code")

        if not scheme_code or not str(scheme_code).strip():
            raise ValueError(
                "Candidate is missing scheme_code"
            )

        return str(scheme_code).strip()