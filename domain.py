#!/usr/bin/env python

from records import *
from database import db_get_records, db_create_record, db_update_record, db_delete_record

class Domain:
    def __init__(self, name, ns, email, ttl):
        self.name = name
        self.ns = ns
        self.email = email
        self.ttl = ttl
        self.records = {}
        soa = Record('%s %s' % (self.ns, self.name), 0, ttl)
        self.records[(self.name, 'SOA')] = [soa]

    def __str__(self):
        return '%s %s %s %s' % (self.name, self.ns, self.email, self.ttl)

    def add_record(self, name, type, data, prio, ttl):
        i = (name, type)
        if i not in self.records:
            self.records[i] = []
        r = Record(data, prio, ttl);
        self.records[i].append(r)

    def sync_domain(self):
        print('Syncing domain %s' % self.name)
        self.dbrecords = db_get_records(self.name)
        rl = set(self.records.keys())
        dbl = set(self.dbrecords.keys())
        for i in list(rl - dbl):
            print 'Add', i
            for r in self.records[i]:
                db_create_record(self.name, i[0], i[1], r.data, r.ttl, r.prio)
        for i in list(dbl - rl):
            print 'Del', i
            for r in self.dbrecords[i]:
                db_delete_record(r.id)
        for i in list(rl & dbl):
            print 'Upd', i

    def dump_domain(self):
        print self.records
