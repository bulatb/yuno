#!/usr/bin/env python

import os
from os.path import abspath, dirname, isfile, join, realpath
import re
import sys

yuno_home = abspath(dirname(realpath(__file__)))
sys.path.insert(0, yuno_home)

from yuno.core import cli, config
from yuno.core.util import working_dir


def main(argv=None):
    config.update('YUNO_HOME', yuno_home)
    args, subcommand_args = cli.get_cli_args()

    if args.command == cli.CREATE_PROJECT:
        return create_project(subcommand_args)

    project_home = get_project_home()

    config.update('SHELL_WORKING_DIR', os.getcwd())
    config.update('PROJECT_HOME', project_home)

    with working_dir(project_home):
        load_settings(args.runtime_settings, args.command)

        program = __import__(
            'yuno.{command}.{command}'.format(command=args.command),
            fromlist=['yuno.' + args.command]
        )

        program.main(subcommand_args)


def create_project(args):
    from yuno.init import init
    init.main(args)


def get_project_home():
    cwd = os.getcwd()
    is_project = lambda path: path and isfile(join(path, 'yuno-project.json'))
    default_project = os.environ.get('YUNO_PROJECT')

    if is_project(cwd):
        return cwd
    elif is_project(default_project):
        return default_project
    else:
        sys.exit(
            "Working path '%s' is not a Yuno project.\n" % cwd +
            "Either cd to a project or set YUNO_PROJECT in your shell.")


def load_settings(runtime_settings, module_name):
    module_name = re.sub('[^a-z0-9_]', '', module_name, flags=re.I)
    module_settings_file = 'settings/%s.json' % module_name

    config.load_default()

    if isfile(module_settings_file):
        config.load_json(module_settings_file)

    for override in runtime_settings or []:
        key = override[0]
        if isinstance(getattr(config.config, key), list):
            value = override[1:]
        else:
            value = override[1]
        config.update(key, value)


if __name__ == '__main__':
    main()
