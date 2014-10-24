#!/usr/bin/env python

class Domain:
    def __init__(self, name, ns, email, ttl):
        self.name = name
        self.ns = ns
        self.email = email
        self.ttl = ttl
    def __str__(self):
        return '%s %s %s %s' % (self.name, self.ns, self.email, self.ttl)
