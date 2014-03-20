#!/usr/bin/env python
from __future__ import print_function

import glob
import itertools
import os
from os.path import abspath, dirname, join, normpath
import shlex
import shutil
import sys
from time import sleep

import argparse
import subprocess
import yaml


YUNO_HOME = normpath(join(abspath(dirname(__file__)), '..'))
YUNO_CMD = join('.', 'yuno.py')

CHECK_AGAINST_LOG = 'log'
CHECK_AGAINST_OUTPUT = 'output'

TESTER_LOG_DIR = 'dev/test_runs/tester'
TARGET_LOG_DIR = 'dev/test_runs/target'


def run_all_tests(args):
    test_runner = join(YUNO_HOME, 'dev', 'system_tests.py')
    args += [
        '--with compiler_invocation "python %s --e2e {testcase}"' % test_runner,
        '--with source_extension .yaml',
        '--with test_folder dev/system_tests',
        '--with data_folder ' + TESTER_LOG_DIR
    ]

    try:
        os.chdir(YUNO_HOME)
        runner = subprocess.Popen('%s %s' % (YUNO_CMD,  ' '.join(args)),
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
        test_setup = yaml.load(system_test.read())

        mode = test_setup['mode']

        for log_name, log in test_setup.get('set', {}).items():
            _set_log_file(
                join(YUNO_HOME, TARGET_LOG_DIR, log_name + '.txt'),
                join(abspath_to_test, log))

    try:
        os.chdir(YUNO_HOME)
        output = subprocess.check_output(
            ['python', YUNO_CMD] + _build_test_command(test_setup),
            universal_newlines=True)

        if 'transform-output' in test_setup:
            output = _transform_output(output, test_setup['transform-output'])

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


def _build_test_command(test_setup):
    mock_compiler = '../../../mock_compiler.py'

    default_settings = {
        'compiler_invocation': '"python %s {testcase}"' % mock_compiler,
        'data_folder': TARGET_LOG_DIR
    }

    settings = default_settings.copy()
    settings_from_test = test_setup.get('settings', {})

    # Checking every test's compiler_invocation for malicious code is not
    # acceptable, but running dozens of them without checking is too dangerous.
    # TODO: Think about a better way to solve this.
    if 'compiler_invocation' in settings_from_test:
        raise ValueError('compiler_invocation not allowed in test settings')

    settings.update(settings_from_test)

    command = shlex.split(test_setup['command'])
    for k, v in settings.items():
        command.extend(['--with', k] + shlex.split(v))

    return command


def _transform_output(output, transforms):
    def slice_lines(text, start=0, end=None):
        lines = text.splitlines(True)
        lines = lines[start:end] if end is not None else lines[start:]
        return ''.join(lines)

    allowed_transforms = {'slice-lines': slice_lines}

    for name, args in transforms.items():
        if name in allowed_transforms:
            output = allowed_transforms[name](output, **args)
        else:
            raise ValueError(
                'Unknown output-transform %s (choose from: %s)' % (
                    name, ', '.join(allowed_transforms.keys())))

    return output


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
    version = '.'.join((str(v) for v in sys.version_info[:3]))
    driver_args, yuno_args = build_arg_parser().parse_known_args()

    if driver_args.test_name:
        run_single_test(driver_args.test_name)
    else:
        print('(python %s) Running all tests (from %s)...' % (
            version, os.getcwd()))
        run_all_tests(yuno_args)
