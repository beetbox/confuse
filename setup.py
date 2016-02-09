from setuptools import setup
import os
import sys


def _read(fn):
    path = os.path.join(os.path.dirname(__file__), fn)
    return open(path).read()


reqs = ['pyyaml']
if sys.version_info[0] <= 2 and sys.version_info[1] < 7:
    reqs.append('ordereddict')

setup(
    name='confuse',
    version='0.3.1',
    description='painless YAML configuration',
    author='Adrian Sampson',
    author_email='adrian@radbox.org',
    url='https://github.com/TechnicalBro/confit',
    license='MIT',
    platforms='ALL',
    long_description=_read("README.rst"),

    install_requires=reqs,
    packages=[
        'confit'
    ],
    # py_modules=['confit'],

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
)
