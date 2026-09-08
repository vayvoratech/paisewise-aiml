TOP_TIER_AMCS = {
    "sbi mutual fund",
    "hdfc mutual fund",
    "icici prudential mutual fund",
    "nippon india mutual fund",
    "kotak mahindra mutual fund",
}

MID_TIER_AMCS = {
    "axis mutual fund",
    "aditya birla sun life mutual fund",
    "uti mutual fund",
    "dsp mutual fund",
    "tata mutual fund",
    "mirae asset mutual fund",
    "franklin templeton mutual fund",
}

AMC_REPUTATION_SCORES = {
    "top": 90,
    "mid": 70,
    "unknown": 50,
}


def get_amc_reputation_score(amc_name):
    if not amc_name:
        return AMC_REPUTATION_SCORES["unknown"]

    normalized = amc_name.strip().lower()

    if normalized in TOP_TIER_AMCS:
        return AMC_REPUTATION_SCORES["top"]

    if normalized in MID_TIER_AMCS:
        return AMC_REPUTATION_SCORES["mid"]

    return AMC_REPUTATION_SCORES["unknown"]
