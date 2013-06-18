import os
import posixpath
import shutil
import subprocess
import sys
import time

from yuno.run import run
from yuno.core import config, testing
from yuno.core.config import config as settings

from . import cli


class SteelTest(testing.Test):
    def __init__(self, path):
        super(SteelTest, self).__init__(path)


    def run_in_harness(self, harness):
        shutil.copyfile(self.source.path, self.source.path + '.most-recent')
        super(SteelTest, self).run_in_harness(harness)


def _finish_current_run():
    try:
        donefile = open(posixpath.join(settings.test_folder, '.done'), 'w+')
        donefile.close()
    except OSError:
        print("Hmm... something went wrong. Try again?")


def _kill_running():
    print("Killing running instances of yuno steel.")

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


def _listen_for_files():
    _record_pid()

    donefile = posixpath.join(settings.test_folder, '.done')
    print("Waiting to receive tests. PID: " + str(os.getpid()))

    while True:
        if os.path.isfile(donefile):
            os.remove(donefile)

            print("Detected new tests.\n", "=" * 80, sep="\n")

            run.TEST_CLASS = SteelTest
            run.main(argv=['all'])
            _delete_assembly()

            print("\n", "=" * 80, "Done.\n", sep="\n")
            print("Waiting to receive tests. PID: " + str(os.getpid()))

        time.sleep(settings.check_interval)


def main(argv=sys.argv):
    options, parser = cli.get_cli_args(argv)
    config.load_json('yuno/steel/settings/config.json')

    try:
        if options.finish:
            _finish_current_run()
        elif options.kill_running:
            _kill_running()
        else:
            _listen_for_files()
    except KeyboardInterrupt:
        print("Steel stopped. Cleaning up...")
        _delete_assembly()
        print("Done.")