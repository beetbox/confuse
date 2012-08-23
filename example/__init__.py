"""An example application using Confit for configuration."""
from __future__ import print_function
from __future__ import unicode_literals
import confit
import argparse

def main():
    config = confit.config('ConfitExample', __name__)

    parser = argparse.ArgumentParser(description='test program for Confit')
    parser.add_argument('--foo', dest='foo', metavar='BAR',
                        help='a parameter')

    parser.parse_args(namespace=config.arg_namespace)
    print(config['foo'].get())
