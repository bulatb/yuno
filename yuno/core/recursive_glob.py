"""A janky globstar implementation, not completely stupid but not really
optimized. Homegrown because glob2 had no license at the time. It may be
worth replacing in the future, but for now it's adequate.

https://github.com/miracle2k/python-glob2/issues/2

"""

import os
from posixpath import join
import re
import sys
from os.path import isfile, isdir

from fnmatch import fnmatch


IGNORED_FOLDERS = ('.git', '.svn', '.hg')


def tokenize_glob(glob):
    # Super thorough. Spared no expense.
    return glob.split('/')


def search_folder(path, search_path, globstar_mode=False):
    if search_path[0] == '**':
        return search_folder(path, search_path[1:], globstar_mode=True)

    matches = []
    listing = os.listdir(path)

    if len(search_path) == 1:
        matches += find_files(path, search_path[0])
        if not globstar_mode:
            return matches

    for item in listing:
        if isdir(os.path.join(path, item)) and item not in IGNORED_FOLDERS:
            is_matching_folder = fnmatch(item, search_path[0])
            # `not is_matching_folder` prevents double-counting.
            if globstar_mode and not is_matching_folder:
                matches += search_folder(
                    join(path, item), search_path, globstar_mode=True)
            elif is_matching_folder:
                matches += search_folder(join(path, item), search_path[1:])

    return matches


def find_files(folder, pattern):
    """Returns a list of files in <folder> matching <pattern>.
    Standard glob expansion only (with fnmatch).

    """
    found = []

    for entry in os.listdir(folder):
        if isfile(os.path.join(folder, entry)):
            if fnmatch(entry, pattern):
                found.append(join(folder, entry))

    return found


def glob(file_glob, root='.'):
    """Returns a list of files paths in [root] that match [file_glob]. Supports
    standard glob tokens and globstars. Leading dots are stripped from paths for
    compatibility with Yuno's UI and the data files and my happiness.

    """
    file_glob = re.sub(r'(\*\*/){2,}', '**/', file_glob)
    file_glob = re.sub(r'^\.{1,2}[\\/]+', '', file_glob)

    tests = []
    search_path = tokenize_glob(file_glob)

    return search_folder(root, search_path)
