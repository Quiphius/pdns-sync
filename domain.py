#!/usr/bin/env python

from records import *
from database import db_get_records, db_create_record, db_update_record

class Domain:
    def __init__(self, name, ns, email, ttl):
        self.name = name
        self.ns = ns
        self.email = email
        self.ttl = ttl
        self.records = {}

    def __str__(self):
        return '%s %s %s %s' % (self.name, self.ns, self.email, self.ttl)

    def add_record(self, name, type, data, prio, ttl):
        if not type in self.records:
            self.records[type] = {}
        if not name in self.records[type]:
            self.records[type][name] = []

        r = Record(data, prio, ttl);
        self.records[type][name].append(r)

    def sync_soa(self):
        if 'SOA' not in self.dbrecords:
            db_create_record(self.name, self.name, 'SOA', '%s %s' % (self.ns, self.email), self.ttl, 0)
        else:
            c = self.dbrecords['SOA'][self.name][0]
            if c.data != '%s %s' % (self.ns, self.email) or c.ttl != int(self.ttl) or c.prio != 0:
                print 'foo'
                db_update_record(c.id, 'SOA', '%s %s' % (self.ns, self.email), self.ttl, 0)

    def sync_records(self,t):
        if t not in self.records and t not in self.dbrecords:
            return
        if t in self.records and t not in self.dbrecords:
            for n in self.records[t]:
                for r in self.records[t][n]:
                    db_create_record(self.name, n, t, r.data, r.ttl, r.prio)
        

    def sync_domain(self):
        print('Syncing domain %s' % self.name)
        self.dbrecords = db_get_records(self.name)
        self.sync_soa()
        for type in ['NS', 'MX', 'CNAME', 'A', 'PTR']:
            self.sync_records(type)

    def dump_domain(self):
        print self.records
