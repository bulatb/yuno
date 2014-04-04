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
        print(self.source.path, self.source.path + '.most-recent')
        shutil.copyfile(self.source.path, self.source.path + '.most-recent')
        super(WatchTest, self).run_in_harness(harness)


def _finish_current_run():
    try:
        donefile = open(posixpath.join(settings.test_folder, '.done'), 'w+')
        donefile.close()
    except OSError:
        print("Hmm... something went wrong. Try again?")


def _kill_running():
    print("Killing running instances of Watch.")

    pid_filename = posixpath.join(settings.data_folder, 'pids.txt')
    killed = 0

    with open(pid_filename, 'r') as pids:
        for line in pids:
            pid = line.strip()
            print('kill -9 {}... '.format(pid), end='')

            try:
                subprocess.check_call('kill -9 ' + line.strip())
                print('done.')
                killed += 1
            except subprocess.CalledProcessError as e:
                print('failed. Exit code ' + str(e.returncode))

    with open(pid_filename, 'w+'):
        pass

    print("Done. Killed " + str(killed))


def _record_pid():
    with open(posixpath.join(settings.data_folder, 'pids.txt'), 'a+') as pids:
        pids.writelines([str(os.getpid()) + '\n'])


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
            run.load_and_run(args, test_class=WatchTest)
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
        elif options.kill_running:
            _kill_running()
        else:
            _watch_for_files(options)
    except KeyboardInterrupt:
        print("Watch stopped. Cleaning up...")
        _delete_assembly()
        print("Done.")