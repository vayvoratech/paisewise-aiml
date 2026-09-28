from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class MutualFundMasterRecord:
    scheme_code: str
    scheme_name: str
    isin: str | None
    amc_name: str
    category: str | None
    sub_category: str | None
    nav: Decimal | None
    nav_date: date | None
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