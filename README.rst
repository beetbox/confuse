Confuse: painless YAML config files that Just Work
==================================================

.. image:: https://travis-ci.org/sampsyo/confuse.svg?branch=master
    :target: https://travis-ci.org/sampsyo/confuse

.. image:: http://img.shields.io/pypi/v/confuse.svg
    :target: https://pypi.python.org/pypi/confuse


I'm tired of fiddling around with `ConfigParser`_. I don’t even really
like INI syntax. I'm tired of writing boilerplate code to check for
missing values, fall back to defaults, override config values with
command-line options, and all that. I think a configuration library
should be able to handle a lot more for me.

So I'm writing **Confuse** to magically take care of defaults, overrides,
type checking, command-line integration, human-readable errors, and
standard OS-specific locations. The configuration files will be based on
`YAML`_, which is a great syntax for writing down data.

What It Does
------------

Here’s what Confuse brings to the table:

-  An **utterly sensible API** resembling dictionary-and-list structures
   but providing **transparent validation** without lots of boilerplate
   code. Type ``config['num_goats'].get(int)`` to get the configured
   number of goats and ensure that it’s an integer.

-  Combine configuration data from **multiple sources**. Using
   *layering*, Confuse allows user-specific configuration to seamlessly
   override system-wide configuration, which in turn overrides built-in
   defaults. An in-package ``config_default.yaml`` can be used to
   provide bottom-layer defaults using the same syntax that users will
   see. A runtime overlay allows the program to programmatically
   override and add configuration values.

-  Look for configuration files in **platform-specific paths**. Like
   ``$XDG_CONFIG_HOME`` or ``~/.config`` on Unix; "Application Support" on
   Mac OS X; ``%APPDATA%`` on Windows. Your program gets its own
   directory, which you can use to store additional data. You can
   transparently create this directory on demand if, for example, you
   need to initialize the configuration file on first run. And an
   environment variable can be used to override the directory's
   location.

-  Integration with **command-line arguments** via `argparse`_ or `optparse`_
   from the standard library. Use argparse's declarative API to allow
   command-line options to override configured defaults.

Using Confuse
-------------

`Confuse's documentation`_ describes its API in detail.

Author
------

Confuse is being developed by `Adrian Sampson`_. It’s not done yet, but
you’re welcome to use it under the terms of the `MIT license`_. Confuse was
originally made to power `beets`_.

.. _ConfigParser: http://docs.python.org/library/configparser.html
.. _YAML: http://yaml.org/
.. _optparse: http://docs.python.org/dev/library/optparse.html
.. _argparse: http://docs.python.org/dev/library/argparse.html
.. _logging: http://docs.python.org/library/logging.html
.. _Confuse’s documentation: http://confuse.readthedocs.org/
.. _Adrian Sampson: https://github.com/sampsyo
.. _MIT license: http://www.opensource.org/licenses/mit-license.php
.. _beets: https://github.com/beetbox/beets
