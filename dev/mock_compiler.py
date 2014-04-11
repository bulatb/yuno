#!/usr/bin/env python

import os
import sys

import argparse


def build_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
        metavar="filename",
        help="mock source file to \"compile\"")

    return parser


def parse_instructions(filename):
    actions = {'exit': 0}

    with open(filename) as f:
        lines = f.readlines()
        instructions = lines[0].split()
        actions.update(dict([i.split('=') for i in instructions]))


    return (actions, ''.join(lines[1:]))


def action_stdout(filename):
    with open(filename) as f:
        sys.stdout.write(f.read())


def action_stderr(filename):
    with open(filename) as f:
        sys.stderr.write(f.read())


def main():
    args = build_arg_parser().parse_args()
    actions, body_text = parse_instructions(args.filename)

    os.chdir(os.path.dirname(args.filename) or '.')

    for name, value in actions.items():
        globals().get('action_' + name, lambda x: None)(value)

    if actions['result'] == 'fail':
        sys.stdout.write(body_text)

    sys.stdout.flush()
    sys.stderr.flush()
    sys.exit(int(actions['exit']))


if __name__ == "__main__":
    main()
