Confit: painless YAML config files that Just Work
=================================================

I’m tired of fiddling around with `ConfigParser`_. I don’t even really
like INI syntax. I’m tired of writing boilerplate code to check for
missing values, fall back to defaults, override config values with
command-line options, and all that. I think a configuration library
should be able to handle a lot more for me.

So I’m writing **Confit** to magically take care of defaults, overrides,
type checking, command-line integration, human-readable errors, and
standard OS-specific locations. The configuration files will be based on
`YAML`_, which is a great syntax for writing down data.

What It Does
------------

Here’s what Confit brings to the table:

-  An **utterly sensible API** resembling dictionary-and-list structures
   but providing **transparent validation** without lots of boilerplate
   code. Type ``config['num_goats'].get(int)`` to get the configured
   number of goats and ensure that it’s an integer.
-  Combine configuration data from **multiple sources**. Using
   *layering*, Confit allows user-specific configuration to seamlessly
   override system-wide configuration, which in turn overrides built-in
   defaults. An in-package ``config_default.yaml`` can be used to
   provide bottom-layer defaults using the same syntax that users will
   see.

-  Look for configuration files in **platform-specific paths**. Like
   ``$XDG_DATA_HOME`` or ``~/.config`` on Unix; “Application Support” on
   Mac OS X; ``%APPDATA%`` on Windows. Your program gets its own
   directory, which you can use to store additional (non-configuration)
   data.

And what it will do (some not-yet-implemented goals):

-  Extensible validation. It should be easy to ensure that a file or
   directory exists, for example.
-  Declarative integration with command-line options (`optparse`_ or
   `argparse`_). Command-line options should be able to easily form
   another “layer” on top of config files.
-  Helpers to create a platform-specific data directory if it doesn’t
   exist yet.
-  A pattern for easily creating singleton configuration objects. It
   should be easy for any part of the code to access the current
   configuration—and even for code that *uses the configured program as
   a library* to get its configuration. There are two ways I can imagine
   doing this:

   -  Like `logging`_, provide a ``confit.get_config(name)`` function to
      get singleton configuration objects by name.
   -  Encourage developers to put ``config = confit.make_config(...)``
      in their root module (or somewhere else well-known). Then each
      client can just say ``import myapp; myapp.config``.

Using Confit
------------

`Confit’s documentation`_ describes its API in detail.

Author
------

Confit is being developed by `Adrian Sampson`_. It’s not done yet, but
you’re welcome to use it under the terms of the `MIT license`_. I’m
building Confit to use it with a future version of `beets`_.

.. _ConfigParser: http://docs.python.org/library/configparser.html
.. _YAML: http://yaml.org/
.. _optparse: http://docs.python.org/dev/library/optparse.html
.. _argparse: http://docs.python.org/dev/library/argparse.html
.. _logging: http://docs.python.org/library/logging.html
.. _Confit’s documentation: http://confit.readthedocs.org/
.. _Adrian Sampson: https://github.com/sampsyo
.. _MIT license: http://www.opensource.org/licenses/mit-license.php
.. _beets: https://github.com/sampsyo/beets
