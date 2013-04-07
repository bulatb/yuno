import os
import sys

from yuno import core
from yuno.core import errors, testing, util
from yuno.core.config import config

import cli, testing


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
        print """
        Detected pipe to `certify files`. If you're trying to pipe test cases,
        use `certify -`.

        Streams piped to `certify files` will be understood as answers for the
        prompts, which can damage the test repo if it's not what you intended.
        If you just want all your cases certified, try `--yes --overwrite`. If
        you really want to drive the program through a pipe, make sure the first
        line of your input stream is "pipe" (no quotes, ending in a \\n)."""

        return False


def _certify_files(options):
    if not sys.stdin.isatty() and not _confirm_pipe():
        return

    print "Generating answer files for " + options.glob

    glob = options.glob.strip()
    harness = testing.AnswerGeneratingHarness(
        interactive=(not options.correct),
        force_overwrite=options.overwrite
    )
    test_set = core.testing.load_from_glob(glob, test_class=testing.NaiveTest)

    harness.run_set(test_set)


def _certify_pipe(options):
    print "Generating answer files for piped-in tests"

    tests = core.testing.load_from_file(
        sys.stdin,
        line_filter=util.strip_line_labels
    )
    _reset_stdin()

    harness = testing.AnswerGeneratingHarness(
        interactive=(not options.correct),
        force_overwrite=options.overwrite
    )

    harness.run_set(tests)


def main(argv=sys.argv):
    options, parser = cli.get_cli_args(argv)

    command_handlers = {
        cli.CERTIFY_FILES: _certify_files,
        cli.CERTIFY_PIPE: _certify_pipe
    }

    try:
        command_handlers[options.command](options)
    except errors.YunoError as e:
        print e.for_console()
