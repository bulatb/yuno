from yuno.core.util import posix_newlines

import difflib

# The functions named in this list will be loaded in as valid options for the
# --diff switch and added to the help text. The first item is the default, used
# when --diff is given with no argument.
#
available = ['context', 'unified']

def unified(expected, actual):
    """Unified diff format: http://en.wikipedia.org/wiki/Diff#Unified_format
    """
    return ''.join(
        difflib.unified_diff(
            posix_newlines(expected).splitlines(True),
            posix_newlines(actual).splitlines(True),
            fromfile='expected',
            tofile='actual'
        )
    )


def context(expected, actual):
    """Context diff format: http://en.wikipedia.org/wiki/Diff#Context_format
    This seems to be more useful for compiler output.
    """
    return ''.join(
        difflib.ndiff(
            posix_newlines(expected).splitlines(True),
            posix_newlines(actual).splitlines(True)
        )
    )