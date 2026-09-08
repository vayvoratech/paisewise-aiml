from app.utils.batching import batch_items


def test_ten_test_users_are_processed_without_database_rows():
    
    users = [f"test-user-{index}" for index in range(10)]

    batches = list(batch_items(users, 50))

    assert len(batches) == 1
    assert batches[0] == users
