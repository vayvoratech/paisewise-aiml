from collections import defaultdict
from math import sqrt
from typing import Any


class PortfolioDiversificationService:
    def analyze(self, holdings: list[dict[str, Any]], returns: dict[str, list[float]] | None = None, market_returns: list[float] | None = None) -> dict[str, Any]:
        if not holdings:
            return {"diversification_score": 0.0, "sector_concentration": {}, "single_stock_concentration": {}, "beta_vs_nifty": None, "max_drawdown": 0.0, "correlation_matrix": {}, "concentrated_bets": []}

        values = {str(h.get("symbol")): float(h.get("current_value") or h.get("value") or 0) for h in holdings}
        total = sum(values.values()) or 1.0
        sector_values = defaultdict(float)
        for h in holdings:
            sector_values[str(h.get("sector") or "Unknown")] += values.get(str(h.get("symbol")), 0.0)

        sector_share = {k: round(v / total, 4) for k, v in sector_values.items()}
        stock_share = {k: round(v / total, 4) for k, v in values.items()}
        max_sector = max(sector_share.values(), default=1.0)
        max_stock = max(stock_share.values(), default=1.0)
        score = round(max(0.0, min(100.0, 100 * (1 - 0.6 * max_sector - 0.4 * max_stock))), 2)
        concentrated = [k for k, v in stock_share.items() if v > 0.30]

        beta = self._beta(returns or {}, market_returns or [])
        drawdown = self._max_drawdown(returns or {})
        correlation = self._correlation(returns or {})

        return {
            "diversification_score": score,
            "sector_concentration": sector_share,
            "single_stock_concentration": stock_share,
            "beta_vs_nifty": beta,
            "max_drawdown": drawdown,
            "correlation_matrix": correlation,
            "concentrated_bets": concentrated,
        }

    def _beta(self, returns, market):
        if not market or len(market) < 2:
            return None
        import numpy as np
        common = []
        for symbol, series in returns.items():
            if len(series) == len(market):
                common.append(series)
        if not common:
            return None
        portfolio = np.mean(np.array(common, dtype=float), axis=0)
        variance = float(np.var(market))
        if variance == 0:
            return None
        return round(float(np.cov(portfolio, market, ddof=0)[0, 1] / variance), 4)

    def _max_drawdown(self, returns):
        import numpy as np
        worst = 0.0
        for series in returns.values():
            if not series:
                continue
            prices = np.cumprod([1 + float(x) for x in series])
            peak = np.maximum.accumulate(prices)
            drawdown = (prices - peak) / peak
            worst = min(worst, float(drawdown.min()))
        return round(abs(worst) * 100, 2)

    def _correlation(self, returns):
        import numpy as np
        symbols = [s for s, v in returns.items() if len(v) > 1]
        if len(symbols) < 2:
            return {}
        matrix = np.corrcoef([returns[s] for s in symbols])
        return {symbols[i]: {symbols[j]: round(float(matrix[i, j]), 4) for j in range(len(symbols))} for i in range(len(symbols))}
