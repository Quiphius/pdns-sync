#!/usr/bin/env python

import fileinput
import psycopg2

cur_ttl = 3600
all_domains = {}

class Domain:
    def __init__(self, name, ns, email, ttl):
        self.name = name
        self.ns = ns
        self.email = email
        self.ttl = ttl
    def __str__(self):
        return '%s %s %s %s' % (self.name, self.ns, self.email, self.ttl)

def main():
    for line in fileinput.input():
        s = line.split()
        print s
        if s[0] == 'T':
            cur_ttl = s[1]
        elif s[0] == 'D':
            d = Domain(s[1], s[2], s[3], cur_ttl)
            print d
            all_domains[s[1]] = d
    print all_domains

main()
