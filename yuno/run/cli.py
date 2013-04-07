import argparse
import help

import diff_routines


RUN_ALL = 'all'
RUN_FAILED = 'failed'
RUN_FAILING = 'failing'
RUN_PASSED = 'passed'
RUN_PASSING = 'passing'
RUN_GLOB = '<glob>'
RUN_PIPE = '-'
ONE_ARG_COMMANDS = (
    RUN_ALL, RUN_FAILED, RUN_FAILING, RUN_PASSED, RUN_PASSING, RUN_PIPE
)

RUN_PHASE = 'phase'
RUN_CHECK = 'check'
RUN_SUITE = 'suite'
RUN_FILES = 'files'

RUN_PHASE_AND_CHECK = 'phase <#> check <#>'


class OverloadedArg(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        num_values = len(values)
        command = None

        # Let's not get all polymorphic here.
        # Explicit is better.

        if num_values == 1:
            if values[0] in ONE_ARG_COMMANDS:
                command = values[0]
            # if values[0] == RUN_ALL:
            #     command = RUN_ALL
            # elif values[0] == RUN_FAILED:
            #     command = RUN_FAILED
            # elif values[0] == RUN_FAILING:
            #     command = RUN_FAILING
            # elif values[0] == RUN_PASSED:
            #     command = RUN_PASSED
            # elif values[0] == RUN_PASSING:
            #     command = RUN_PASSING
            # elif values[0] == RUN_PIPE:
            #     command = RUN_PIPE
            else: # it's a glob
                command = RUN_GLOB
                setattr(namespace, 'glob', values[0])
        elif num_values == 2:

            if values[0] == RUN_PHASE:
                command = RUN_PHASE
                setattr(namespace, 'phase', values[1])
            elif values[0] == RUN_CHECK:
                command = RUN_CHECK
                setattr(namespace, 'check', values[1])
            elif values[0] == RUN_FILES:
                command = RUN_FILES
                setattr(namespace, 'files', values[1])
            elif values[0] == RUN_SUITE:
                command = RUN_SUITE
                setattr(namespace, 'suite', values[1])
        elif num_values == 4:
            if values[0] == RUN_PHASE and values[2] == RUN_CHECK:
                command = RUN_PHASE_AND_CHECK
                setattr(namespace, 'phase', values[1])
                setattr(namespace, 'check', values[3])

        setattr(namespace, 'command', command)


def build_arg_parser():
    parser = argparse.ArgumentParser(usage=help.usage)

    parser.add_argument(
        'command',
        action=OverloadedArg,
        nargs='+',
        help=argparse.SUPPRESS
    )

    parser.add_argument(
        '--save',
        dest='save_as',
        metavar='suite_name',
        help='Run the tests, then save them as a suite with this name.'
    )

    parser.add_argument(
        '--diff',
        dest='diff_mode',
        metavar='diff_mode',
        nargs='?',
        choices=diff_routines.available,
        const=diff_routines.available[0],
        help='''Show diff output for failed tests. Accepted modes are context
        and unified. Defaults to context.'''
    )

    parser.add_argument(
        '-o',
        '--overwrite',
        dest='overwrite',
        action='store_true',
        help="Use with --save to overwrite an existing suite"
    )

    parser.add_argument(
        '--pause',
        dest='pause_on',
        metavar='event(s)',
        nargs='?',
        const='f',
        help='''Pause on certain events: p (test passed), f (test failed),
        s (test skipped), w (test warned), or any combination (pf, fsw, etc).
        Defaults to f.'''
    )

    return parser


def get_cli_args(argv):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    return (args, parser)
