from database.database import get_db_connection


# In-memory catalogue
fund_catalogue = []


def load_catalogue():
    """
    Load all active funds from database
    """

    global fund_catalogue

    query = """
        SELECT
            s.id,
            s.scheme_name,
            s.category,
            s.risk_level,
            s.expense_ratio,
            s.aum_crore,
            p.nav,
            p.return_1y,
            p.return_3y,
            p.return_5y,
            p.sharpe_ratio,
            p.volatility,
            p.max_drawdown
        FROM mf_schemes s
        LEFT JOIN mf_scheme_performance p
        ON s.id = p.scheme_id
        WHERE s.is_active = true;
    """

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [
            "id",
            "scheme_name",
            "category",
            "risk_level",
            "expense_ratio",
            "aum_crore",
            "nav",
            "return_1y",
            "return_3y",
            "return_5y",
            "sharpe_ratio",
            "volatility",
            "max_drawdown"
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
    """
    Return loaded funds
    """

    return fund_catalogue



def refresh_catalogue():
    """
    Refresh catalogue every 4 hours
    """

    print("Refreshing fund catalogue...")
    load_catalogue()