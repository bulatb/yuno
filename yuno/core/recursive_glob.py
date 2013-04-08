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


IGNORED_FOLDERS = ('.git', '.svn', '.hg')


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
    """Searches [path] and subdirs (if applicable) for files whose paths
    match all the fragments in [search_path], in order, expanding standard
    glob tokens with fnmatch and globstars (**) to zero or more directories.

    [search_path] must end in a pattern that will match a file name.

    Mutates [matched_files] in place and returns it just in case.

    """

    # A globstar expands to zero or more folders between it and the next
    # folder in the path, if any. The basic idea here is:
    #
    #   1. Expand to zero: search this folder again, but chopping off the
    #      globstar and matching against the next path element. (Inputs are
    #      filtered so multiple consecutive globstars are crunched into one.)
    #      That will match things like a/b for a/**/b, but it won't match
    #      a/a/b.
    #
    #   2. Expand to 1: To match the latter, start a new search in each
    #      subfolder and keep the globstar fragment in the search path.
    #      That will match a/a/b (but not a/a/a/b) for a/**/b, which puts you
    #      back at 1.
    #
    #   3. When there's just one token left, stop searching folders and match
    #      filenames instead.

    if len(search_path) == 0:
        # Search has already used up all its path fragments and reached (past)
        # the bottom of a tree. Nothing to do here.
        return matched_files
    elif len(search_path) == 1:
        # Step 3
        return find_files(path, search_path[0], matched_files)

    listing = os.listdir(path)
    match_any_subfolder = False

    # Step 1
    if search_path[0] == '**':
        search_folder(
            path, search_path[1:], matched_files
        )
        match_any_subfolder = True

    # This little hack keeps paths valid and relative while avoiding a
    # leading dot. (Since They were accessed above with the dot intact.)
    # It's faster than removing ./ from all the strings later.
    path = '' if path == '.' else path

    for item in listing:
        if isdir(os.path.join(path, item)):
            if item in IGNORED_FOLDERS:
                continue

            # Step 2
            if match_any_subfolder:
                search_folder(
                    posixpath.join(path, item), search_path, matched_files
                )
            # No globstar in this fragment
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
    file_glob = re.sub(r'(\*\*/){2,}', '**/', file_glob)
    file_glob = re.sub(r'^\.{1,2}[\\/]+', '', file_glob)

    tests = []
    search_path = tokenize_glob(file_glob)

    return search_folder(root, search_path, tests)
