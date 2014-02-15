#!/usr/bin/env python
from __future__ import print_function

import os
from os.path import abspath, dirname, join, normpath
import sys
from time import sleep

import subprocess


YUNO_HOME = normpath(join(abspath(dirname(__file__)), '..'))


def run_all_tests():
    test_runner = join(YUNO_HOME, 'dev', 'system_tests.py')
    args = [
        '--with compiler_invocation "python %s {testcase}"' % test_runner,
        '--with source_extension .txt',
        '--diff unified',
        '--with test_folder dev/system_tests',
        '--with data_folder dev/test_runs/tester'
    ]

    try:
        os.chdir(YUNO_HOME)
        runner = subprocess.Popen(
            'yuno.py run all ' + ' '.join(args),
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


CHECK_AGAINST_LOG = 'log'
CHECK_AGAINST_OUTPUT = 'output'


def run_single_test():
    target_logs_to = 'dev/test_runs/target'

    with open(sys.argv[1]) as system_test:
        test_instructions = system_test.readlines()
        mode = test_instructions[0].split('=')[1].strip()
        args = test_instructions[1].strip()

    mock_compiler = '../../../mock_compiler.py'
    args += ' --with compiler_invocation "python %s {testcase}"' % mock_compiler
    args += ' --with data_folder %s' % target_logs_to

    try:
        os.chdir(YUNO_HOME)
        output = subprocess.check_output(
            'yuno.py ' + args,
            shell=True,
            universal_newlines=True)

        if mode == CHECK_AGAINST_OUTPUT:
            print(output, end='')
        elif mode == CHECK_AGAINST_LOG:
            with open(join(target_logs_to, 'last-run.txt')) as log:
                # Eat the first line, print the rest. These logs will be short.
                print(''.join(log.readlines()[1:]), end='')

    except subprocess.CalledProcessError as e:
        print("Error running test: ")
        print(str(e.output), str(e.cmd))


if __name__ == '__main__':
    version = sys.version_info[0]
    if len(sys.argv) > 1:
        run_single_test()
    else:
        print('(py%d) Running all tests (from %s)...' % (version, os.getcwd()))
        run_all_tests()
