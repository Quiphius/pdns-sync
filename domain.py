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
