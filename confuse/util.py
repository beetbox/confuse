from __future__ import division, absolute_import, print_function

import os
import sys
import argparse
import optparse
import platform
import pkgutil


PY3 = sys.version_info[0] == 3
STRING = str if PY3 else unicode  # noqa: F821
BASESTRING = str if PY3 else basestring  # noqa: F821
NUMERIC_TYPES = (int, float) if PY3 else (int, float, long)  # noqa: F821


UNIX_DIR_FALLBACK = '~/.config'
WINDOWS_DIR_VAR = 'APPDATA'
WINDOWS_DIR_FALLBACK = '~\\AppData\\Roaming'
MAC_DIR = '~/Library/Application Support'


def iter_first(sequence):
    """Get the first element from an iterable or raise a ValueError if
    the iterator generates no values.
    """
    it = iter(sequence)
    try:
        return next(it)
    except StopIteration:
        raise ValueError()


def namespace_to_dict(obj):
    """If obj is argparse.Namespace or optparse.Values we'll return
      a dict representation of it, else return the original object.

    Redefine this method if using other parsers.

    :param obj: *
    :return:
    :rtype: dict or *
    """
    if isinstance(obj, (argparse.Namespace, optparse.Values)):
        return vars(obj)
    return obj


# Config file paths, including platform-specific paths and in-package
# defaults.

def find_package_path(name):
    """Returns the path to the package containing the named module or
    None if the path could not be identified (e.g., if
    ``name == "__main__"``).
    """
    # Based on get_root_path from Flask by Armin Ronacher.
    loader = pkgutil.get_loader(name)
    if loader is None or name == '__main__':
        return None

    if hasattr(loader, 'get_filename'):
        filepath = loader.get_filename(name)
    else:
        # Fall back to importing the specified module.
        __import__(name)
        filepath = sys.modules[name].__file__

    return os.path.dirname(os.path.abspath(filepath))


def xdg_config_dirs():
    """Returns a list of paths taken from the XDG_CONFIG_DIRS
    and XDG_CONFIG_HOME environment varibables if they exist
    """
    paths = []
    if 'XDG_CONFIG_HOME' in os.environ:
        paths.append(os.environ['XDG_CONFIG_HOME'])
    if 'XDG_CONFIG_DIRS' in os.environ:
        paths.extend(os.environ['XDG_CONFIG_DIRS'].split(':'))
    else:
        paths.append('/etc/xdg')
    paths.append('/etc')
    return paths


def config_dirs():
    """Return a platform-specific list of candidates for user
    configuration directories on the system.

    The candidates are in order of priority, from highest to lowest. The
    last element is the "fallback" location to be used when no
    higher-priority config file exists.
    """
    paths = []

    if platform.system() == 'Darwin':
        paths.append(UNIX_DIR_FALLBACK)
        paths.append(MAC_DIR)
        paths.extend(xdg_config_dirs())

    elif platform.system() == 'Windows':
        paths.append(WINDOWS_DIR_FALLBACK)
        if WINDOWS_DIR_VAR in os.environ:
            paths.append(os.environ[WINDOWS_DIR_VAR])

    else:
        # Assume Unix.
        paths.append(UNIX_DIR_FALLBACK)
        paths.extend(xdg_config_dirs())

    # Expand and deduplicate paths.
    out = []
    for path in paths:
        path = os.path.abspath(os.path.expanduser(path))
        if path not in out:
            out.append(path)
    return out
