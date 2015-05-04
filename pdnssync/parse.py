import re
from pdnssync.domain import Domain
from pdnssync.utils import find_domain, check_ipv4, check_ipv6, gen_ptr_ipv4, gen_ptr_ipv6, expand_ipv6
from pdnssync.error import warning, error, ioerror
from pdnssync.record import RecordList


class Parser(object):

    def __init__(self):
        self.all_domains = {}
        self.all_records = RecordList()

    def parse(self, fname):
        cur_ttl = 3600
        row = 0
        cur_domain = None
        cur_parent = None

        try:
            for line in open(fname):
                row += 1
                line = line.rstrip('\n\r')
                if not line or line[0] == '#':
                    continue
                s = re.split('\s*', line)
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
                    if s[1] not in self.all_domains:
                        if sl == 4 or sl == 8:
                            if sl == 4:
                                cur_domain = Domain(s[1], s[2], s[3], cur_ttl)
                            else:
                                cur_domain = Domain(s[1], s[2], s[3], cur_ttl, s[4], s[5], s[6], s[7])
                            cur_parent = find_domain(s[1], self.all_domains)
                            self.all_domains[s[1]] = cur_domain
                        else:
                            error('Wrong number of arguments for domain', fname, row)
                    else:
                        error('Duplicate domain %s' % s[1], fname, row)

                elif s[0] == 'N':
                    if cur_domain:
                        if sl > 1:
                            for ns in s[1:]:
                                cur_domain.add_record(cur_domain.name, 'NS', ns, 0, cur_ttl)
                                if cur_parent:
                                    cur_parent.add_record(cur_domain.name, 'NS', ns, 0, cur_ttl)
                        else:
                            warning('No arguments for NS', fname, row)
                    else:
                        error('No domain defines for NS', fname, row)

                elif s[0] == 'M':
                    if cur_domain:
                        if sl > 1:
                            prio = 10
                            for x in s[1:]:
                                if x.isdigit():
                                    prio = int(x)
                                else:
                                    cur_domain.add_record(cur_domain.name, 'MX', x, prio, cur_ttl)
                        else:
                            warning('No arguments for MX', fname, row)
                    else:
                        error('No domain defined for MX', fname, row)

                elif s[0] == 'C':
                    if sl == 3:
                        self.all_records.add_record(s[1], 'CNAME', s[2], 0, cur_ttl)
                    else:
                        warning('Wrong number of arguments for CNAME', fname, row)

                elif s[0] == 'S':
                    if sl == 6:
                        self.all_records.add_record(s[1], 'SRV', '%s %s %s' % (s[3], s[4], s[5]), int(s[2]), cur_ttl)
                    else:
                        warning('Wrong number of arguments for SRV', fname, row)

                elif s[0] == 'X':
                    if sl > 1:
                        txt = ' '.join(s[2:])
                        if txt[0] == '"' and txt[-1] == '"':
                            self.all_records.add_record(s[1], 'TXT', ' '.join(s[2:]), 0, cur_ttl)
                        else:
                            warning('Text not enclosed with " for TXT', fname, row)
                    else:
                        warning('Wrong number of arguments for TXT', fname, row)

                elif check_ipv4(s[0]):
                    if sl > 1:
                        for x in s[1:]:
                            force = False
                            if x[0] == '~':
                                force = True
                                x = x[1:]
                            self.all_records.add_record(x, 'A', s[0], 0, cur_ttl)
                            ptr = gen_ptr_ipv4(s[0])
                            self.all_records.add_record_uniq(ptr, 'PTR', x, 0, cur_ttl, force)
                    else:
                        warning('No names for A', fname, row)

                elif check_ipv6(s[0]):
                    if sl > 1:
                        for x in s[1:]:
                            force = False
                            if x[0] == '~':
                                force = True
                                x = x[1:]
                            self.all_records.add_record(x, 'AAAA', s[0], 0, cur_ttl)
                            ptr = gen_ptr_ipv6(expand_ipv6(s[0]))
                            self.all_records.add_record_uniq(ptr, 'PTR', x, 0, cur_ttl, force)
                    else:
                        warning('No names for AAAA', fname, row)

                else:
                    warning('Invalid row', fname, row)
        except IOError as e:
            ioerror(e.strerror, fname)

    def assign(self):
        for i in self.all_records.records:
            r = self.all_records.records[i]
            d = find_domain(i[0], self.all_domains)
            if d:
                d.add(i, r)
            else:
                warning('Missing domain for %s %s' % (i[1], i[0]))

    def get_domains(self):
        return self.all_domains
