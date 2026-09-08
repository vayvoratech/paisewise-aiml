import pandas as pd

"""Check for null values."""
def check_nulls(df):
    return df.isnull().sum()


"""Count duplicate rows."""
def check_duplicates(df):
    return df.duplicated().sum()


def validate_income(df):
    return df[df["annual_income"] < 0]


def validate_age(df):
    return df[(df["age"] < 18) | (df["age"] > 100)]


def validate_risk_profile(df):
    
    valid = ["Low", "Moderate", "High"]
    return df[~df["risk_profile"].isin(valid)]


def validate_data_types(df):

    errors = {}

    if not pd.api.types.is_numeric_dtype(df["age"]):
        errors["age"] = "Invalid data type"

    if not pd.api.types.is_numeric_dtype(df["annual_income"]):
        errors["annual_income"] = "Invalid data type"

    if not pd.api.types.is_string_dtype(df["risk_profile"]):
        errors["risk_profile"] = "Invalid data type"

    return errors