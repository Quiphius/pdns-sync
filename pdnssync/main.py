import argparse
import os
from config import parse_config
from domain import Domain
from database import Database
from utils import find_domain, check_ipv4, check_ipv6, gen_ptr_ipv4, gen_ptr_ipv6, expand_ipv6
from error import warning, error, ioerror, get_warn, get_err

typemap = {'N': 'NS', 'M': 'MX', 'C': 'CNAME'}

cur_domain = None
all_domains = {}
all_db_domains = {}
all_records = {}


def parse(fname):
    cur_ttl = 3600
    row = 0

    try:
        for line in open(fname):
            row += 1
            line = line.rstrip('\n\r')
            if not line or line[0] == '#':
                continue
            s = line.split()
            sl = len(s)
            if s[0] == 'T':
                if sl == 2:
                    if s[1].isdigit() and int(s[1]) > 0:
                        cur_ttl = int(s[1])
                    else:
                        warning('Not a valid TTL value', fname, row)
                else:
                    warning('No arguments for TTL value', fname, row)
            elif s[0] == 'D':
                if sl == 4:
                    if s[1] not in all_domains:
                        d = Domain(s[1], s[2], s[3], cur_ttl)
                        all_domains[s[1]] = d
                    else:
                        error('Duplicate domain %s' % s[1], fname, row)
                else:
                    error('Wrong number of arguments for domain', fname, row)
            elif s[0] == 'N':
                if sl > 1:
                    for ns in s[1:]:
                        d.add_record(d.name, 'NS', ns, 0, cur_ttl)
                else:
                    warning('No arguments for NS', fname, row)
            elif s[0] == 'M':
                if sl > 1:
                    prio = 10
                    for x in s[1:]:
                        if x.isdigit():
                            prio = int(x)
                        else:
                            d.add_record(d.name, 'MX', x, prio, cur_ttl)
                else:
                    warning('No arguments for MX', fname, row)
            elif s[0] == 'C':
                if sl == 3:
                    find_domain(s[1], all_domains).add_record(s[1], 'CNAME', s[2], 0, cur_ttl)
                else:
                    warning('Wrong number of arguments for CNAME', fname, row)
            elif check_ipv4(s[0]):
                if sl > 1:
                    for x in s[1:]:
                        force = False
                        if x[0] == '~':
                            force = True
                            x = x[1:]
                        d = find_domain(x, all_domains)
                        if d:
                            d.add_record(x, 'A', s[0], 0, cur_ttl)
                            ptr = gen_ptr_ipv4(s[0])
                            ptrd = find_domain(ptr, all_domains)
                            if ptrd:
                                ptrd.add_record_uniq(ptr, 'PTR', x, 0, cur_ttl, force)
                            else:
                                warning('Missing domain for PTR %s' % ptr, fname, row)
                        else:
                            warning('Missing domain for A %s' % x, fname, row)
                else:
                    warning('No names for A', fname, row)
            elif check_ipv6(s[0]):
                if sl > 1:
                    for x in s[1:]:
                        d = find_domain(x, all_domains)
                        if d:
                            d.add_record(x, 'AAAA', s[0], 0, cur_ttl)
                            ptr = gen_ptr_ipv6(expand_ipv6(s[0]))
                            ptrd = find_domain(ptr, all_domains)
                            if ptrd:
                                ptrd.add_record_uniq(ptr, 'PTR', x, 0, cur_ttl)
                            else:
                                warning('Missing domain for PTR %s' % ptr, fname, row)
                        else:
                            warning('Missing domain for AAAA %s' % x, fname, row)
                else:
                    warning('No names for AAAA', fname, row)
            else:
                warning('Invalid row', fname, row)
    except IOError as e:
        ioerror(e.strerror, fname)


def validate():
    for d in all_domains:
        all_domains[d].validate()


def sync(db):
    all_db_domains = db.get_domains()

    list_domains = all_domains.keys()
    list_db_domains = all_db_domains.keys()
    create_list = list(set(list_domains) - set(list_db_domains))
    delete_list = list(set(list_db_domains) - set(list_domains))

    db.create_domains(create_list)
    db.delete_domains(delete_list)

    for i in list_domains:
        d = all_domains[i]
        d.sync_domain(db)

def export(db):
    all_db_domain = db.get_domains()
    for d in all_db_domain:
        print "# %s" % d
        records = db.get_records(d)
        soa = records[(d, 'SOA')][0].data.split(' ')
        print "D %s %s %s" % (d, soa[0], soa[1])

        if (d, 'NS') in records:
            ns = records[(d, 'NS')]
            ns_names = []
            for i in ns:
                ns_names.append(i.data)
            print "N %s" % ' '.join(ns_names)

        if (d, 'MX') in records:
            mx = records[(d, 'MX')]
            mx_names = []
            for i in mx:
                mx_names.append("%s %s" % (i.prio, i.data))
            print "M %s" % ' '.join(mx_names)

        for i in records:
            if i[1] == 'A':
                for j in records[i]:
                    print "%s %s" % (j.data, i[0])
            if i[1] == 'AAAA':
                for j in records[i]:
                    print "%s %s" % (j.data, i[0])
            if i[1] == 'CNAME':
                for j in records[i]:
                    print "C %s %s" % (i[0], j.data)

        print


def do_sync():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    parser.add_argument("-w", "--werror", action="store_true", help="also break on warnings")
    parser.add_argument("-c", "--config", help="specify config file")
    parser.add_argument('files', metavar='file', nargs='+', help='the files to parse')
    args = parser.parse_args()

    if args.config:
        config = args.config
    else:
        config = os.environ['HOME'] + '/.pdnssync.ini'

    options = parse_config(config)
    if 'type' not in options or 'database' not in options or 'dbuser' not in options or 'dbpassword' not in options or 'dbhost' not in options:
        print('Missing database config in ~/.pdnssync.ini')
        quit()

    for fname in args.files:
        parse(fname)

    validate()

    err = get_err()
    warn = get_warn()

    print('%d error(s) and %d warning(s)' % (err, warn))

    if err == 0 and (not args.werror or warn == 0):
        db = Database(options['type'], options['database'], options['dbuser'], options['dbpassword'], options['dbhost'])
        sync(db)
    else:
        print('Errors found, not syncing')


def do_export():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="specify config file")
    args = parser.parse_args()

    if args.config:
        config = args.config
    else:
        config = os.environ['HOME'] + '/.pdnssync.ini'

    options = parse_config(config)
    if 'type' not in options or 'database' not in options or 'dbuser' not in options or 'dbpassword' not in options or 'dbhost' not in options:
        print('Missing database config in ~/.pdnssync.ini')
        quit()

    db = Database(options['type'], options['database'], options['dbuser'], options['dbpassword'], options['dbhost'])
    export(db)
