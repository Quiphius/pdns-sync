#!/usr/bin/env python

import fileinput
import psycopg2

ttl = 3600

class Domain:
    def __init__(self, name, ns, email):
        self.name = name
        self.ns = ns
        self.email = email
    def __str__(self):
        return '%s %s %s' % (self.name, self.ns, self.email)

def main():
    for line in fileinput.input():
        s = line.split()
        print s
        if s[0] == 'T':
            ttl = s[1]
        elif s[0] == 'D':
            d = Domain(s[1], s[2], s[3])
            print d

main()
