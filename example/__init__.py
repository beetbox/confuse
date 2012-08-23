"""An example application using Confit for configuration."""
from __future__ import print_function
from __future__ import unicode_literals
import confit
import argparse

def main():
    config = confit.config('ConfitExample', __name__)

    parser = argparse.ArgumentParser(description='example Confit program')
    parser.add_argument('--library', '-l', dest='library', metavar='LIBPATH',
                        help='library database file')
    parser.add_argument('--directory', '-d', dest='directory',
                        metavar='DIRECTORY',
                        help='destination music directory')
    parser.add_argument('--verbose', '-v', dest='verbose', action='store_true',
                        help='print debugging messages')

    parser.parse_args(namespace=config.arg_namespace)

    if config['verbose'].get(bool):
        print('verbose mode')
    print('directory is', config['directory'].get(confit.as_filename))
    print('library is', config['library'].get(confit.as_filename))
