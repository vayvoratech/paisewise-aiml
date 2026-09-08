def batch_items(items, batch_size):
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    for start in range(0, len(items), batch_size):
        yield items[start:start + batch_size]
