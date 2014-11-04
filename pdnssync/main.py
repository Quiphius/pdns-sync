#!/usr/bin/env python

import argparse
import os
from config import parse_config
from domain import Domain
from database import db_connect, db_get_domains, db_create_domains, db_delete_domains
from utils import find_domain, gen_ptr, check_ipv4, check_ipv6

typemap = { 'N': 'NS', 'M': 'MX', 'C': 'CNAME' }

cur_domain = None
all_domains = {}
all_db_domains = {}
warning = 0
error = 0

def parse(fname):
    global warning, error
    cur_ttl = 3600
    row = 0

    try:
        with open(fname) as f:
            for line in f.readlines():
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
                            cur_ttl = int(s[1])
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
                            d.add_record(d.name, 'NS', ns, 0, cur_ttl)
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
                                d.add_record(d.name, 'MX', x, prio, cur_ttl)
                    else:
                        print('W: No arguments for MX on line %d' % row)
                        warning += 1
                elif s[0] == 'C':
                    if sl == 3:
                        find_domain(s[1], all_domains).add_record(s[1], 'CNAME', s[2], 0, cur_ttl)
                    else:
                        print('W: Wrong number of arguments for CNAME on line %d' % row)
                        warning += 1
                elif check_ipv4(s[0]):
                    if sl > 1:
                        for x in s[1:]:
                            d = find_domain(x, all_domains)
                            if d:
                                d.add_record(x, 'A', s[0], 0, cur_ttl)
                                ptr = gen_ptr(s[0])
                                ptrd = find_domain(ptr, all_domains)
                                if ptrd:
                                    ptrd.add_record(ptr, 'PTR', x, 0, cur_ttl)
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
    except IOError as e:
        print('%s: %s' % (fname, e.strerror))

def sync(dsn):
    db_connect(dsn)
    all_db_domains = db_get_domains()

    list_domains = all_domains.keys()
    list_db_domains = all_db_domains.keys()
    create_list = list(set(list_domains) - set(list_db_domains))
    delete_list = list(set(list_db_domains) - set(list_domains))

    db_create_domains(create_list)
    db_delete_domains(delete_list)

    for i in list_domains:
        d = all_domains[i]
        d.sync_domain()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", action="count", default=0, help="increase output verbosity")
    parser.add_argument('files', metavar='file', nargs='+', help='the files to parse')
    args = parser.parse_args()

    options = parse_config(os.environ['HOME'] + '/.pdnssync.ini')
    if 'database' not in options or 'dbuser' not in options or 'dbpassword' not in options or 'dbhost' not in options:
        print('Missing database config in ~/.pdnssync.ini')
        quit()

    dsn = 'dbname=%s user=%s host=%s password=%s' % (options['database'], options['dbuser'], options['dbhost'], options['dbpassword'])

    for fname in args.files:
        parse(fname)

    print('%d error(s) and %d warning(s)' % (error, warning))

    if error == 0:
        sync(dsn)
    else:
        print('Errors found, not syncing')
