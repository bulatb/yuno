import argparse


def build_arg_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--finish',
        dest='finish',
        action='store_true',
        help='Recover from a network error. Use when told to by Compile.'
    )

    parser.add_argument(
        '--kill',
        dest='kill_running',
        action='store_true',
        help='Kill all running instances of Watch.'
    )

    return parser


def get_cli_args(argv):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    return (args, parser)