from database.database import get_db_connection

# In-memory catalogue
fund_catalogue = []


def load_catalogue():
   

    global fund_catalogue

    query = """
        SELECT
            scheme_code,
            scheme_name,
            category,
            risk_level,
            nav,
            returns_1y,
            returns_3y,
            returns_5y,
            expense_ratio,
            fund_size_cr
        FROM public.mf_schemes
        WHERE is_active = true;
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [
            "scheme_code",
            "scheme_name",
            "category",
            "risk_level",
            "nav",
            "return_1y",
            "return_3y",
            "return_5y",
            "expense_ratio",
            "aum_crore",
        ]

        fund_catalogue = [
            dict(zip(columns, row))
            for row in rows
        ]

        print(
            f"Fund catalogue loaded: {len(fund_catalogue)} funds"
        )

    finally:
        cursor.close()
        connection.close()


def get_catalogue():
    return fund_catalogue


def refresh_catalogue():
    print("Refreshing fund catalogue...")
    load_catalogue()