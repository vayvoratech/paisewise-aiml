from datetime import datetime

# Last time the user opened the PaiseWise app
last_app_open = "2026-08-01"

# Convert the date into a datetime object
last_open_date = datetime.strptime(
    last_app_open,
    "%Y-%m-%d"
)

# Today's date
today = datetime.today()

# Calculate inactive days
inactive_days = (today - last_open_date).days

print("Inactive days:", inactive_days)

# Churn condition
if inactive_days >= 14:
    print("User Status: CHURNED")
else:
    print("User Status: ACTIVE")