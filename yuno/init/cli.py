import argparse


def build_arg_parser():
    parser = argparse.ArgumentParser(
        usage='yuno init [-h] project_name')

    parser.add_argument(
        'project_name',
        help='?')

    return parser


def get_cli_args(argv):
    parser = build_arg_parser()
    return parser.parse_args(argv), parser
