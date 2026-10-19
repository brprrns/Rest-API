class FakeResults(list):
    """Looks like PynamoDB's result iterator: iterable + last_evaluated_key."""

    def __init__(self, items=(), last_evaluated_key=None):
        super().__init__(items)
        self.last_evaluated_key = last_evaluated_key
