Changelog
---------

v1.6.0
''''''

- A new `Configuration.reload` method makes it convenient to reload and
  re-parse all YAML files from the file system.

v1.5.0
''''''

- A new `MappingValues` template behaves like `Sequence` but for mappings with
  arbitrary keys.
- A new `Optional` template allows other templates to be null.
- `Filename` templates now have an option to resolve relative to a specific
  directory. Also, configuration sources now have a corresponding global
  option to resolve relative to the base configuration directory instead of
  the location of the specific configuration file.
- There is a better error message for `Sequence` templates when the data from
  the configuration is not a sequence.

v1.4.0
''''''

- `pathlib.PurePath` objects can now be converted to `Path` templates.
- `AttrDict` now properly supports (over)writing attributes via dot notation.

v1.3.0
''''''

- Break up the `confuse` module into a package. (All names should still be
  importable from `confuse`.)
- When using `None` as a template, the result is a value whose default is
  `None`. Previously, this was equivalent to leaving the key off entirely,
  i.e., a template with no default. To get the same effect now, use
  `confuse.REQUIRED` in the template.

v1.2.0
''''''

- `float` values (like ``4.2``) can now be used in templates (just like
  ``42`` works as an `int` template).
- The `Filename` and `Path` templates now correctly accept default values.
- It's now possible to provide custom PyYAML `Loader` objects for
  parsing config files.

v1.1.0
''''''

- A new ``Path`` template produces a `pathlib`_ Path object.
- Drop support for Python 3.4 (following in the footsteps of PyYAML).
- String templates support environment variable expansion.

.. _pathlib: https://docs.python.org/3/library/pathlib.html

v1.0.0
''''''

The first stable release, and the first that `beets`_ depends on externally.

.. _beets: https://beets.io
