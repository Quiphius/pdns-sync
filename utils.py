#!/usr/bin/env python

import re

def valid_ip(a):
    pat = re.compile('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    return pat.match(a) is not None

def find_domain(a, l):
    ta = a.split('.')
    x = len(ta)
    while x > 1:
        cur = '.'.join(ta[-x:])
        if cur in l:
            return l[cur]
        x -= 1
    return None

def gen_ptr(a):
    ta = a.split('.')
    ta.reverse()
    ta.append('in-addr.arpa')
    r = '.'.join(ta)
    return r
