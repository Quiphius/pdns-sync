import argparse
from pdnssync.database import Database
from pdnssync.parse import Parser
from pdnssync.error import get_warn, get_err

parser = Parser()


def validate():
    domains = parser.get_domains()
    for d in sorted(domains):
        domains[d].validate(domains)


def sync(db):
    all_db_domains = db.get_domains()
    all_domains = parser.get_domains()

    list_domains = all_domains.keys()
    list_db_domains = all_db_domains.keys()
    create_list = list(set(list_domains) - set(list_db_domains))
    delete_list = list(set(list_db_domains) - set(list_domains))

    db.create_domains(create_list)
    db.delete_domains(delete_list)

    for i in sorted(list_domains):
        d = all_domains[i]
        d.sync_domain(db)


def export(db):
    all_db_domain = db.get_domains()
    for d in all_db_domain:
        print('# %s' % d)
        records = db.get_records(d)
        soa = records[(d, 'SOA')][0].data.split(' ')
        print('D %s %s %s' % (d, soa[0], soa[1]))

        if (d, 'NS') in records:
            ns = records[(d, 'NS')]
            ns_names = []
            for i in ns:
                ns_names.append(i.data)
            print('N %s' % ' '.join(ns_names))

        if (d, 'MX') in records:
            mx = records[(d, 'MX')]
            mx_names = []
            for i in mx:
                mx_names.append("%s %s" % (i.prio, i.data))
            print('M %s' % ' '.join(mx_names))

        for i in records:
            if i[1] == 'A':
                for j in records[i]:
                    print('%s %s' % (j.data, i[0]))
            if i[1] == 'AAAA':
                for j in records[i]:
                    print('%s %s' % (j.data, i[0]))
            if i[1] == 'CNAME':
                for j in records[i]:
                    print('C %s %s' % (i[0], j.data))
            if i[1] == 'SRV':
                for j in records[i]:
                    print('S %s %s %s' % (i[0], j.prio, j.data))
            if i[1] == 'TXT':
                for j in records[i]:
                    print('X %s %s' % (i[0], j.data))
        print()


def do_sync():
    aparser = argparse.ArgumentParser()
    aparser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    aparser.add_argument("-w", "--werror", action="store_true", help="also break on warnings")
    aparser.add_argument('files', metavar='file', nargs='+', help='the files to parse')
    args = aparser.parse_args()

    for fname in args.files:
        parser.parse(fname)

    parser.assign()

    validate()

    err = get_err()
    warn = get_warn()

    print('%d error(s) and %d warning(s)' % (err, warn))

    if err == 0 and (not args.werror or warn == 0):
        db = Database()
        sync(db)
    else:
        print('Errors found, not syncing')


def do_export():
    db = Database()
    export(db)
