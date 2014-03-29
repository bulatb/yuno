from __future__ import print_function

import os
import shutil

from yuno.core.config import config

from yuno.init import cli


def main(argv):
    args, _ = cli.get_cli_args(argv)

    try:
        shutil.copytree(
            os.path.join(config.YUNO_HOME, 'resources', 'default_project'),
            args.project_name)
        print("Made a Yuno project in '%s'." % args.project_name)
    except shutil.Error as e:
        print(e)
