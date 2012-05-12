"""An example application using Confit for configuration."""
from __future__ import print_function
import confit

def main():
    config = confit.config('ConfitExample', __name__)
    print(config['foo'].get())
