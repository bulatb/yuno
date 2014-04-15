from __future__ import print_function

import os
import shutil

from yuno.core.config import config

from yuno.modules.init import cli


def get_project_template_path():
    # If YUNO_HOME is set, it's running from source.
    if config.YUNO_HOME is not None:
        return os.path.join(config.YUNO_HOME, 'resources', 'default_project')

    # If not, assume it's running from an entry point.
    from pkg_resources import Requirement, resource_filename
    return resource_filename(
        Requirement.parse("Yuno"), 'resources/default_project')


def main(argv):
    args, _ = cli.get_cli_args(argv)

    try:
        shutil.copytree(get_project_template_path(), args.project_name)
        print("Made a Yuno project in '%s'." % args.project_name)
    except shutil.Error as e:
        print(e)
