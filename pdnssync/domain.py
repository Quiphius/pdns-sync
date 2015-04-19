import os
from datetime import datetime


class Record(object):
    def __init__(self, data, prio, ttl):
        self.data = data
        self.prio = prio
        self.ttl = ttl
        self.used = False


class Domain(object):
    def __init__(self, name, ns, email, ttl):
        self.name = name
        self.ns = ns
        self.email = email
        self.ttl = ttl
        self.records = {}
        self.updated = False
        self.serial = 0

    def gen_soa(self):
        self.soa_content = '%s %s %s 86400 7200 604800 172800' % (self.ns, self.email, self.serial)
        soa = Record(self.soa_content, 0, self.ttl)
        self.records[(self.name, 'SOA')] = [soa]

    def get_serial(self):
        if (self.name, 'SOA') in self.dbrecords:
            r = self.dbrecords[(self.name, 'SOA')][0]
            self.serial = r.data.split(' ')[2]
        self.gen_soa()

    def update_serial(self):
        d = datetime.now().strftime('%Y%m%d')
        if d == str(self.serial)[:8]:
            self.serial = str(int(self.serial) + 1)
        else:
            self.serial = d + '00'
        self.gen_soa()

    def add_record_uniq(self, name, type, data, prio, ttl, force=False):
        i = (name, type)
        if i not in self.records or force:
            r = Record(data, prio, ttl)
            self.records[i] = [r]

    def add_record(self, name, type, data, prio, ttl):
        i = (name, type)
        if i not in self.records:
            self.records[i] = []
        r = Record(data, prio, ttl)
        self.records[i].append(r)

    def sync_record(self, db, i):
        for dbr in self.dbrecords[i]:
            found = False
            for r in self.records[i]:
                if dbr.data == r.data:
                    if dbr.prio != r.prio or dbr.ttl != r.ttl:
                        db.update_record(dbr.id, r.ttl, r.prio)
                        self.updated = True
                    r.used = True
                    found = True
            if not found:
                db.delete_record(dbr.id)
                self.updated = True
        for r in self.records[i]:
            if not r.used:
                db.create_record(self.name, i[0], i[1], r.data, r.ttl, r.prio)
                self.updated = True

    def sync_domain(self, db):
        print('Syncing domain %s' % self.name)
        self.dbrecords = db.get_records(self.name)
        self.get_serial()
        record_s = set(self.records.keys())
        dbrecord_s = set(self.dbrecords.keys())
        for i in list(record_s - dbrecord_s):
            for r in self.records[i]:
                db.create_record(self.name, i[0], i[1], r.data, r.ttl, r.prio)
                self.updated = True
        for i in list(dbrecord_s - record_s):
            for r in self.dbrecords[i]:
                db.delete_record(r.id)
                self.updated = True
        for i in list(record_s & dbrecord_s):
            self.sync_record(db, i)
        if self.updated:
            print('Domain %s updated' % self.name)
            self.update_serial()
            db.update_soa(self.name, self.soa_content)
            os.system('pdnssec rectify-zone %s' % self.name)

    def validate(self):
        print 'Validate %s' % self.name
