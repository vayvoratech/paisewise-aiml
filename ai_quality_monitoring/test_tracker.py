from quality_tracker import QualityTracker


tracker = QualityTracker()


record1 = tracker.create_record(
    feature="jargon",
    score=4.5,
    user_id="U001"
)

record2 = tracker.create_record(
    feature="portfolio",
    score=3.8,
    user_id="U002"
)

record3 = tracker.create_record(
    feature="market_context",
    score=3.2,
    user_id="U003"
)


records = [
    record1,
    record2,
    record3
]


print("Quality Records:")
print(records)

print("\nAverage Quality Score:")
print(tracker.average_score(records))

print("\nQuality by Feature:")
print(tracker.feature_scores(records))