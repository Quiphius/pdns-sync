#!/usr/bin/env python

import fileinput
#import psycopg2
import re
from domain import Domain

cur_ttl = 3600
cur_domain = None
all_domains = {}

def valid_ip(a):
    pat = re.compile('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    return pat.match(a) is not None

def find_domain(a):
    ta = a.split('.')
    x = len(ta)
    while x > 1:
        cur = '.'.join(ta[-x:])
        print(cur)
        if cur in all_domains:
            return all_domains[cur]
        x -= 1
    return None

def main():

    row = 0

    for line in fileinput.input():
        row += 1
        line = line.rstrip('\n\r')
        if not line:
            continue
        s = line.split()
        print(s)
        if s[0] =='#':
            continue
        elif s[0] == 'T':
            cur_ttl = s[1]
        elif s[0] == 'D':
            d = Domain(s[1], s[2], s[3], cur_ttl)
            all_domains[s[1]] = d
            current_domain = d
        elif s[0] == 'N':
            for ns in s[1:]:
                d.add_ns(ns)
        elif s[0] == 'M':
            d.add_mx(s[1], s[2])
        elif s[0] == 'C':
            find_domain(s[1]).add_cname(s[1], s[2])
        elif valid_ip(s[0]):
            print('Found A')
        else:
            print('Invalid row %d' % row);


main()

all_domains['oet.nu'].dump_domain()
