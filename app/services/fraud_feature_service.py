from typing import Any


class FraudFeatureService:
    FEATURE_NAMES = (
        "shares",
        "price_per_share",
        "total_amount",
        "side_buy",
        "side_sell",
        "order_type_market",
        "order_type_limit",
    )

    @classmethod
    def extract_features(
        cls,
        order: dict[str, Any],
    ) -> list[float]:
        required_fields = (
            "shares",
            "price_per_share",
            "total_amount",
            "side",
            "order_type",
        )

        missing_fields = [
            field
            for field in required_fields
            if field not in order
        ]

        if missing_fields:
            raise ValueError(
                f"Missing required order fields: {missing_fields}"
            )

        shares = order["shares"]
        price_per_share = order["price_per_share"]
        total_amount = order["total_amount"]

        if not isinstance(shares, (int, float)):
            raise TypeError("shares must be numeric")

        if not isinstance(price_per_share, (int, float)):
            raise TypeError("price_per_share must be numeric")

        if not isinstance(total_amount, (int, float)):
            raise TypeError("total_amount must be numeric")

        if shares <= 0:
            raise ValueError(
                "shares must be greater than zero"
            )

        if price_per_share <= 0:
            raise ValueError(
                "price_per_share must be greater than zero"
            )

        if total_amount <= 0:
            raise ValueError(
                "total_amount must be greater than zero"
            )

        side = str(order["side"]).upper()
        order_type = str(order["order_type"]).upper()

        if side not in {"BUY", "SELL"}:
            raise ValueError(
                f"Unsupported order side: {side}"
            )

        if order_type not in {"MARKET", "LIMIT"}:
            raise ValueError(
                f"Unsupported order type: {order_type}"
            )

        return [
            float(shares),
            float(price_per_share),
            float(total_amount),
            1.0 if side == "BUY" else 0.0,
            1.0 if side == "SELL" else 0.0,
            1.0 if order_type == "MARKET" else 0.0,
            1.0 if order_type == "LIMIT" else 0.0,
        ]