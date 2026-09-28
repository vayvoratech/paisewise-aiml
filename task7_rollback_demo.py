TOTAL_USERS = 100
ANOMALOUS_USERS = 6

THRESHOLD = 0.05

anomaly_rate = ANOMALOUS_USERS / TOTAL_USERS

print("Total users:", TOTAL_USERS)
print("Anomalous users:", ANOMALOUS_USERS)
print("Anomaly rate:", anomaly_rate * 100, "%")
print("Rollback threshold:", THRESHOLD * 100, "%")

if anomaly_rate > THRESHOLD:
    print("⚠️ Anomaly rate exceeded 5%")
    print("🔄 AUTOMATIC ROLLBACK TRIGGERED")
    print("Previous model version restored")
else:
    print("✅ Anomaly rate within acceptable limit")
    print("New model continues running")