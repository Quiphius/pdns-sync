#!/usr/bin/env python

from records import *
from database import db_get_records, db_create_record, db_update_record

class Domain:
    def __init__(self, name, ns, email, ttl):
        self.name = name
        self.ns = ns
        self.email = email
        self.ttl = ttl
        self.all_ns = []
        self.all_mx = []
        self.all_cnames = []
        self.all_a = []
        self.all_ptr = []

    def __str__(self):
        return '%s %s %s %s' % (self.name, self.ns, self.email, self.ttl)

    def add_ns(self, ns, ttl):
        r = NS(ns, ttl)
        self.all_ns.append(r)

    def add_mx(self, mx, prio, ttl):
        r = MX(mx, prio, ttl)
        self.all_mx.append(r)

    def add_cname(self, name, alias, ttl):
        r = CNAME(name, alias, ttl)
        self.all_cnames.append(r)

    def add_a(self, name, addr, ttl):
        r = A(name, addr, ttl)
        self.all_a.append(r)

    def add_ptr(self, name, addr, ttl):
        r = PTR(name, addr, ttl)
        self.all_ptr.append(r)

    def sync_domain(self):
        print('Syncing %s' % self.name)
        r = db_get_records(self.name, 'SOA')
        if len(r) == 0:
            db_create_record(self.name, 'SOA', '%s %s' % (self.ns, self.email), self.ttl, 0)
        elif len(r) != 1:
            print('E: Wrong number of SOA records for domain %s' % self.name)
        else:
            c = r[0]
            if c.data != '%s %s' % (self.ns, self.email) or c.ttl != int(self.ttl) or c.prio != 0:
                db_update_record(c.id, 'SOA', '%s %s' % (self.ns, self.email), self.ttl, 0)
        
    def dump_domain(self):
        print self.name, self.ttl, 'SOA', self.ns, self.email
        for ns in self.all_ns:
            print ns
        for mx in self.all_mx:
            print mx
        for cname in self.all_cnames:
            print cname
        for a in self.all_a:
            print a
        for ptr in self.all_ptr:
            print ptr
