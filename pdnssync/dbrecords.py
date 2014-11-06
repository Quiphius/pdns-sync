class DBDomain:
    def __init__(self, id, name, type):
        self.name = name
        self.id = id
        self.type = type


class DBRecord:
    def __init__(self, id, data, ttl, prio):
        self.id = id
        self.data = data
        self.ttl = ttl
        self.prio = prio
