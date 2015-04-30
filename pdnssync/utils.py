import socket


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


def has_address(r, l):
    d = find_domain(r, l)
    return (r, 'A') in d.records


def gen_ptr_ipv4(a):
    ta = a.split('.')
    ta.reverse()
    ta.append('in-addr.arpa')
    r = '.'.join(ta)
    return r


def gen_ptr_ipv6(a):
    ta = list(a)
    ta.reverse()
    ta.append('ip6.arpa')
    r = '.'.join(ta)
    return r


def expand_ipv6(addr):
    parts = addr.split(':')
    missing = 8 - len(parts) + 1
    res = ''

    for part in parts:
        if part:
            res += ('0000' + part)[-4:]
        else:
            while missing:
                res += '0000'
                missing -= 1
    return res
