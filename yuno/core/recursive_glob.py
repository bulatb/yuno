"""A janky globstar implementation, not completely stupid but not really
optimized. The search is recursive in both senses, so don't use this for
folders that go more than... a thousand deep?

But also, why do you have folders that deep? Human, stahp!

"""

import os
import posixpath
import re
import sys
from os.path import isfile, isdir

from fnmatch import fnmatch


WILDCARDS = ('*', '**')


def tokenize_glob(glob):
    # Super thorough. Spared no expense.
    return glob.split('/')


def find_files(folder, pattern, bucket):
    """Searches a directory for files matching [pattern] and throws them into
    [bucket]. Standard glob expansion only (with fnmatch).

    """
    for entry in os.listdir(folder):
        if isfile(os.path.join(folder, entry)):
            if fnmatch(entry, pattern):
                bucket.append(posixpath.join(folder, entry))

    return bucket


def search_folder(path, search_path, matched_files):
    """Searches [path] and subdirs for files whose paths match all the fragments
    in [search_path], expanding standard glob tokens with fnmatch and globstars
    (**) to zero or more directories.

    Mutates [matched_files] in place and returns it just in case.

    """
    if len(search_path) == 0:
        return matched_files
    elif len(search_path) == 1:
        return find_files(path, search_path[0], matched_files)

    listing = os.listdir(path)
    path = '' if path == '.' else path
    for item in listing:
        if isdir(os.path.join(path, item)):
            if search_path[0] == '**':
                search_folder(
                    posixpath.join(path, item), search_path[1:], matched_files
                )
                search_folder(
                    posixpath.join(path, item), search_path, matched_files
                )
            elif fnmatch(item, search_path[0]):
                search_folder(
                    posixpath.join(path, item), search_path[1:], matched_files
                )

    return matched_files


def glob(file_glob, root='.'):
    """Returns a list of files paths in [root] that match [file_glob]. Supports
    standard glob tokens and globstars. Leading dots are stripped from paths for
    compatibility with Yuno's UI and the data files and my happiness.

    """
    file_glob = re.sub(r'(/\*\*){2,}', '/**', file_glob)
    file_glob = re.sub(r'^\.{1,2}[\\/]+', '', file_glob)

    tests = []
    search_path = tokenize_glob(file_glob)

    return search_folder(root, search_path, tests)
