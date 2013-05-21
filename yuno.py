#!/usr/bin/env python3

import os
import sys

from yuno.core import cli, config
from yuno.core.util import working_dir


def main(argv=None):
    # Figure out where Yuno lives so plugins can cd correctly if they need to.
    yuno_home = os.path.abspath(os.path.dirname(__file__))
    setattr(config.config, 'YUNO_HOME', yuno_home)

    with working_dir(yuno_home):
        config.load_default()
        options, parser = cli.get_cli_args(argv or sys.argv[1:])
        program = __import__(
            'yuno.{command}.{command}'.format(command=options.command),
            fromlist=['yuno.' + options.command]
        )

        program.main(options.tail)

if __name__ == '__main__':
    main()
