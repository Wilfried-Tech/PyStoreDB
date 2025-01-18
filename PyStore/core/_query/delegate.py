from PyStore.engines import PyStoreEngine


class QueryDelegate:

    def __init__(self, path: str, engine: PyStoreEngine, **kwargs):
        self.path = path
        self.engine = engine
        self.parameters = kwargs

    def get(self, path: str):
        return QueryDelegate(path, self.engine, **self.parameters)

    def limit(self, limit):
        return QueryDelegate(self.path, self.engine, **{**self.parameters, 'limit': limit})

    def order_by(self, orders: list[tuple[str, bool]]):
        return QueryDelegate(self.path, self.engine, **{**self.parameters, 'order_by': orders})

    def limit_to_last(self, limit):
        return QueryDelegate(self.path, self.engine, **{**self.parameters, 'limit_to_last': limit})
