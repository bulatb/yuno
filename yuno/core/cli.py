"""Command-line interface for Yuno.

"""

import argparse


DESCRIPTION = 'Compiler! Y U NO compile???'
HELP = 'help'


def build_arg_parser():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        'command',
        metavar='command',
        choices=[HELP, 'run', 'show', 'certify', 'prune', 'compile', 'steel'],
        help='One of: %(choices)s')

    parser.add_argument(
        '--with',
        action=variadic_list_action(),
        nargs='+',
        dest='runtime_settings',
        metavar=('key value', 'value'),
        help='Change configuration setting <key> to <value> for this run. Use \
        zero or more times, one `--with` per setting. If the setting is a \
        list, add one <value> for each item.')

    return parser


def variadic_list_action(min_length=2):
    class VariadicListAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            num_values = len(values)
            if num_values < min_length:
                parser.error("%s expects at least %d values. Got %d: %s" % (
                    option_string, min_length, num_values, ", ".join(values)))

            if getattr(namespace, self.dest) is None:
                setattr(namespace, self.dest, [])

            getattr(namespace, self.dest).append(values)


    return VariadicListAction


def get_cli_args():
    parser = build_arg_parser()
    launcher_args, plugin_args = parser.parse_known_args()

    if launcher_args.command in (HELP, '-h', '--help'):
        parser.print_help()
        parser.exit()

    return launcher_args, plugin_args
