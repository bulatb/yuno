#!/usr/bin/env python
from os.path import abspath, dirname, join
import sys

def main():
    data_folder = join(abspath(dirname(__file__)), 'test_runs', 'target')
    with open(join(data_folder, 'last-run.txt')) as log:
        # Eat the first line, print the rest. These run logs will be short.
        sys.stdout.write(''.join(log.readlines()[1:]))


if __name__ == '__main__':
    main()
