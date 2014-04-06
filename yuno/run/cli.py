import argparse

from . import diff_routines, help


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

        if num_values == 1:
            if values[0] in ONE_ARG_COMMANDS:
                command = values[0]
            else:
                # It's a glob.
                command = RUN_GLOB
                setattr(namespace, 'glob', values[0])
        elif num_values == 2:
            # Example:
            #
            # `yuno run phase 1` will make a namespace like this:
            #     (command='run', phase='1', ...)
            #
            # where <command> is <values[0]> and a field named <values[0]> is
            # <values[1]>. The <command> is used for routing to a handler
            # which will read <values[1]> from a key named <values[0]>.
            #
            # TODO: This maybe shouldn't need a comment to be clear.
            argument, value = values
            setattr(namespace, argument, value)

            command = values[0]
        elif num_values == 4:
            if values[0] == RUN_PHASE and values[2] == RUN_CHECK:
                command = RUN_PHASE_AND_CHECK
                setattr(namespace, 'phase', values[1])
                setattr(namespace, 'check', values[3])
            else:
                parser.error("Expected `phase <#> check <#>`; got `%s`" % (
                    ' '.join(values)))
        else:
            num_shown = 6
            num_hidden = num_values - num_shown
            shown_values = values[:num_shown]

            message = "Expected 1, 2, or 4 arguments; got %d: %s" % (
                num_values, ' '.join(shown_values))

            if num_hidden > 0:
                message += " [... %d more]" % num_hidden

            parser.error(message)

        setattr(namespace, 'command', command)


def build_arg_parser():
    parser = argparse.ArgumentParser(
        usage=help.usage,
        description=help.description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

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

    parser.add_argument(
        '-I', '--ignore',
        dest='ignore_patterns',
        metavar='regex',
        nargs='+',
        help='Don\'t run tests whose path (including filename) matches any \
        <regex>. Python-style patterns; takes (?iLmsux) flags; backrefs can \
        be named or \\1, \\2, etc.'
    )

    return parser


def get_cli_args(argv):
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    return (args, parser)
