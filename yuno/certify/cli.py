import argparse

from . import help


CERTIFY_FILES = 'files'
CERTIFY_PIPE = '-'


class OverloadedArg(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        command = None

        if values[0] == CERTIFY_FILES and len(values) == 2:
            command = CERTIFY_FILES
            setattr(namespace, 'glob', values[1])
        elif values[0] == CERTIFY_PIPE:
            command = CERTIFY_PIPE

        setattr(namespace, 'command', command)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        usage=help.usage,
        description=help.description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        'command',
        action=OverloadedArg,
        nargs='+',
        help=argparse.SUPPRESS
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='overwrite existing answer files without prompting'
    )

    parser.add_argument(
        '--correct',
        action='store_true',
        help='don\'t ask if output is correct before saving'
    )

    return parser


def get_cli_args(argv):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    return (args, parser)
