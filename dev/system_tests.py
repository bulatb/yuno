#!/usr/bin/env python
from __future__ import print_function

import glob
import os
from os.path import abspath, dirname, join, normpath
import shutil
import sys
from time import sleep

import argparse
import subprocess


YUNO_HOME = normpath(join(abspath(dirname(__file__)), '..'))

CHECK_AGAINST_LOG = 'log'
CHECK_AGAINST_OUTPUT = 'output'

TESTER_LOG_DIR = 'dev/test_runs/tester'
TARGET_LOG_DIR = 'dev/test_runs/target'


def run_all_tests(args):
    test_runner = join(YUNO_HOME, 'dev', 'system_tests.py')
    args += [
        '--with compiler_invocation "python %s --e2e {testcase}"' % test_runner,
        '--with source_extension .txt',
        '--with test_folder dev/system_tests',
        '--with data_folder ' + TESTER_LOG_DIR
    ]

    try:
        os.chdir(YUNO_HOME)
        runner = subprocess.Popen('yuno.py ' + ' '.join(args),
            # Use shell=True so the shell can read yuno's shebang and find py3.
            # Windows installations may or may not have a `python3` that points
            # to Python 3, but Python 3 on Windows has an automatic version
            # switcher that can read shebangs. Invoking the .py is portable and
            # lets that happen.
            shell=True,
            universal_newlines=True)

        while runner.poll() is None:
            sleep(1)


    except subprocess.CalledProcessError as e:
        print("Error launching test runner:")
        print(str(e.output), str(e.cmd))


def run_single_test(test_name):
    abspath_to_test = abspath(dirname(test_name))

    with open(test_name) as system_test:
        lines = system_test.readlines()
        test_setup = dict([opt.split('=') for opt in lines[0].strip().split()])

        mode = test_setup['mode']

        for setting, value in test_setup.items():
            if setting.startswith('set-'):
                _set_log_file(
                    join(YUNO_HOME, TARGET_LOG_DIR, setting[4:] + '.txt'),
                    join(abspath_to_test, value))

        args = lines[1].strip()

    mock_compiler = '../../../mock_compiler.py'
    args += ' --with compiler_invocation "python %s {testcase}"' % mock_compiler
    args += ' --with data_folder %s' % TARGET_LOG_DIR

    try:
        os.chdir(YUNO_HOME)
        output = subprocess.check_output(
            'yuno.py ' + args,
            shell=True,
            universal_newlines=True)

        if mode == CHECK_AGAINST_OUTPUT:
            print(output, end='')
        elif mode == CHECK_AGAINST_LOG:
            with open(join(TARGET_LOG_DIR, 'last-run.txt')) as log:
                # Eat the first line, print the rest. These logs will be short.
                print(''.join(log.readlines()[1:]), end='')

        for log_file in glob.glob(join(TARGET_LOG_DIR, '*.txt')):
            os.remove(log_file)

    except subprocess.CalledProcessError as e:
        print("Error running test: ")
        print(str(e.output), str(e.cmd))


def _set_log_file(log_file, contents_file):
    shutil.copyfile(contents_file, log_file)


def build_arg_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--e2e',
        dest='test_name',
        default=None)

    return parser


if __name__ == '__main__':
    version = sys.version_info[0]
    driver_args, yuno_args = build_arg_parser().parse_known_args()

    if driver_args.test_name:
        run_single_test(driver_args.test_name)
    else:
        print('(py%d) Running all tests (from %s)...' % (version, os.getcwd()))
        run_all_tests(yuno_args)
