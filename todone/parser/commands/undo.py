import todone.exceptions as exceptions


def parse_args(args=[]):
    if args:
        raise exceptions.ArgumentError('undo command takes no arguments')
    return {}
