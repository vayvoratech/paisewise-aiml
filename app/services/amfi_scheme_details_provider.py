from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from io import StringIO


@dataclass(frozen=True)
class AMFISchemeDetailsRecord:
    scheme_code: str
    scheme_name: str
    isin: str | None
    amc_name: str
    category: str | None
    sub_category: str | None
    scheme_type: str | None
    min_sip_amount: Decimal | None
    min_lumpsum: Decimal | None
    returns_1y: Decimal | None
    returns_3y: Decimal | None
    returns_5y: Decimal | None
    expense_ratio: Decimal | None
    fund_manager: str | None
    fund_size_cr: Decimal | None
    is_tax_saver: bool
    lock_in_years: Decimal | None


class AMFISchemeDetailsProvider:
    """
    Normalizes mutual-fund master data before it is persisted
    into the official mf_schemes table.

    Supports the real AMFI Scheme Data Download CSV format.

    No synthetic business values are generated here.
    Fields not supplied by the AMFI source remain None/default.
    """

    @staticmethod
    def _decimal_or_none(value: object) -> Decimal | None:
        if value is None:
            return None

        if isinstance(value, Decimal):
            return value

        text = str(value).strip()

        if not text or text.upper() in {"-", "NA", "N/A"}:
            return None

        try:
            return Decimal(text)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError(
                f"Invalid decimal value: {value}"
            ) from exc

    @staticmethod
    def _text_or_none(value: object) -> str | None:
        if value is None:
            return None

        text = str(value).strip()

        if not text or text.upper() in {"-", "NA", "N/A"}:
            return None

        return text

    @staticmethod
    def _boolean(value: object) -> bool:
        if isinstance(value, bool):
            return value

        if value is None:
            return False

        normalized = str(value).strip().lower()

        if normalized in {
            "true",
            "1",
            "yes",
            "y",
            "t",
        }:
            return True

        if normalized in {
            "false",
            "0",
            "no",
            "n",
            "f",
        }:
            return False

        raise ValueError(
            f"Invalid boolean value: {value}"
        )

    @classmethod
    def normalize(
        cls,
        *,
        scheme_code: object,
        scheme_name: object,
        isin: object,
        amc_name: object,
        category: object = None,
        sub_category: object = None,
        scheme_type: object = None,
        min_sip_amount: object = None,
        min_lumpsum: object = None,
        returns_1y: object = None,
        returns_3y: object = None,
        returns_5y: object = None,
        expense_ratio: object = None,
        fund_manager: object = None,
        fund_size_cr: object = None,
        is_tax_saver: object = False,
        lock_in_years: object = None,
    ) -> AMFISchemeDetailsRecord:
        normalized_scheme_code = str(
            scheme_code
        ).strip()

        normalized_scheme_name = str(
            scheme_name
        ).strip()

        normalized_amc_name = str(
            amc_name
        ).strip()

        if not normalized_scheme_code:
            raise ValueError(
                "scheme_code is required"
            )

        if not normalized_scheme_name:
            raise ValueError(
                "scheme_name is required"
            )

        if not normalized_amc_name:
            raise ValueError(
                "amc_name is required"
            )

        normalized_scheme_type = (
            cls._text_or_none(scheme_type)
        )

        if normalized_scheme_type is not None:
            allowed_scheme_types = {
                "Open Ended",
                "Close Ended",
                "Interval",
            }

            if normalized_scheme_type not in allowed_scheme_types:
                raise ValueError(
                    f"Invalid scheme_type: "
                    f"{normalized_scheme_type}"
                )

        return AMFISchemeDetailsRecord(
            scheme_code=normalized_scheme_code,
            scheme_name=normalized_scheme_name,
            isin=cls._text_or_none(isin),
            amc_name=normalized_amc_name,
            category=cls._text_or_none(category),
            sub_category=cls._text_or_none(
                sub_category
            ),
            scheme_type=normalized_scheme_type,
            min_sip_amount=cls._decimal_or_none(
                min_sip_amount
            ),
            min_lumpsum=cls._decimal_or_none(
                min_lumpsum
            ),
            returns_1y=cls._decimal_or_none(
                returns_1y
            ),
            returns_3y=cls._decimal_or_none(
                returns_3y
            ),
            returns_5y=cls._decimal_or_none(
                returns_5y
            ),
            expense_ratio=cls._decimal_or_none(
                expense_ratio
            ),
            fund_manager=cls._text_or_none(
                fund_manager
            ),
            fund_size_cr=cls._decimal_or_none(
                fund_size_cr
            ),
            is_tax_saver=cls._boolean(
                is_tax_saver
            ),
            lock_in_years=cls._decimal_or_none(
                lock_in_years
            ),
        )

    @classmethod
    def parse_csv(
        cls,
        content: str,
    ) -> list[AMFISchemeDetailsRecord]:
        """
        Parse the real AMFI Scheme Data Download CSV.

        Expected columns include:

            AMC
            Code
            Scheme Name
            Scheme Type
            Scheme Category
            Scheme NAV Name
            Scheme Minimum Amount
            Launch Date
            Closure Date
            ISIN Div Payout/ ISIN GrowthISIN Div Reinvestment

        Only values actually supplied by this source are mapped.

        Unsupported business fields remain None.
        """

        if not isinstance(content, str):
            raise TypeError(
                "content must be a string"
            )

        if not content.strip():
            return []

        reader = csv.DictReader(
            StringIO(content),
            skipinitialspace=True,
        )

        if reader.fieldnames is None:
            return []

        normalized_headers = {
            header.strip().lower(): header
            for header in reader.fieldnames
            if header is not None
        }

        required_headers = {
            "amc",
            "code",
            "scheme name",
            "scheme type",
            "scheme category",
            "scheme minimum amount",
        }

        missing_headers = [
            header
            for header in required_headers
            if header not in normalized_headers
        ]

        if missing_headers:
            raise ValueError(
                "Missing required AMFI CSV columns: "
                + ", ".join(
                    sorted(missing_headers)
                )
            )

        def get_value(
            row: dict[str, str | None],
            header: str,
        ) -> str | None:
            actual_header = (
                normalized_headers.get(header)
            )

            if actual_header is None:
                return None

            value = row.get(actual_header)

            if value is None:
                return None

            return value.strip()

        # AMFI currently exposes the growth/dividend
        # ISIN values under a combined header.
        #
        # Example:
        #
        # ISIN Div Payout/ ISIN GrowthISIN Div Reinvestment
        #
        # We intentionally identify it by prefix instead
        # of relying on an exact header string.
        isin_header: str | None = None

        for (
            normalized_header,
            actual_header,
        ) in normalized_headers.items():
            if normalized_header.startswith(
                "isin div payout/ isin growth"
            ):
                isin_header = actual_header
                break

        records: list[
            AMFISchemeDetailsRecord
        ] = []

        for row in reader:
            scheme_code = get_value(
                row,
                "code",
            )

            scheme_name = get_value(
                row,
                "scheme name",
            )

            amc_name = get_value(
                row,
                "amc",
            )

            # Skip malformed rows.
            if (
                not scheme_code
                or not scheme_name
                or not amc_name
            ):
                continue

            # AMFI scheme codes are numeric.
            if not scheme_code.isdigit():
                continue

            scheme_type = get_value(
                row,
                "scheme type",
            )

            category = get_value(
                row,
                "scheme category",
            )

            minimum_amount = get_value(
                row,
                "scheme minimum amount",
            )

            combined_isin = None

            if isin_header is not None:
                combined_isin = row.get(
                    isin_header
                )

                if combined_isin is not None:
                    combined_isin = (
                        combined_isin.strip()
                    )

            isin = cls._extract_primary_isin(
                combined_isin
            )

            try:
                record = cls.normalize(
                    scheme_code=scheme_code,
                    scheme_name=scheme_name,
                    isin=isin,
                    amc_name=amc_name,
                    category=category,
                    scheme_type=scheme_type,
                    min_lumpsum=minimum_amount,
                )
            except ValueError:
                # Ignore malformed source records
                # without blocking the complete
                # AMFI import.
                continue

            records.append(record)

        return records

    @staticmethod
    def _extract_primary_isin(
        value: str | None,
    ) -> str | None:
        """
        Extract the first valid 12-character Indian ISIN.

        AMFI may provide:

            INF209K01165

        or:

            INF209K01WL2INF209K01WM0
        """

        if value is None:
            return None

        normalized = value.strip()

        if not normalized or normalized.upper() in {
            "-",
            "NA",
            "N/A",
        }:
            return None

        for index in range(
            0,
            max(0, len(normalized) - 11),
        ):
            candidate = normalized[
                index:index + 12
            ]

            if (
                len(candidate) == 12
                and candidate[:2].upper() == "IN"
                and candidate[2:].isalnum()
            ):
                return candidate

        return None