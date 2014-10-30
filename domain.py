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
        self.updated = False
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

    def sync_record(self, i):
        for db in self.dbrecords[i]:
            found = False
            for r in self.records[i]:
                if db.data == r.data:
                    if db.prio != r.prio or db.ttl != r.ttl:
                        db_update_record(db.id, r.ttl, r.prio)
                        self.updated = True
                    r.used = True
                    found = True
            if not found:
                db_delete_record(db.id)
                self.updated = True
        for r in self.records[i]:
            if not r.used:
                db_create_record(self.name, i[0], i[1], r.data, r.ttl, r.prio)
                self.updated = True


    def sync_domain(self):
        print('Syncing domain %s' % self.name)
        self.dbrecords = db_get_records(self.name)
        record_s = set(self.records.keys())
        dbrecord_s = set(self.dbrecords.keys())
        for i in list(record_s - dbrecord_s):
            for r in self.records[i]:
                db_create_record(self.name, i[0], i[1], r.data, r.ttl, r.prio)
                self.updated = True
        for i in list(dbrecord_s - record_s):
            for r in self.dbrecords[i]:
                db_delete_record(r.id)
                self.updated = True
        for i in list(record_s & dbrecord_s):
            self.sync_record(i)
