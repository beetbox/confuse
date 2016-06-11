from setuptools import setup
import os


def _read(fn):
    path = os.path.join(os.path.dirname(__file__), fn)
    return open(path).read()


setup(
    name='confuse',
    version='0.4.0',
    description='painless YAML configuration',
    author='Adrian Sampson',
    author_email='adrian@radbox.org',
    url='https://github.com/sampsyo/confuse',
    license='MIT',
    platforms='ALL',
    long_description=_read("README.rst"),
    install_requires=[
        'pyyaml'
    ],
    py_modules=['confuse'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
