from __future__ import print_function

import os
import sys

from yuno import core
from yuno.core import errors, testing, util
from yuno.core.config import config

from . import cli, testing, text


def _reset_stdin():
    """Reattaches stdin to the terminal. Used to take input if the program was
    piped to.

    """
    try:
        sys.stdin = open('CON')
    except IOError:
        sys.stdin = open('/dev/tty')


def _confirm_pipe():
    if sys.stdin.readline().strip() == 'pipe':
        return True
    else:
        print(text.UNEXPECTED_PIPE)
        return False


def _certify_files(options):
    if not sys.stdin.isatty() and not _confirm_pipe():
        return

    print("Generating answer files for " + options.glob)

    glob = options.glob.strip()
    harness = testing.AnswerGeneratingHarness(
        interactive=(not options.correct),
        force_overwrite=options.overwrite
    )
    test_set = core.testing.load_from_glob(glob, test_class=testing.NaiveTest)

    harness.run_set(test_set)


def _certify_pipe(options):
    print("Generating answer files for piped-in tests")

    tests = core.testing.load_from_file(
        sys.stdin,
        line_filter=util.strip_line_labels,
        test_class=testing.NaiveTest
    )
    _reset_stdin()

    harness = testing.AnswerGeneratingHarness(
        interactive=(not options.correct),
        force_overwrite=options.overwrite
    )

    harness.run_set(tests)


def main(argv=sys.argv):
    args, parser = cli.get_cli_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(2)

    command_handlers = {
        cli.CERTIFY_FILES: _certify_files,
        cli.CERTIFY_PIPE: _certify_pipe
    }

    try:
        command_handlers[args.command](args)
    except errors.YunoError as e:
        print(e.for_console())
    except KeyboardInterrupt:
        print("Stopped.")
