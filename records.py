#!/usr/bin/env python

class NS:
    def __init__(self, name, ttl):
        self.name = name
        self.ttl = ttl

    def __str__(self):
        return "\t%s NS %s" % (self.ttl, self.name)

class MX:
    def __init__(self, name, prio, ttl):
        self.name = name
        self.prio = prio
        self.ttl = ttl

    def __str__(self):
        return "\t%s MX %s %s" % (self.ttl, self.prio, self.name)

class CNAME:
    def __init__(self, name, alias, ttl):
        self.name = name
        self.alias = alias
        self.ttl = ttl

    def __str__(self):
        return "%s %s CNAME %s" % (self.name, self.ttl, self.alias)

class A:
    def __init__(self, name, addr, ttl):
        self.name = name
        self.addr = addr
        self.ttl = ttl

    def __str__(self):
        return "%s %s A %s" % (self.name, self.ttl, self.addr)

class PTR:
    def __init__(self, name, addr, ttl):
        self.name = name
        self.addr = addr
        self.ttl = ttl

    def __str__(self):
        return "%s %s PTR %s" % (self.name, self.ttl, self.addr)
