#!/usr/bin/env python

class Domain:
    def __init__(self, name, ns, email, ttl):
        self.name = name
        self.ns = ns
        self.email = email
        self.ttl = ttl
        self.all_ns = []
        self.all_mx = []
        self.all_cnames = {}

    def __str__(self):
        return '%s %s %s %s' % (self.name, self.ns, self.email, self.ttl)

    def add_ns(self, ns):
        self.all_ns.append(ns)

    def add_mx(self, prio, mx):
        self.all_mx.append((prio, mx))

    def add_cname(self, name, alias):
        self.all_cnames[name] = alias

    def dump_domain(self):
        print self.name, self.ttl, 'SOA', self.ns, self.email
        for ns in self.all_ns:
            print self.name, self.ttl, 'NS', ns
        for mx in self.all_mx:
            print self.name, self.ttl, 'MX', mx[0], mx[1]
        for name, cname in self.all_cnames.items():
            print name, self.ttl, 'CNAME', cname

