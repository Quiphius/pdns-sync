class Record:
    def __init__(self, data, prio, ttl):
        self.data = data
        self.prio = prio
        self.ttl = ttl
        self.used = False
