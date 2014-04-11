from __future__ import print_function

import os
import re
import sys
import posixpath
from datetime import datetime
from os.path import isfile

from yuno.core import history, util, errors
from yuno.core.config import config

from . import cli, text


def _in_data_folder(filename):
    return posixpath.join(config.data_folder, filename)


def _show_file(filename, line_indent='  ', sort=True):
    lines_read = 0

    with errors.converted(IOError, to=errors.DataFileError):
        with open(filename) as data_file:
            for line in (sorted(data_file) if sort else data_file):
                line = line.strip()
                if line != '':
                    print(line_indent + line)
                    lines_read += 1

    return lines_read


def _show_by_type(result_type, line_indent='  '):
    last_run = history.RunRecord.from_last_run()
    tests = last_run.__dict__[result_type]

    num_of_type = len(tests)
    when = last_run.when.strftime(history.RunRecord.time_format)
    message = util.nice_plural(num_of_type, 'test', 'tests')

    if num_of_type == 0:
        print("No {} {} last run ({})".format(message, result_type, when))
        return

    print("%s last run:\n" % result_type.capitalize())
    for test in sorted(tests):
        print(line_indent + test.strip())
    print("\n%d %s %s, %s" % (num_of_type, message, result_type, when))


def _show_failed():
    _show_by_type('failed')


def _show_failing():
    print("All failing:\n")
    count = _show_file(_in_data_folder('failing.txt'))
    print("\n%d %s" % (count, util.nice_plural(count, 'test', 'tests')))


def _show_passed():
    _show_by_type('passed')


def _show_passing():
    print("All passing:\n")
    count = _show_file(_in_data_folder('passing.txt'))
    print("\n%d %s" % (count, util.nice_plural(count, 'test', 'tests')))


def _show_skipped():
    _show_by_type('skipped')


def _show_warned():
    _show_by_type('warned')


def _show_suites():
    def with_trailing_slash(path):
        return path if folder.endswith("/") else path + "/"

    folders = config.suite_folders

    print("All suites:\n")

    for folder in folders:
        print("  " + with_trailing_slash(folder))
        num_found = 0

        for entry in sorted(os.listdir(folder)):
            if entry.endswith('.txt') and isfile(os.path.join(folder, entry)):
                num_found += 1
                print("    " + re.sub(r'\.txt$', '', entry))

        if num_found == 0:
            print("    (none)")

        print("")

    if len(folders) > 1:
        print(text.SEARCH_ORDER)


def _show_last():
    _show_file(_in_data_folder('last-run.txt'), line_indent=' ', sort=False)


def main(argv=sys.argv):
    args, parser = cli.get_cli_args(argv)

    if args.what is None:
        parser.print_help()
        sys.exit(2)

    command_handlers = {
        cli.SHOW_FAILED: _show_failed,
        cli.SHOW_FAILING: _show_failing,
        cli.SHOW_PASSED: _show_passed,
        cli.SHOW_PASSING: _show_passing,
        cli.SHOW_SKIPPED: _show_skipped,
        cli.SHOW_WARNED: _show_warned,
        cli.SHOW_SUITES: _show_suites,
        cli.SHOW_LAST: _show_last
    }

    try:
        command_handlers[args.what]()
    except errors.YunoError as e:
        print(e.for_console())
    except KeyboardInterrupt:
        print("Stopped.")
