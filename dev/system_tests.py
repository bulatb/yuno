#!/usr/bin/env python
from __future__ import print_function

import argparse
import glob
import itertools
import os
from os.path import abspath, dirname, join, normpath, realpath
import shlex
import shutil
import subprocess
import sys
from time import sleep

import yaml


YUNO_HOME = normpath(join(abspath(dirname(realpath(__file__))), '..'))
DEV_DIR = join(YUNO_HOME, 'dev')

HARNESS_PROJECT = join(YUNO_HOME, 'dev', 'projects', 'harness')
TARGET_PROJECT = join(YUNO_HOME, 'dev', 'projects', 'target')

PROJECT = join(YUNO_HOME, 'resources', 'default_project')

CHECK_AGAINST_LOG = 'log'
CHECK_AGAINST_OUTPUT = 'output'

TESTER_LOG_DIR = 'data'
TARGET_LOG_DIR = 'scratch'


def run_all_tests(args, yuno_cmd, no_install):
    args.extend([
        '--with',
        'compiler_invocation',
        'python ../system_tests.py%s --e2e {testcase}' % (' -n' if no_install else '')
    ])

    try:
        os.chdir(HARNESS_PROJECT)
        runner = subprocess.Popen(
            yuno_cmd + args, universal_newlines=True)

        while runner.poll() is None:
            sleep(1)

    except subprocess.CalledProcessError as e:
        print("Error launching test runner:")
        print(str(e.output), str(e.cmd))

    except OSError as e:
        print("Error launching test runner:")
        print(str(e))


def run_single_test(test_name, yuno_cmd):
    abspath_to_test = abspath(dirname(test_name))

    with open(test_name) as system_test:
        test_setup = yaml.load(system_test.read())

        mode = test_setup['mode']
        for log_name, log in test_setup.get('set', {}).items():
            _set_log_file(
                join(DEV_DIR, 'projects', 'target', 'scratch', log_name + '.txt'),
                join(abspath_to_test, log))

    try:
        os.chdir(TARGET_PROJECT)
        output = subprocess.check_output(
            yuno_cmd + _build_test_command(test_setup),
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
    command = shlex.split(test_setup['command'])
    settings = test_setup.get('settings', {})

    # Checking every test's compiler_invocation for malicious code is not
    # acceptable, but running dozens of them without checking is too dangerous.
    # TODO: Think about a better way to solve this.
    if 'compiler_invocation' in settings:
        raise ValueError('compiler_invocation not allowed in test settings')

    for setting, value in settings.items():
        command.extend(['--with', setting] + shlex.split(value))

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
        default=None,
        help=argparse.SUPPRESS)

    parser.add_argument(
        '-n', '--no-install',
        dest='no_install',
        action='store_true',
        help='run system tests from unzipped source, without installing')

    return parser

if __name__ == '__main__':
    version = '.'.join((str(v) for v in sys.version_info[:3]))
    driver_args, yuno_args = build_arg_parser().parse_known_args()

    if driver_args.no_install:
        yuno_cmd = ['python', join(YUNO_HOME, 'yuno.py')]
    else:
        yuno_cmd = ['yuno']

    if driver_args.test_name:
        run_single_test(driver_args.test_name, yuno_cmd)
    else:
        print('(python %s) Running all tests (from %s)...' % (
            version, os.getcwd()))
        run_all_tests(yuno_args, yuno_cmd, driver_args.no_install)
