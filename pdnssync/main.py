import argparse
import os
from config import parse_config
from database import Database
from parse import parse, assign, all_domains, all_records
from error import get_warn, get_err


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

    print all_records

    assign()

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
