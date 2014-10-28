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
        if not name in self.records:
            self.records[name] = {}
        if not type in self.records[name]:
            self.records[name][type] = []

        r = Record(data, prio, ttl);
        self.records[name][type].append(r)

    def sync_soa(self):
        if self.name in self.dbrecords and 'SOA' in self.dbrecords[self.name]:
            soa = self.dbrecords[self.name]['SOA']
        else:
            soa = []                
        if len(soa) == 0:
            db_create_record(self.name, 'SOA', '%s %s' % (self.ns, self.email), self.ttl, 0)
        elif len(soa) != 1:
            print('E: Wrong number of SOA records for domain %s' % self.name)
        else:
            c = soa[0]
            if c.data != '%s %s' % (self.ns, self.email) or c.ttl != int(self.ttl) or c.prio != 0:
                print 'foo'
                db_update_record(c.id, 'SOA', '%s %s' % (self.ns, self.email), self.ttl, 0)

    def sync_records(self, n, t):
        print('%s %s' % (n, t))

    def sync_domain(self):
        print('Syncing domain %s' % self.name)
        self.dbrecords = db_get_records(self.name)
        self.sync_soa()
        print self.records.keys()
        for name in self.records.keys():
            for type in self.records[name].keys():
                self.sync_records(name, type)

    def dump_domain(self):
        print self.records
