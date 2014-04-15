import argparse

from . import help


SHOW_FAILED = 'failed'
SHOW_FAILING = 'failing'
SHOW_PASSED = 'passed'
SHOW_PASSING = 'passing'
SHOW_SKIPPED = 'skipped'
SHOW_WARNED = 'warned'
SHOW_SUITES = 'suites'
SHOW_LAST = 'last'


def build_arg_parser():
    parser = argparse.ArgumentParser(
        usage=help.usage,
        description=help.description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        'what',
        choices=[
            'failed', 'failing',
            'passed', 'passing',
            'skipped', 'warned',
            'suites',
            'last'
        ],
        help=''
    )

    return parser


def get_cli_args(argv):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    return (args, parser)
