from __future__ import print_function

from collections import namedtuple
import os
import posixpath
import shutil
import subprocess
import sys
import time

from yuno.run import run, cli as run_cli
from yuno.core import config, testing
from yuno.core.config import config as settings

from . import cli


class WatchTest(testing.Test):
    def __init__(self, path):
        super(WatchTest, self).__init__(path)


    def run_in_harness(self, harness):
        shutil.copyfile(self.source.path, self.source.path + '.most-recent')
        super(WatchTest, self).run_in_harness(harness)


def _finish_current_run():
    try:
        donefile = open(posixpath.join(settings.test_folder, '.done'), 'w+')
        donefile.close()
    except OSError:
        print("Hmm... something went wrong. Try again?")


def _delete_assembly():
    asm_tests = testing.load_all()

    for test in asm_tests:
        os.remove(posixpath.join(settings.test_folder, test.source.path))


def _watch_for_files(options):
    _record_pid()

    args, _ = run_cli.get_cli_args(['all'])
    donefile = posixpath.join(settings.test_folder, '.done')

    print("Waiting for new tests. PID: " + str(os.getpid()))

    while True:
        if os.path.isfile(donefile):
            os.remove(donefile)

            print("Found new tests.\n", "=" * 80, sep="\n")

            harness, test_set = run.load_and_run(args, test_class=WatchTest)
            if len(test_set) > 0:
                run.display_results(harness)

            _delete_assembly()

            print("")
            print("=" * 80, "Done.\n", sep="\n")
            print("Waiting for new tests. PID: " + str(os.getpid()))

        time.sleep(settings.check_interval)


def main(argv=sys.argv):
    options, parser = cli.get_cli_args(argv)

    try:
        if options.finish:
            _finish_current_run()
        else:
            _watch_for_files(options)
    except KeyboardInterrupt:
        print("Watch stopped. Cleaning up...")
        _delete_assembly()
        print("Done.")
