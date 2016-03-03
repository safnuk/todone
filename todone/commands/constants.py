DATE_REGEX = [
    r'({})',
    r'({})(?P<sign>[+-])(?P<offset>\d+)(?P<interval>[d|w|m|y])'
]

DUE_REGEX = [x.format('due|du|d') for x in DATE_REGEX]
REMIND_REGEX = [x.format('remind|remin|remi|rem|re|r') for x in DATE_REGEX]
