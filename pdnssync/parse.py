from domain import Domain
from utils import find_domain, check_ipv4, check_ipv6, gen_ptr_ipv4, gen_ptr_ipv6, expand_ipv6
from error import warning, error, ioerror


all_domains = {}
all_records = {}


def parse(fname):
    cur_ttl = 3600
    row = 0
    d = None

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
