import pandas as pd

# Sample historical user data

data = {
    "user_id": ["U001", "U002", "U003", "U004"],
    "day_7_opens": [5, 7, 2, 6],
    "day_14_opens": [2, 5, 0, 4],
    "day_30_opens": [0, 4, 0, 3],
    "churn_status": [
        "Churned",
        "Retained",
        "Churned",
        "Retained"
    ]
}

df = pd.DataFrame(data)

print(df)