from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class AMFINAVRecord:
    scheme_code: str
    scheme_name: str
    isin_growth: str | None
    isin_div_reinvestment: str | None
    nav: Decimal
    nav_date: date


class AMFINAVProvider:
    """
    Fetches and parses AMFI NAV data.

    Supported formats:

    1. Current AMFI format:

       Scheme Code;
       ISIN Div Payout/ISIN Growth;
       ISIN Div Reinvestment;
       Scheme Name;
       Plan;
       Option;
       Net Asset Value;
       Date

       Example:
       135761;INF846K01WN3;INF846K01WL7;Axis Children's Fund;
       Regular Plan;IDCW Option;23.9799;22-Sep-2026

    2. Older 6-field format:

       Scheme Code;
       ISIN Div Payout/ISIN Growth;
       ISIN Div Reinvestment;
       Scheme Name;
       Net Asset Value;
       Date
    """

    DATE_FORMATS = (
        "%d-%b-%Y",
        "%d-%m-%Y",
        "%d/%m/%Y",
    )

    @classmethod
    def _normalize_isin(cls, value: str | None) -> str | None:
        """
        Normalize an ISIN value.

        Empty values and AMFI placeholders are converted to None.
        """
        if value is None:
            return None

        normalized = value.strip()

        if not normalized or normalized.upper() in {
            "-",
            "NA",
            "N/A",
            "NIL",
        }:
            return None

        return normalized

    @classmethod
    def _parse_decimal(cls, value: str) -> Decimal | None:
        """
        Convert a string to Decimal.

        Invalid or missing numeric values return None.
        """
        normalized = value.strip()

        if not normalized or normalized.upper() in {
            "-",
            "NA",
            "N/A",
            "NIL",
        }:
            return None

        try:
            return Decimal(normalized)
        except (InvalidOperation, ValueError):
            return None

    @classmethod
    def _parse_date(cls, value: str) -> date | None:
        """
        Parse AMFI-supported date formats.
        """
        normalized = value.strip()

        if not normalized or normalized.upper() in {
            "-",
            "NA",
            "N/A",
            "NIL",
        }:
            return None

        for date_format in cls.DATE_FORMATS:
            try:
                return datetime.strptime(
                    normalized,
                    date_format,
                ).date()
            except ValueError:
                continue

        return None

    @classmethod
    def parse(cls, content: str) -> list[AMFINAVRecord]:
        """
        Parse AMFI semicolon-delimited NAV content.

        Invalid, header, category, and malformed rows are skipped.

        Raises:
            TypeError:
                If content is not a string.
        """
        if not isinstance(content, str):
            raise TypeError("content must be a string")

        records: list[AMFINAVRecord] = []

        if not content:
            return records

        for raw_line in content.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            parts = [part.strip() for part in line.split(";")]

            # ---------------------------------------------------------
            # Current AMFI format
            #
            # 0 = Scheme Code
            # 1 = ISIN Growth
            # 2 = ISIN Dividend/Reinvestment
            # 3 = Scheme Name
            # 4 = Plan
            # 5 = Option
            # 6 = NAV
            # 7 = NAV Date
            # ---------------------------------------------------------
            if len(parts) >= 8:
                scheme_code = parts[0]
                isin_growth = cls._normalize_isin(parts[1])
                isin_div_reinvestment = cls._normalize_isin(parts[2])
                scheme_name = parts[3]
                nav_value = parts[6]
                nav_date_value = parts[7]

            # ---------------------------------------------------------
            # Older AMFI format
            #
            # 0 = Scheme Code
            # 1 = ISIN Growth
            # 2 = ISIN Dividend/Reinvestment
            # 3 = Scheme Name
            # 4 = NAV
            # 5 = NAV Date
            # ---------------------------------------------------------
            elif len(parts) >= 6:
                scheme_code = parts[0]
                isin_growth = cls._normalize_isin(parts[1])
                isin_div_reinvestment = cls._normalize_isin(parts[2])
                scheme_name = parts[3]
                nav_value = parts[4]
                nav_date_value = parts[5]

            else:
                # Ignore short/malformed rows.
                continue

            # Ignore empty identity fields.
            if not scheme_code or not scheme_name:
                continue

            # Real AMFI scheme codes are numeric.
            #
            # This also prevents lines such as:
            # "Scheme Code;..."
            # "Open Ended Schemes(...)"
            # from being treated as funds.
            if not scheme_code.isdigit():
                continue

            nav = cls._parse_decimal(nav_value)
            nav_date = cls._parse_date(nav_date_value)

            # Invalid NAV/date rows are ignored.
            if nav is None or nav_date is None:
                continue

            # Negative NAV values are invalid.
            if nav < 0:
                continue

            records.append(
                AMFINAVRecord(
                    scheme_code=scheme_code,
                    scheme_name=scheme_name,
                    isin_growth=isin_growth,
                    isin_div_reinvestment=isin_div_reinvestment,
                    nav=nav,
                    nav_date=nav_date,
                )
            )

        return records

    @classmethod
    def fetch(
        cls,
        source_url: str,
        *,
        timeout_seconds: int = 15,
    ) -> list[AMFINAVRecord]:
        """
        Fetch AMFI NAV data from the configured source URL.

        Args:
            source_url:
                AMFI NAV download URL.

            timeout_seconds:
                HTTP request timeout.

        Returns:
            Parsed AMFI NAV records.

        Raises:
            ValueError:
                If the URL is missing or timeout is invalid.
        """
        if not source_url or not source_url.strip():
            raise ValueError("AMFI NAV source URL is required")

        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

        request = Request(
            source_url.strip(),
            headers={
                "User-Agent": "Vayvora-MutualFundCatalog/1.0",
                "Accept": "text/plain,text/*,*/*",
            },
        )

        with urlopen(
            request,
            timeout=timeout_seconds,
        ) as response:
            content = response.read().decode(
                "utf-8",
                errors="replace",
            )

        return cls.parse(content)