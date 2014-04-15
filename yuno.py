#!/usr/bin/env python
"""If Yuno was installed with setuptools, it launches from an entry point at
yuno.launch:main. For systems where that isn't possible or too much work, like
ieng9, this launcher lets it run directly from the unzipped source.

$ cd <here>
$ yuno.py run all

Note that symlinks may not work in Windows. If you link here and it fails with
import errors, try a DOSKEY alias instead.

> doskey yuno=python /path/to/yuno.py $*

"""


if __name__ == '__main__':
    from os.path import abspath, dirname, realpath
    import sys
    from yuno import launch

    if sys.argv[0] == 'yuno.py':
        sys.argv[0] = 'yuno'

    launch.main(yuno_home=abspath(dirname(realpath(__file__))))
