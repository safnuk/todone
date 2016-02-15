import argparse
import os
import sys

from .actions import CHOICES as ACTION_CHOICES
from .actions import SCRIPT_DESCRIPTION, dispatch_action

def main(args=None):
    if args is None:
        args = sys.argv[1:] if len(sys.argv) > 1 else ['help']

    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument('action', choices=ACTION_CHOICES)

    args = parser.parse_args(args)

    dispatch_action(args.action, args)


if __name__ == '__main__':
    main()
