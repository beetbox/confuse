from __future__ import division, absolute_import, print_function

import os
from os import path
import sys
from setuptools.dist import Distribution
from setuptools import setup, Command
import shlex


class CustomDistribution(Distribution):
    def __init__(self, *args, **kwargs):
        self.sdist_requires = None
        Distribution.__init__(self, *args, **kwargs)

    def get_finalized_command(self, command, create=1):
        cmd_obj = self.get_command_obj(command, create)
        cmd_obj.ensure_finalized()
        return cmd_obj

    def export_live_eggs(self, env=False):
        """Adds all of the eggs in the current environment to PYTHONPATH."""
        path_eggs = [p for p in sys.path if p.endswith('.egg')]

        command = self.get_finalized_command("egg_info")
        egg_base = path.abspath(command.egg_base)

        unique_path_eggs = set(path_eggs + [egg_base])

        os.environ['PYTHONPATH'] = ':'.join(unique_path_eggs)


class test(Command):  # noqa: ignore=N801
    """Command to run tox."""

    description = "run tox tests"

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        self.tox_args = ''

    def finalize_options(self):
        pass

    def run(self):
        # Install test dependencies if needed.
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)

        # Add eggs to PYTHONPATH. We need to do this to ensure our eggs are
        # seen by Tox.
        # Without this, Tox can't find it's dependencies.
        self.distribution.export_live_eggs()

        tox = __import__('tox')

        parsed_args = shlex.split(self.tox_args)
        result = tox.cmdline(args=parsed_args)

        sys.exit(result)


def _read(fn):
    path = os.path.join(os.path.dirname(__file__), fn)
    with open(path, "rb") as f:
        data = f.read()

    return data.decode("utf-8")


setup(
    name='confuse',
    version='1.2.0',
    description='painless YAML configuration',
    author='Adrian Sampson',
    author_email='adrian@radbox.org',
    url='https://github.com/beetbox/confuse',
    license='MIT',
    platforms='ALL',
    long_description=_read("README.rst"),
    long_description_content_type='text/x-rst',
    install_requires=['pyyaml'],
    tests_require=['tox', 'pathlib'],
    py_modules=['confuse'],
    cmdclass={'test': test},
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    distclass=CustomDistribution
)
