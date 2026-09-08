from app.schemas.what_if import (
    WhatIfHoldingProjection,
    WhatIfRequest,
    WhatIfResponse,
)
from app.services.portfolio_analytics_service import (
    PortfolioAnalyticsService,
)


class WhatIfService:
    """
    Calculates a hypothetical portfolio outcome
    by distributing an additional monthly SIP
    across the user's existing holdings.
    """

    def __init__(
        self,
        portfolio_analytics_service: (
            PortfolioAnalyticsService | None
        ) = None,
    ) -> None:
        self.portfolio_analytics_service = (
            portfolio_analytics_service
            or PortfolioAnalyticsService()
        )

    @staticmethod
    def _project_value(
        monthly_sip: float,
        months: int,
        annual_return: float,
    ) -> float:
        """
        Project the future value of monthly SIP
        contributions assuming contributions are made
        at the end of each month.
        """
        monthly_rate = (
            (1 + annual_return / 100) ** (1 / 12)
        ) - 1

        if monthly_rate == 0:
            return monthly_sip * months

        return monthly_sip * (
            ((1 + monthly_rate) ** months - 1)
            / monthly_rate
        )

    def calculate(
        self,
        request: WhatIfRequest,
    ) -> WhatIfResponse:
        """
        Calculate a dynamic SIP scenario using
        the user's current portfolio allocation.
        """

        if not request.userId or not request.userId.strip():
            raise ValueError(
                "userId cannot be empty"
            )

        analytics = (
            self.portfolio_analytics_service.calculate(
                user_id=request.userId.strip()
            )
        )

        existing_portfolio_value = float(
            analytics.currentValue
        )

        monthly_sip = float(request.monthlySip)
        months = int(request.months)
        annual_return = float(
            request.expectedAnnualReturn
        )

        if existing_portfolio_value <= 0:
            raise ValueError(
                "Cannot calculate SIP allocation "
                "because the portfolio has no current value"
            )

        total_additional_investment = (
            monthly_sip * months
        )

        projected_holdings = []

        for holding in analytics.holdings:
            current_value = float(
                holding.current_value
            )

            allocation_percentage = (
                current_value
                / existing_portfolio_value
                * 100
            )

            holding_monthly_sip = (
                monthly_sip
                * allocation_percentage
                / 100
            )

            holding_additional_investment = (
                holding_monthly_sip * months
            )

            projected_additional_value = (
                self._project_value(
                    monthly_sip=holding_monthly_sip,
                    months=months,
                    annual_return=annual_return,
                )
            )

            projected_holdings.append(
                WhatIfHoldingProjection(
                    symbol=holding.symbol,
                    currentValue=round(
                        current_value,
                        2,
                    ),
                    allocationPercentage=round(
                        allocation_percentage,
                        2,
                    ),
                    monthlySipAllocation=round(
                        holding_monthly_sip,
                        2,
                    ),
                    additionalInvestment=round(
                        holding_additional_investment,
                        2,
                    ),
                    projectedAdditionalValue=round(
                        projected_additional_value,
                        2,
                    ),
                )
            )

        projected_additional_value = sum(
            holding.projectedAdditionalValue
            for holding in projected_holdings
        )

        estimated_additional_gain = (
            projected_additional_value
            - total_additional_investment
        )

        projected_portfolio_value = (
            existing_portfolio_value
            + projected_additional_value
        )

        return WhatIfResponse(
            userId=request.userId.strip(),
            monthlySip=round(monthly_sip, 2),
            months=months,
            existingPortfolioValue=round(
                existing_portfolio_value,
                2,
            ),
            totalAdditionalInvestment=round(
                total_additional_investment,
                2,
            ),
            projectedAdditionalValue=round(
                projected_additional_value,
                2,
            ),
            projectedPortfolioValue=round(
                projected_portfolio_value,
                2,
            ),
            estimatedAdditionalGain=round(
                estimated_additional_gain,
                2,
            ),
            holdings=projected_holdings,
        )