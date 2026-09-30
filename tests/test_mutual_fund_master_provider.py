from datetime import date
from decimal import Decimal

from app.services.mutual_fund_master_provider import MutualFundMasterRecord


def test_mutual_fund_master_record():
    record = MutualFundMasterRecord(
        scheme_code="100001",
        scheme_name="Sample Fund",
        isin="INF000000001",
        amc_name="Sample AMC",
        category="Equity",
        sub_category="Large Cap",
        nav=Decimal("125.45"),
        nav_date=date(2026, 9, 21),
        min_sip_amount=Decimal("100"),
        min_lumpsum=Decimal("1000"),
        returns_1y=Decimal("10.50"),
        returns_3y=Decimal("12.25"),
        returns_5y=Decimal("14.10"),
        expense_ratio=Decimal("1.20"),
        fund_manager="Sample Manager",
        fund_size_cr=Decimal("5000"),
        is_tax_saver=False,
        lock_in_years=None,
    )

    assert record.scheme_code == "100001"
    assert record.scheme_name == "Sample Fund"
    assert record.isin == "INF000000001"
    assert record.amc_name == "Sample AMC"
    assert record.category == "Equity"
    assert record.sub_category == "Large Cap"
    assert record.nav == Decimal("125.45")
    assert record.nav_date == date(2026, 9, 21)
    assert record.min_sip_amount == Decimal("100")
    assert record.min_lumpsum == Decimal("1000")
    assert record.returns_1y == Decimal("10.50")
    assert record.returns_3y == Decimal("12.25")
    assert record.returns_5y == Decimal("14.10")
    assert record.expense_ratio == Decimal("1.20")
    assert record.fund_manager == "Sample Manager"
    assert record.fund_size_cr == Decimal("5000")
    assert record.is_tax_saver is False
    assert record.lock_in_years is None