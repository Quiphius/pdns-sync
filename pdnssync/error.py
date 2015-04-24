_warn = 0
_err = 0


def fwarning(msg, fname, row):
    global _warn
    print('W: %s in file %s line %d' % (msg, fname, row))
    _warn += 1


def warning(msg):
    global _warn
    print('W: %s' % msg)
    _warn += 1


def ferror(msg, fname, row):
    global _err
    print('E: %s in file %s line %d' % (msg, fname, row))
    _err += 1


def ioerror(msg, fname):
    global _err
    print('E: %s: %s' % (fname, msg))
    _err += 1


def get_err():
    return _err


def get_warn():
    return _warn
