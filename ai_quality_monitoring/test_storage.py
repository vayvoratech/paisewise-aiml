from quality_tracker import QualityTracker
from quality_storage import QualityStorage


tracker = QualityTracker()
storage = QualityStorage()


record = tracker.create_record(
    feature="jargon",
    score=4.5,
    user_id="U001"
)


storage.add_record(record)


records = storage.get_records()


print("Total evaluation records:")
print(len(records))

print("\nLatest record:")
print(records[-1])