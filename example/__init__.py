"""An example application using Confit for configuration."""
from __future__ import print_function
from __future__ import unicode_literals
import confit
import argparse


config = confit.LazyConfig('ConfitExample', __name__)


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

    print('configuration directory is', config.config_dir())

    # Use a boolean flag and the transient overlay.
    if config['verbose']:
        print('verbose mode')
        config['log']['level'] = 2
    else:
        config['log']['level'] = 0
    print('logging level is', config['log']['level'].get(int))

    # Some validated/converted values.
    print('directory is', config['directory'].as_filename())
    print('library is', config['library'].as_filename())
