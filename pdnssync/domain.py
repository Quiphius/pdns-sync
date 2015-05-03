import os
from datetime import datetime
from pdnssync.record import Record
from pdnssync.error import warning, error
from pdnssync.utils import has_address


class Domain(object):
    def __init__(self, name, ns, email, ttl, refresh=86400, retry=7200, expire=604800, minimum=300):
        self.name = name
        self.ns = ns
        self.email = email
        self.ttl = ttl
        self.records = {}
        self.updated = False
        self.serial = 0
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.minimum = minimum

    def gen_soa(self):
        self.soa_content = '%s %s %s %s %s %s %s' % (self.ns, self.email, self.serial, self.refresh, self.retry, self.expire, self.minimum)
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

    def add_record(self, name, rtype, data, prio, ttl):
        i = (name, rtype)
        if i not in self.records:
            self.records[i] = []
        r = Record(data, prio, ttl)
        self.records[i].append(r)

    def add(self, k, l):
        self.records[k] = l

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

    def validate(self, domains):
        print('Validate %s' % self.name)

        if (self.name, 'NS') in self.records:
            ns_rec = self.records[(self.name, 'NS')]
            ns = [n.data for n in ns_rec]
            if self.ns not in ns:
                warning('Nameserver %s not in NS list' % self.ns)

            dup = set([n for n in ns if ns.count(n) > 1])
            if dup:
                warning('Duplicate NS records %s in domain %s' % (','.join(dup), self.name))

            for n in ns:
                if not has_address(n, domains):
                    warning('Address for NS %s not found' % n)
        else:
            error('No nameservers for domain %s' % self.name)

        if (self.name, 'MX') in self.records:
            mx_rec = self.records[(self.name, 'MX')]
            mx = [m.data for m in mx_rec]
            for m in mx:
                if not has_address(m, domains):
                    warning('Address for MX %s not found' % m)
