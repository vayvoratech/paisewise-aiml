# PaiseWise Market Data

import requests


def fetch_nifty50_data():

    url = "https://www.niftyindices.com/indices/equity/broad-based-indices/nifty--50"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    # --------------------------------------------------
    # NOTE:
    # The NIFTY website is primarily a webpage.
    # This function is kept separate so the market-data
    # source can easily be replaced with a proper
    # market-data API later.
    # --------------------------------------------------

    return response


def get_nifty_change():

    """
    Returns NIFTY 50 percentage change.

    Temporary fallback value is used if the
    external market-data source cannot be parsed.
    """

    try:

        response = fetch_nifty50_data()

        # --------------------------------------------------
        # TODO:
        # Parse the current NIFTY value and percentage
        # change from the selected market-data source.
        # --------------------------------------------------

        # Temporary value until a structured
        # market-data API is connected.

        nifty_change = 0.75

        return round(
            nifty_change,
            2
        )

    except Exception as e:

        print(
            f"NIFTY data fetch failed: {e}"
        )

        return 0.0