from __future__ import annotations

from typing import Any


class FundRecommendationAuditService:
    """
    Analyzes monthly recommendation exposure by AMC.

    This service does not label an AMC as biased based only on raw
    exposure counts. It reports concentration metrics and identifies
    records that exceed the configured concentration threshold.
    """

    def audit_month(
        self,
        amc_exposure: list[dict[str, Any]],
        *,
        concentration_threshold: float,
    ) -> dict[str, Any]:
        """
        Audit AMC recommendation concentration for one period.

        `amc_exposure` is expected to contain:
            amc_name
            exposure_count
            unique_user_count
            unique_scheme_count

        The threshold represents the maximum allowed share of total
        recommendation exposures for one AMC.
        """

        if not 0.0 < concentration_threshold <= 1.0:
            raise ValueError(
                "concentration_threshold must be greater than "
                "zero and less than or equal to one"
            )

        if not amc_exposure:
            return {
                "total_exposures": 0,
                "amc_count": 0,
                "audited": False,
                "flagged_amcs": [],
                "amc_results": [],
            }

        normalized: list[dict[str, Any]] = []

        total_exposures = 0

        for record in amc_exposure:
            amc_name = record.get("amc_name")

            if not amc_name or not str(amc_name).strip():
                raise ValueError(
                    "AMC exposure record is missing amc_name"
                )

            exposure_count = self._non_negative_int(
                record.get("exposure_count")
            )

            unique_user_count = self._non_negative_int(
                record.get("unique_user_count")
            )

            unique_scheme_count = self._non_negative_int(
                record.get("unique_scheme_count")
            )

            normalized.append(
                {
                    "amc_name": str(amc_name).strip(),
                    "exposure_count": exposure_count,
                    "unique_user_count": unique_user_count,
                    "unique_scheme_count": unique_scheme_count,
                }
            )

            total_exposures += exposure_count

        if total_exposures == 0:
            return {
                "total_exposures": 0,
                "amc_count": len(normalized),
                "audited": False,
                "flagged_amcs": [],
                "amc_results": [
                    {
                        **record,
                        "exposure_share": 0.0,
                        "concentration_flag": False,
                    }
                    for record in normalized
                ],
            }

        results: list[dict[str, Any]] = []
        flagged_amcs: list[str] = []

        for record in normalized:
            exposure_share = (
                record["exposure_count"]
                / total_exposures
            )

            concentration_flag = (
                exposure_share
                > concentration_threshold
            )

            result = {
                **record,
                "exposure_share": round(
                    exposure_share,
                    6,
                ),
                "concentration_flag": concentration_flag,
            }

            results.append(result)

            if concentration_flag:
                flagged_amcs.append(
                    record["amc_name"]
                )

        results.sort(
            key=lambda item: (
                -item["exposure_share"],
                item["amc_name"],
            )
        )

        return {
            "total_exposures": total_exposures,
            "amc_count": len(normalized),
            "audited": True,
            "flagged_amcs": flagged_amcs,
            "amc_results": results,
        }

    @staticmethod
    def _non_negative_int(value: Any) -> int:
        if value is None:
            return 0

        try:
            number = int(value)
        except (TypeError, ValueError):
            return 0

        return max(0, number)