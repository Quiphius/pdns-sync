#!/usr/bin/env python

import socket
import re

def check_ipv4(n):
    try:
        socket.inet_pton(socket.AF_INET, n)
        return True
    except socket.error:
        return False

def check_ipv6(n):
    try:
        socket.inet_pton(socket.AF_INET6, n)
        return True
    except socket.error:
        return False

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
