"""An example application using Confit for configuration."""
from __future__ import print_function
from __future__ import unicode_literals
import os
import confit
import argparse

template = {
    'library': confit.Filename(),
    'import_write': confit.OneOf([bool, 'true', 'false']),
    'ignore': confit.StrSeq(),
    'plugins': list,

    'paths': {
        'directory': confit.Filename(),
        'default': confit.Filename(relative_to='directory'),
    }
}

config = confit.LazyConfig('ConfitExample', file="~/PycharmProjects/confit/example/config_default.yaml")


def main():
    parser = argparse.ArgumentParser(description='example Confit program')
    parser.add_argument('--library', '-l', dest='library', metavar='LIBPATH',
                        help='library database file')
    parser.add_argument('--directory', '-d', dest='directory',
                        metavar='DIRECTORY',
                        help='destination music directory')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true',
                        help='print debugging messages')

    args = parser.parse_args()
    config.set_args(args)
    # Use a boolean flag and the transient overlay.
    if config['verbose']:
        print('verbose mode')
        config['log']['level'] = 2
    else:
        config['log']['level'] = 0
    print('logging level is', config['log']['level'].get(int))
    valid = config.get(template)

    print(config.dump())

    # Some validated/converted values.
    print('library is', valid.library)
    print('directory is', valid.paths.directory)
    print('paths.default is', valid.paths.default)
