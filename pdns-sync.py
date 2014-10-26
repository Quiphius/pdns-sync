#!/usr/bin/env python

import fileinput
from domain import Domain
from utils import valid_ip, find_domain, gen_ptr
from database import db_connect, db_get_domains, db_create_domains, db_delete_domains

cur_ttl = 3600
cur_domain = None
all_domains = {}
all_db_domains = {}
warning = 0
error = 0

def main():

    row = 0
    global warning, error

    for line in fileinput.input():
        row += 1
        line = line.rstrip('\n\r')
        if not line:
            continue
        s = line.split()
        sl = len(s)
        if s[0] =='#':
            continue
        elif s[0] == 'T':
            if sl == 2:
                if s[1].isdigit() and int(s[1]) > 0:
                    cur_ttl = s[1]
                else:
                    print('W: Not a valid TTL value on line %d' % row)
                    warning += 1
            else:
                print('W: No arguments for TTL value on line %d' % row)
                warning += 1
        elif s[0] == 'D':
            if sl == 4:
                if s[1] not in all_domains:
                    d = Domain(s[1], s[2], s[3], cur_ttl)
                    all_domains[s[1]] = d
                    current_domain = d
                else:
                    print('E: duplicate domain %s at line %d' %(s[1], row))
                    error += 1
            else:
                print('E: Wrong number of arguments for Domain on line %d' % row)
                error += 1
        elif s[0] == 'N':
            if sl > 1:
                for ns in s[1:]:
                    d.add_ns(ns, cur_ttl)
            else:
                print('W: No arguments for NS on line %d' % row)
                warning += 1
        elif s[0] == 'M':
            if sl > 1:
                prio = 10
                for x in s[1:]:
                    if x.isdigit():
                        prio = int(x)
                    else:
                        d.add_mx(x, prio, cur_ttl)
            else:
                print('W: No arguments for MX on line %d' % row)
                warning += 1
        elif s[0] == 'C':
            if sl == 3:
                find_domain(s[1], all_domains).add_cname(s[1], s[2], cur_ttl)
            else:
                print('W: Wrong number of arguments for CNAME on line %d' % row)
                warning += 1
        elif valid_ip(s[0]):
            if sl > 1:
                for x in s[1:]:
                    d = find_domain(x, all_domains)
                    if d:
                        d.add_a(x, s[0], cur_ttl)
                        ptr = gen_ptr(s[0])
                        ptrd = find_domain(ptr, all_domains)
                        if ptrd:
                            ptrd.add_ptr(ptr, x, cur_ttl)
                        else:
                            print('W: Missing domain for PTR %s on line %s' % (ptr, row))
                            warning += 1
                    else:
                        print('W: Missing domain for A %s on line %s' % (x, row))
                        warning += 1
            else:
                print('W: No names for A on line %d' % row)
                warning += 1
        else:
            print('W: Invalid row %d' % row);
            warning += 1

def sync():
    db_connect()
    db_get_domains(all_db_domains)

    list_domains = all_domains.keys()
    list_db_domains = all_db_domains.keys()
    create_list = list(set(list_domains) - set(list_db_domains))
    delete_list = list(set(list_db_domains) - set(list_domains))

    db_create_domains(create_list)
    db_delete_domains(delete_list)

main()

print('%d error(s) and %d warning(s)' % (error, warning))

if error == 0:
    sync()
else:
    print('Errors found, not syncing')
