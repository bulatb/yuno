#!/usr/bin/env python

import os
import re
import sys

from yuno.core import cli, config
from yuno.core.util import working_dir


def main(argv=None):
    # Figure out where Yuno lives so plugins can cd correctly if they need to.
    yuno_home = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    config.update('YUNO_HOME', yuno_home)

    with working_dir(yuno_home):
        args, subcommand_args = cli.get_cli_args()
        load_settings(args.runtime_settings, args.command)

        program = __import__(
            'yuno.{command}.{command}'.format(command=args.command),
            fromlist=['yuno.' + args.command]
        )

        program.main(subcommand_args)


def load_settings(runtime_settings, plugin_name):
    plugin_name = re.sub('[^a-z0-9_]', '', plugin_name, flags=re.I)
    plugin_settings_file = 'yuno/%s/settings/config.json' % plugin_name

    config.load_default()

    if os.path.isfile(plugin_settings_file):
        config.load_json(plugin_settings_file)

    for override in runtime_settings or []:
        key = override[0]
        if isinstance(getattr(config.config, key), list):
            value = override[1:]
        else:
            value = override[1]
        config.update(key, value)


if __name__ == '__main__':
    main()
