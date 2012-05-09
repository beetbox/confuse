"""An example application using Confit for configuration."""
import confit

def main():
    config = confit.config('ConfitExample', __name__)
    print config['foo'].get()
