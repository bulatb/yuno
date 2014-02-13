#!/usr/bin/env python
from __future__ import print_function

import os
from os.path import abspath, dirname, join, normpath
import sys

import subprocess


yuno_home = normpath(join(abspath(dirname(__file__)), '..'))


def run_all_tests():
    test_runner = join(yuno_home, 'dev', 'system_tests.py')
    args = [
        '--with compiler_invocation "python %s {testcase}"' % test_runner,
        '--with source_extension .txt',
        '--diff unified',
        '--with test_folder dev/system_tests',
        '--with data_folder dev/test_runs/tester'
    ]

    try:
        os.chdir(yuno_home)
        output = subprocess.check_output(
            'yuno.py run all ' + ' '.join(args),
            # Use shell=True so the shell can read yuno's shebang and find py3.
            # Windows installations may or may not have a `python3` that points
            # to Python 3, but Python 3 on Windows has an automatic version
            # switcher that can read shebangs. Invoking the .py is portable and
            # lets that happen.
            shell=True,
            universal_newlines=True)

        # Normally the output would be bytes, but it seems that
        # universal_newlines adds a string conversion. Makes sense, but don't
        # forget.
        print(output)

    except subprocess.CalledProcessError as e:
        print("Error launching test runner:")
        print(str(e.output), str(e.cmd))


def run_single_test():
    with open(sys.argv[1]) as system_test:
        args = system_test.read().strip()

    mock_compiler = join(yuno_home, 'dev', 'mock_compiler.py')
    args += ' --with compiler_invocation "python %s {testcase}"' % mock_compiler
    args += ' --with data_folder dev/test_runs/target'

    try:
        os.chdir(yuno_home)
        output = subprocess.check_output(
            'yuno.py ' + args,
            shell=True,
            universal_newlines=True)

        print(output)

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
