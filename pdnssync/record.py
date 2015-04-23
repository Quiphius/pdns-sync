class Record(object):
    def __init__(self, data, prio, ttl):
        self.data = data
        self.prio = prio
        self.ttl = ttl
        self.used = False

    def __repr__(self):
        return self.data


class RecordList(object):
    def __init__(self):
        self.records = {}

    def add_record(self, name, rtype, data, prio, ttl):
        i = (name, rtype)
        if i not in self.records:
            self.records[i] = []
        r = Record(data, prio, ttl)
        self.records[i].append(r)

    def add_record_uniq(self, name, rtype, data, prio, ttl, force=False):
        i = (name, rtype)
        if i not in self.records or force:
            r = Record(data, prio, ttl)
            self.records[i] = [r]

    def __repr__(self):
        ret = ""
        for l in self.records:
            ret += "%s %s\n" % (l, self.records[l])
        return ret
