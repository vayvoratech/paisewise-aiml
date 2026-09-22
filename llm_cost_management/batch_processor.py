class BatchProcessor:

    MAX_BATCH_SIZE = 10

    def create_batches(self, users):

        batches = []

        for i in range(
            0,
            len(users),
            self.MAX_BATCH_SIZE
        ):

            batch = users[
                i:i + self.MAX_BATCH_SIZE
            ]

            batches.append(batch)

        return batches

    def process_batches(
        self,
        users,
        process_function
    ):

        batches = self.create_batches(
            users
        )

        results = []

        for batch in batches:

            result = process_function(
                batch
            )

            results.append(result)

        return results