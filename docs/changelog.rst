Changelog
=========

Changelog goes here! Please add your entry to the bottom of one of the lists
below!

.. Uncomment the relevant section when you add the first entry

Unreleased
----------

v2.2.1
------

- Narrow `Path` template shorthand handling to concrete `pathlib.Path` values
  for more accurate type checking.
- Fix `confuse.Path` which now points to `confuse.templates.Path` instead of
  `pathlib.Path`.

Other changes
~~~~~~~~~~~~~

- Require `typing_extensions` on older Python versions (and use `typing` on
  newer versions). [#189](https://github.com/beetbox/confuse/issues/189)

2.2.0 (January 28, 2026)
------------------------

New features
~~~~~~~~~~~~

- Ship inline type information via a `py.typed` marker for type checkers.
- Tighten and extend type hints across the public API, templates, and sources.

Other changes
~~~~~~~~~~~~~

- Drop support for Python 3.9.
- Add strict mypy configuration and align tests/examples with the new typing.
- Include `docs` and `tests` directory in source distributions.

2.1.0 (October 27, 2025)
------------------------

New features
~~~~~~~~~~~~

- Added typehints to `as_*` functions which allows for enhanced type checking
  and IDE support.

Other changes
~~~~~~~~~~~~~

- Drop support for versions of Python below 3.9.
- Removed 'u' prefix from string literals for Python 3.0+ compatibility.
- Removed a number of python 2 leftovers.
- Removed deprecated `pkgutil.get_loader` usage in favor of
  `importlib..util.find_spec` for better compatibility with modern Python
  versions.
- Added a minimal release workflow for GitHub Actions to automate the release
  process.
- Added support for Python 3.13 and Python 3.14.
- Modernized package and tests setup.

2.0.1 (April 01, 2023)
----------------------

Other changes
~~~~~~~~~~~~~

- Remove a `<4` Python version requirement bound.

2.0.0 (July 16, 2022)
---------------------

Other changes
~~~~~~~~~~~~~

- Drop support for versions of Python below 3.6.

1.7.0 (November 27, 2021)
-------------------------

New features
~~~~~~~~~~~~

- Add support for reading configuration values from environment variables (see
  `EnvSource`).

Bug fixes
~~~~~~~~~

- Resolve a possible race condition when creating configuration directories.

1.6.0 (September 26, 2021)
--------------------------

New features
~~~~~~~~~~~~

- A new `Configuration.reload` method makes it convenient to reload and re-parse
  all YAML files from the file system.

1.5.0 (June 28, 2021)
---------------------

New features
~~~~~~~~~~~~

- A new `MappingValues` template behaves like `Sequence` but for mappings with
  arbitrary keys.
- A new `Optional` template allows other templates to be null.
- `Filename` templates now have an option to resolve relative to a specific
  directory. Also, configuration sources now have a corresponding global option
  to resolve relative to the base configuration directory instead of the
  location of the specific configuration file.

Bug fixes
~~~~~~~~~

- There is a better error message for `Sequence` templates when the data from
  the configuration is not a sequence.

1.4.0 (November 21, 2020)
-------------------------

Bug fixes
~~~~~~~~~

- `pathlib.PurePath` objects can now be converted to `Path` templates.
- `AttrDict` now properly supports (over)writing attributes via dot notation.

1.3.0 (June 27, 2020)
---------------------

New features
~~~~~~~~~~~~

- When using `None` as a template, the result is a value whose default is
  `None`. Previously, this was equivalent to leaving the key off entirely, i.e.,
  a template with no default. To get the same effect now, use `confuse.REQUIRED`
  in the template.

Other changes
~~~~~~~~~~~~~

- Break up the `confuse` module into a package. (All names should still be
  importable from `confuse`.)

1.2.0 (June 26, 2020)
---------------------

New features
~~~~~~~~~~~~

- `float` values (like ``4.2``) can now be used in templates (just like ``42``
  works as an `int` template).
- It's now possible to provide custom PyYAML `Loader` objects for parsing config
  files.

Bug fixes
~~~~~~~~~

- The `Filename` and `Path` templates now correctly accept default values.

1.1.0 (April 08, 2020)
----------------------

New features
~~~~~~~~~~~~

- A new ``Path`` template produces a pathlib_ Path object.
- String templates support environment variable expansion.

Other changes
~~~~~~~~~~~~~

- Drop support for Python 3.4 (following in the footsteps of PyYAML).

.. _pathlib: https://docs.python.org/3/library/pathlib.html

1.0.0 (May 30, 2019)
--------------------

Other changes
~~~~~~~~~~~~~

The first stable release, and the first that beets_ depends on externally.

.. _beets: https://beets.io
