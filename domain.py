#!/usr/bin/env python

from records import *

class Domain:
    def __init__(self, name, ns, email, ttl):
        self.name = name
        self.ns = ns
        self.email = email
        self.ttl = ttl
        self.all_ns = []
        self.all_mx = []
        self.all_cnames = []

    def __str__(self):
        return '%s %s %s %s' % (self.name, self.ns, self.email, self.ttl)

    def add_ns(self, ns):
        r = NS(ns, self.ttl)
        self.all_ns.append(r)

    def add_mx(self, prio, mx):
        r = MX(mx, prio, self.ttl)
        self.all_mx.append(r)

    def add_cname(self, name, alias):
        r = CNAME(name, alias, self.ttl)
        self.all_cnames.append(r)

    def dump_domain(self):
        print self.name, self.ttl, 'SOA', self.ns, self.email
        for ns in self.all_ns:
            print ns
        for mx in self.all_mx:
            print mx
        for cname in self.all_cnames:
            print cname

