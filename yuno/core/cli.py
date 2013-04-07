"""Command-line interface for Yuno.

"""

import argparse


DESCRIPTION = 'Compiler! Y U NO compile???'


def build_arg_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        'command',
        metavar='command',
        choices=['run', 'show', 'certify', 'prune'],
        help='''One of: run (to run tests), show (results and settings),
        certify (to create tests), or prune (to remove deleted and renamed
        test paths from the history)'''
    )

    parser.add_argument(
        'tail',
        nargs=argparse.REMAINDER,
        help=argparse.SUPPRESS
    )

    return parser


def get_cli_args(argv):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    return (args, parser)
