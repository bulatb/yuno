import os
import posixpath
import re


def to_posix_path(path):
    return posixpath.join(*path.split(os.sep))


def posix_newlines(text):
    return text.replace('\r\n', '\n')


def multiline_fill(placeholder, value, template):
    """Replaces template placeholders with values.

    Basic case:
        stuff stuff {item} stuff (-> becomes ->) stuff stuff value stuff

    Multiline case:
        stuff stuff
        [arbitrary whitespace]{placeholder_for_value_with_newlines}

        (-> becomes ->)

        stuff stuff
        [that whitespace](value line 1)
        [that whitespace](value line 2)
        ...etc

    TODO: There might be a way to do this with format().

    """
    if '\n' not in value and '\r' not in value:
        # format() would need weird escaping here
        return template.replace('{' + placeholder + '}', value)

    def value_padder(value):
        def padder(matchobj):
            # Leading whitespace includes the original newline
            leading_whitespace = matchobj.group(1)
            lines = value.splitlines(True)
            original_line = leading_whitespace + lines[0]

            # Now remove the newlines so they don't get double-added to the
            # output because splitlines(True) keeps them intact. It's not
            # beautiful, but it works for the cases that matter without
            # assuming what was near the {placeholder} in the template.
            # Otherwise leading or trailing newlines tend to get eaten, which
            # here is really bad because the values (exact output, etc.) need to
            # be presented as-is.
            space_padding = re.sub(r'\r\n|\n', '', leading_whitespace)
            added_lines = ''.join(space_padding + line for line in lines[1:])

            return original_line + added_lines

        return padder

    matcher = r'(\s*)\{(%s)\}' % placeholder
    return re.sub(matcher, value_padder(value), template, flags=re.MULTILINE)


def decomment_json(json_string):
    return re.sub(r'^\s*//.*$', '', json_string, flags=re.MULTILINE)


def nice_plural(number, singular, plural):
    return singular if number == 1 else plural


def strip_line_labels(line):
    """Each line in the run record file(s) has a label that identifies its
    type: p for passed tests, + for fixes, - for regressions, and so on. When
    piping in test lists or building ad-hoc suites from these records, it's
    nice to have this helper to clean up the data.

    """
    return re.sub(r'^[pfws\+\-\=] ', '', line)


class working_dir(object):
    """Change the program's working directory for the enclosed block, then
    change it back. Among other things, this allows all the paths in the config
    file to be absolute or relative to Yuno without confusing rules.

    """
    def __init__(self, new_dir):
        self._working_dir = new_dir
        self._saved_working_dir = os.getcwd()


    def __enter__(self):
        os.chdir(self._working_dir)


    def __exit__(self, type, value, traceback):
        os.chdir(self._saved_working_dir)
