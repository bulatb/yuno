import argparse

from yuno.core.config import config

from . import help


def build_arg_parser():
    suite_folder = config.suite_folders[0]
    parser = argparse.ArgumentParser(description=help.description)

    parser.add_argument(
        '--all',
        dest='prune_all',
        action='store_true',
        help='prune everything, including your suites and the last run\'s log'
    )

    parser.add_argument(
        '--suites',
        dest='prune_suites',
        action='store_true',
        help='also prune your suites (in %s only)' % suite_folder
    )

    parser.add_argument(
        '--last-run',
        dest='prune_last',
        action='store_true',
        help='also prune the last run\'s log file (rarely needed)'
    )

    return parser


def get_cli_args(argv):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    return (args, parser)
