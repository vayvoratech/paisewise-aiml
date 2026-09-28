from decimal import Decimal

import pytest

from app.services.amfi_scheme_details_provider import (
    AMFISchemeDetailsProvider,
)


def test_normalize_complete_scheme_details():
    record = AMFISchemeDetailsProvider.normalize(
        scheme_code="100001",
        scheme_name="Sample Equity Fund",
        isin="INF000000001",
        amc_name="Sample AMC",
        category="Equity",
        sub_category="Large Cap",
        min_sip_amount="100",
        min_lumpsum="1000",
        returns_1y="10.50",
        returns_3y="12.25",
        returns_5y="14.10",
        expense_ratio="1.20",
        fund_manager="Sample Manager",
        fund_size_cr="5000",
        is_tax_saver="false",
        lock_in_years=None,
    )

    assert record.scheme_code == "100001"
    assert record.scheme_name == "Sample Equity Fund"
    assert record.isin == "INF000000001"
    assert record.amc_name == "Sample AMC"

    assert record.category == "Equity"
    assert record.sub_category == "Large Cap"

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


def test_missing_optional_values_become_none():
    record = AMFISchemeDetailsProvider.normalize(
        scheme_code="100002",
        scheme_name="Sample Fund",
        isin="-",
        amc_name="Sample AMC",
        category="-",
        sub_category="NA",
        min_sip_amount="-",
        min_lumpsum="",
        returns_1y=None,
        returns_3y="N/A",
        returns_5y="-",
        expense_ratio=None,
        fund_manager="-",
        fund_size_cr="NA",
        is_tax_saver=False,
        lock_in_years=None,
    )

    assert record.isin is None
    assert record.category is None
    assert record.sub_category is None

    assert record.min_sip_amount is None
    assert record.min_lumpsum is None
    assert record.returns_1y is None
    assert record.returns_3y is None
    assert record.returns_5y is None
    assert record.expense_ratio is None
    assert record.fund_manager is None
    assert record.fund_size_cr is None
    assert record.lock_in_years is None


def test_boolean_values_are_normalized():
    true_values = [
        "true",
        "TRUE",
        "yes",
        "Y",
        "1",
    ]

    for value in true_values:
        assert (
            AMFISchemeDetailsProvider._boolean(value)
            is True
        )

    false_values = [
        "false",
        "FALSE",
        "no",
        "N",
        "0",
    ]

    for value in false_values:
        assert (
            AMFISchemeDetailsProvider._boolean(value)
            is False
        )


def test_invalid_boolean_is_rejected():
    with pytest.raises(
        ValueError,
        match="Invalid boolean",
    ):
        AMFISchemeDetailsProvider._boolean(
            "maybe"
        )


def test_invalid_decimal_is_rejected():
    with pytest.raises(
        ValueError,
        match="Invalid decimal",
    ):
        AMFISchemeDetailsProvider._decimal_or_none(
            "not-a-number"
        )


def test_empty_scheme_code_is_rejected():
    with pytest.raises(
        ValueError,
        match="scheme_code is required",
    ):
        AMFISchemeDetailsProvider.normalize(
            scheme_code="",
            scheme_name="Sample Fund",
            isin=None,
            amc_name="Sample AMC",
        )


def test_empty_scheme_name_is_rejected():
    with pytest.raises(
        ValueError,
        match="scheme_name is required",
    ):
        AMFISchemeDetailsProvider.normalize(
            scheme_code="100001",
            scheme_name="",
            isin=None,
            amc_name="Sample AMC",
        )


def test_empty_amc_name_is_rejected():
    with pytest.raises(
        ValueError,
        match="amc_name is required",
    ):
        AMFISchemeDetailsProvider.normalize(
            scheme_code="100001",
            scheme_name="Sample Fund",
            isin=None,
            amc_name="",
        )


def test_decimal_values_accept_decimal_objects():
    record = AMFISchemeDetailsProvider.normalize(
        scheme_code="100003",
        scheme_name="Sample Fund",
        isin="INF000000003",
        amc_name="Sample AMC",
        min_sip_amount=Decimal("500"),
        expense_ratio=Decimal("0.75"),
        fund_size_cr=Decimal("12500.50"),
    )

    assert record.min_sip_amount == Decimal("500")
    assert record.expense_ratio == Decimal("0.75")
    assert record.fund_size_cr == Decimal("12500.50")


def test_parse_real_amfi_csv_format():
    content = """AMC,Code,Scheme Name,Scheme Type,Scheme Category,Scheme NAV Name,Scheme Minimum Amount,Launch Date, Closure Date,ISIN Div Payout/ ISIN GrowthISIN Div Reinvestment
Aditya Birla Sun Life AMC Limited,100033,Aditya Birla Sun Life Large & Mid Cap Fund,Open Ended,Equity Scheme - Large & Mid Cap Fund,Aditya Birla Sun Life Large & Mid Cap Fund - Regular Growth,5000,24-Feb-1995,24-Feb-1995,INF209K01165
"""

    records = AMFISchemeDetailsProvider.parse_csv(
        content
    )

    assert len(records) == 1

    record = records[0]

    assert record.scheme_code == "100033"
    assert (
        record.amc_name
        == "Aditya Birla Sun Life AMC Limited"
    )
    assert (
        record.scheme_name
        == "Aditya Birla Sun Life Large & Mid Cap Fund"
    )
    assert record.scheme_type == "Open Ended"
    assert (
        record.category
        == "Equity Scheme - Large & Mid Cap Fund"
    )
    assert record.min_lumpsum == Decimal("5000")
    assert record.isin == "INF209K01165"

    # AMFI Scheme Data Download does not provide
    # these fields, so they must remain unset.
    assert record.returns_1y is None
    assert record.returns_3y is None
    assert record.returns_5y is None
    assert record.expense_ratio is None
    assert record.fund_manager is None
    assert record.fund_size_cr is None
    assert record.lock_in_years is None


def test_parse_amfi_csv_extracts_primary_isin():
    content = """AMC,Code,Scheme Name,Scheme Type,Scheme Category,Scheme NAV Name,Scheme Minimum Amount,Launch Date, Closure Date,ISIN Div Payout/ ISIN GrowthISIN Div Reinvestment
Aditya Birla Sun Life AMC Limited,100034,Aditya Birla Sun Life Large & Mid Cap Fund,Open Ended,Equity Scheme - Large & Mid Cap Fund,Aditya Birla Sun Life Large & Mid Cap Fund - Regular IDCW,5000,24-Feb-1995,24-Feb-1995,INF209K01157INF209K01CE5
"""

    records = AMFISchemeDetailsProvider.parse_csv(
        content
    )

    assert len(records) == 1
    assert records[0].scheme_code == "100034"
    assert records[0].isin == "INF209K01157"


def test_parse_amfi_csv_multiple_records():
    content = """AMC,Code,Scheme Name,Scheme Type,Scheme Category,Scheme NAV Name,Scheme Minimum Amount,Launch Date, Closure Date,ISIN Div Payout/ ISIN GrowthISIN Div Reinvestment
AMC One,100001,Fund One,Open Ended,Equity Scheme - Large Cap Fund,Fund One - Growth,500,01-Jan-2000,01-Jan-2000,INF000000001
AMC Two,100002,Fund Two,Open Ended,Debt Scheme - Banking and PSU Fund,Fund Two - Growth,1000,01-Jan-2001,01-Jan-2001,INF000000002
AMC Three,100003,Fund Three,Close Ended,Equity Scheme - ELSS,Fund Three - Growth,5000,01-Jan-2002,01-Jan-2002,INF000000003
"""

    records = AMFISchemeDetailsProvider.parse_csv(
        content
    )

    assert len(records) == 3

    assert [
        record.scheme_code
        for record in records
    ] == [
        "100001",
        "100002",
        "100003",
    ]


def test_parse_amfi_csv_skips_invalid_rows():
    content = """AMC,Code,Scheme Name,Scheme Type,Scheme Category,Scheme NAV Name,Scheme Minimum Amount,Launch Date, Closure Date,ISIN Div Payout/ ISIN GrowthISIN Div Reinvestment
AMC One,100001,Valid Fund,Open Ended,Equity Scheme - Large Cap Fund,Valid Fund - Growth,500,01-Jan-2000,01-Jan-2000,INF000000001
AMC Two,,Missing Code,Open Ended,Debt Scheme,Missing Code - Growth,1000,01-Jan-2001,01-Jan-2001,INF000000002
AMC Three,ABC,Invalid Code,Open Ended,Equity Scheme,Invalid Code - Growth,1000,01-Jan-2002,01-Jan-2002,INF000000003
,100004,Missing AMC,Open Ended,Equity Scheme,Missing AMC - Growth,1000,01-Jan-2003,01-Jan-2003,INF000000004
"""

    records = AMFISchemeDetailsProvider.parse_csv(
        content
    )

    assert len(records) == 1
    assert records[0].scheme_code == "100001"


def test_parse_empty_amfi_csv():
    records = AMFISchemeDetailsProvider.parse_csv(
        ""
    )

    assert records == []


def test_parse_amfi_csv_requires_expected_columns():
    content = """AMC,Code,Scheme Name
AMC One,100001,Sample Fund
"""

    with pytest.raises(
        ValueError,
        match="Missing required AMFI CSV columns",
    ):
        AMFISchemeDetailsProvider.parse_csv(
            content
        )


def test_parse_csv_rejects_non_string_content():
    with pytest.raises(
        TypeError,
        match="content must be a string",
    ):
        AMFISchemeDetailsProvider.parse_csv(None)