_warn = 0
_err = 0


def warning(msg, fname=None, row=0):
    global _warn
    if fname:
        print('W: %s in file %s line %d' % (msg, fname, row))
    else:
        print('W: %s' % msg)
    _warn += 1


def error(msg, fname=None, row=0):
    global _err
    if fname:
        print('E: %s in file %s line %d' % (msg, fname, row))
    else:
        print('E: %s' % msg)
    _err += 1


def ioerror(msg, fname):
    global _err
    print('E: %s: %s' % (fname, msg))
    _err += 1


def get_err():
    return _err


def get_warn():
    return _warn
