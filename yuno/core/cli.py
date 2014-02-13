"""Command-line interface for Yuno.

"""

import argparse


DESCRIPTION = 'Compiler! Y U NO compile???'


def build_arg_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'command',
        metavar='command',
        choices=['run', 'show', 'certify', 'prune', 'flint', 'steel'],
        help='''One of: run (to run tests), show (results and settings),
        certify (to create tests), or prune (to remove deleted and renamed
        test paths from the history)'''
    )

    parser.add_argument(
        '--with',
        action=variadic_list_option(),
        nargs='+',
        dest='runtime_settings',
        metavar=('key value', 'value'),
        help='Change configuration setting <key> to <value> for this run. Use \
        zero or more times, one `--with` per setting. If the setting is a \
        list, add one <value> for each item.')

    return parser


def variadic_list_option(min_length=2):
    class VariadicListOption(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            num_values = len(values)
            if num_values < min_length:
                parser.error("%s expects at least %d values. Got %d: %s" % (
                    option_string, min_length, num_values, ", ".join(values)))

            if getattr(namespace, self.dest) is None:
                setattr(namespace, self.dest, [])

            getattr(namespace, self.dest).append(values)


    return VariadicListOption


def get_cli_args():
    return build_arg_parser().parse_known_args()
