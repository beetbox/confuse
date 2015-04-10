Confit: Painless Configuration
==============================

`Confit`_ (*con-FEE*) is a straightforward, full-featured configuration
library written in Python.

.. _Confit: https://github.com/sampsyo/confit

When to Use Confit
------------------

Confit abstracts the process of compiling a runtime configuration. In this
context, a configuration holds values that would otherwise be hard coded
into your application or library. Common examples include:

- A host and port for a remote service.
- A username and password for a remote service.
- A port number to bind.
- A timeout in milliseconds.
- A path to a temporary directory.
- A log level.

Configurations are distinct from data, although the line is hard to define.
In our approximation, an application can run without data, but it cannot run
without a configuration. A configuration can be packaged and imported, but
data cannot.


Features
--------


- Put your **default configuration in code** so that your application or
  library will run out of the box.
- Easily let your users **override the configuration** with **command-line
  arguments, environment variables, and configuration files in multiple
  formats**.
- Define your own **custom sources**, e.g., for reading configuration from a
  database.
- Choose a precedence order for **any number or combination of sources** that
  make sense for you.
- Easily **type check and validate** configuration overrides and emit **human
  readable errors** that point users to the offending overrides.
- Look for configuration files in **platform-specific paths** like
  ``$XDG_CONFIG_HOME`` or ``~/.config`` on Unix; ``Application Support`` on
  Mac OS X; and ``%APPDATA%`` on Windows.


Examples
--------

Hello World
^^^^^^^^^^^

::

  1| import confit
  2| default_config = confit.from_mapping({'greeting': 'Hello, world!'})
  3| sys_config = confit.from_yaml('/etc/example.yml')
  4| config = default_config + sys_config
  5| config['greeting'].get(str)

Let's step through each line in this example:

1. Import Confit.
2. Create a configuration from code---that is, from a mapping literal. It
   will serve as our default.
3. Read a configuration from a `YAML`_ file in the system configuration
   directory.
4. Compose the two configurations by laying the system configuration over the
   default configuration. Every variable in the system configuration will
   override the ones in the default.
5. Read a string variable from the configuration.

.. _YAML: http://yaml.org/

This example is just enough to get a taste for Confit. Details are explained
in later sections.


Git
^^^

To demonstrate the full power of Confit, consider the `configuration model
for Git <http://git-scm.com/docs/git-config#FILES>`_.

::

  from_git_ini = lambda path: confit.from_ini(path, sep=".")
  sys_config = from_git_ini(confit.sys_config_path("git", "config"))
  second_user_config = sum(map(from_git_ini, confit.user_config_paths("git", "config")))
  first_user_config = from_git_ini(os.expanduser("~/.gitconfig"))
  repo_config = from_git_ini(os.path.join(git_dir(), "config"))
  # Git takes configuration from environment variables with names different
  # from the configuration variables they map to. That requires some custom
  # (but simple) logic not built in to Confit. It is left as an exercise for
  # the reader.
  env_config = ...
  config = sum((defaults, sys_config, second_user_config, first_user_config, repo_config, env_config))


curl
^^^^

Confit is useful for libraries in addition to applications. Consider libcurl,
which loads configuration from `~/.curlrc` and special environment variables
(`http_proxy`, `https_proxy`, `no_proxy`, etc). Libraries can use all the
facilities of Confit (with the exception of ``from_args``) to ease handling
of their configuration.


Configuration
-------------

A configuration consists of variable bindings. In each new project, a
configuration is born when some variable holds an arbitrary value, e.g.  a
path to a temporary directory. The value is moved to the configuration as a
default, and the variable's value is loaded from the configuration.

Variables
^^^^^^^^^

In Confit, a configuration is an immutable mapping from string names to
*variables*. Variables have two methods, ``get`` and ``origin``.

::

  get(cast=lambda x: x)

Call *cast* with the variable's value and return the result. *cast* is useful
for casting the value to a different type (i.e., "get the value as a ___").
*cast* may also check the value against some validity criteria, e.g. whether
a string can be parsed, or whether an integer fits within a range. If *cast*
raises an exception, then it will be wrapped in a ``ConfitCastError``, that,
if uncaught, will be pretty-printed to the console (using ``sys.excepthook``)
indicating both the failing call to ``get`` and the origin of the faulty
value::

  /usr/bin/script:123:
      port = config['port'].get(is_not_privileged)
  failed on the override at /home/user/.example.yml:8:
  port: 80

::

  origin()

Return the variable's origin. An **origin** is a location identifier for an
individual variable within a given source (see Sources section). Each origin
type may have different properties, but every built-in origin can be
pretty-printed with its ``__str__`` method.


Sources
-------

Configurations come from **sources**, e.g. command-line arguments,
environment variables, or files. Confit comes with a few functions for
creating configurations from well-known sources.

::

  from_mapping(mapping)

Return a configuration taken from a mapping from string names to values. Each
variable will have a ``FileOrigin`` pointing to the call to this function.

::

  from_object(object)

Return a configuration drawn from the non-callable public properties of
*object*. A property is considered public if its name does not start with an
underscore. Each variable will have a ``FileOrigin`` pointing to the call to
this function.

::

  from_yaml(path)

Return a configuration parsed from a YAML file at *path*, or if *path* is not
a file, return an empty configuration. Each variable will have a
``FileOrigin``. Can be used to parse JSON as well since YAML is a superset.

::

  from_ini(path, sep="_")

Return a configuration parsed from an INI file at *path*, or if *path* is not
a file, return an empty configuration. Each variable will have a
``FileOrigin``, and its key will be prefixed by its section name separated by
*sep*.

::

  user_config_paths(*paths)

Return a list of paths to user-specific configuration directories
conventional for the current platform, with *paths* appended to each using
``os.path.join``.

OS X    | ``~/.config``, ``~/Library/Application Support``
Unix    | ``$XDG_CONFIG_HOME``, ``~/.config``
Windows | ``%HOME%\AppData\Roaming``

::

  sys_config_path(*paths)

Return path to the system-wide configuration directory (shared by all users)
conventional for the current platform, with *paths* appended using
``os.path.join``.

Unix, OS X | ``/etc``
Windows    | ``%APPDATA%``

::

  module_dir(module_name)

Return the path to the directory where the named module is found.

::

  from_env(prefix, sep="_")

Return a configuration pulled from the environment. For each environment
variable whose name has the given *prefix*, the configuration will have a
variable whose name is everything after the *prefix* with underscores
replaced by *sep* (see caveat at the end of this description), whose value is
a string, and whose origin is an ``EnvironmentOrigin``.

Environment overrides are handy for scripts that cannot create a
configuration file (or cannot edit an existing one) and cannot change the
command line before invoking your application.

One notable caveat is that most shells have a limited character set for
environment variable names. Often, the OS will support all non-null
characters, but shells will only support letters, numbers, and underscores.
In those cases, environment variables can be used to override only variables
with "well behaved names". To help overcome this limitation, this source
supports overriding variables with non-underscore separators using the *sep*
argument.

::

  from_args(argv, prefix)

Return a pair. The first half will be a configuration parsed from the command
line long options in *argv* that have the given *prefix*. Each variable will
have a ``CommandLineOrigin``. The second half will be the remaining unparsed
command line arguments in the same order they appeared. Example::

  (config, args) = confit.from_args(["a", "--eg-hello", "world", "b"], "eg")
  config["hello"].get() # "world"
  args # ["a", "b"]

::

  class confit.FileOrigin(filename, line, [column])

::

  class confit.EnvironmentOrigin(variable)

::

  class confit.CommandLineOrigin(option)


Custom sources
^^^^^^^^^^^^^^

To extend this set with your own custom source, define a function that
returns a configuration::

  class confit.Configuration(config)

*config* should be a mapping from variable names to (value, origin) pairs.
For origins that do not fit the built-in types, consider defining your own
origin class. If you do, it is best practice to define a pretty-printing
``__str__`` method.


Composition
-----------

Configurations can be composed with the addition operator::

  config = defaults + overrides

The result of this will be a new configuration with a union of the variables
in ``overrides`` and ``defaults`` with the values and origins from
``overrides`` taking precedence.

``defaults`` and ``overrides`` themselves can be compositions, creating a
tree of configurations. Generally, due to the left associativity of the ``+``
operator in Python, only ``defaults`` will be a composition, creating a
sequence. Summing an iterable of configurations will compose them from left
to right, in order of lowest precedence to highest precedence.

Variables have a third method that becomes useful in the context of
compositions. ``stack`` will return a list, in precedence order starting with
most preferred, of all the variable definitions in the configuration tree::

  assert config['var'].stack()[0].get() == config['var'].get()

.. note:: Programmatic updates simplify in the face of composition.
  ``config["var"].add(value)`` becomes
  ``config + confit.from_mapping({"var": value})``, which I think we can even
  simplify to ``config + {"var": value}``.
  ``config["var"].set(value)`` becomes
  ``confit.from_mapping({"var": value}) + config``, which I don't think we
  can simplify due to the associativity of addition in Python.


Casts
-----

Confit comes with a few built-in casts.

::

  as_bool

Return ``True`` for non-zero integers, ``"t"``, ``"true"``, ``"on"``, and
``"yes"``; return ``False`` for ``0``, ``"f"``, ``"false"``, ``"off"``, and
``"no"``. String values are case insensitive.

::

  as_int(check=None)
  as_float(check=None)

Return an integer or float after asserting *check* on it. If the underlying
value is a string, it will be strictly parsed as an integer or float (after
stripping surrounding whitespace). A common use for *check* is a range check,
e.g.  ``lambda x: 1 <= x <= 10``.

::

  as_str(regex)

Return a string if it matches the regular expression.

::

  as_strs(split=str.split)

Given either a string or a list of strings, return a list of strings. A
single string is split using *split*; the default splits on whitespace.

::

  as_date(formats)

::

  as_time(formats)

::

  as_datetime(formats)

::

  as_filename

Return a filename, substituting tildes and absolute-ifying relative paths.
The filename is relative to the source that provided it. That is, a relative
path in a file (including a Python module) is relative to the directory
containing the file. A relative path in a command-line argument or an
environment variable is relative to the current working directory.

::

  as_choice(choices)

Assert the value is among the *choices* (using the ``in`` operator) and, if
*choices* is a ``dict``, return the associated value.


Custom casts
^^^^^^^^^^^^

It is easy to define your own casts. A cast is just a function that takes a
stack of variables, in precedence order starting with most preferred, and
returns a value or raises an exception.

.. note:: The stack is necessary to implement as_filename as a function
  separate from the Configuration interface. To support user-defined casts,
  they must be separate from the interface, and to prevent built-in casts
  from enjoying "privileged" status such that user-defined casts cannot do
  all the same things, they must be separate from the interface as well.
  Without the stack, as_filename cannot read the file origin of a variable to
  perform relative path resolution. However, demanding that casts accept a
  stack means that built-in types, e.g. int, bool, float, cannot be used as
  casts; users have to remember to use as_int, as_bool, as_float. It might be
  an acceptable trade-off.


Miscellaneous
-------------

::

  type_check(config, onerror="raise")

Check that the type of the most preferred value (final override) matches the
type of the least preferred value (default) for each variable. If a mismatch
is found, take the action described in *onerror*, chosen from among the
following:

"raise" | Raise a ``TypeError``.
"warn"  | Call ``logging.warning``.

::

  flatten(config, casts=None)

Return a mapping from variable names to their most preferred value, passing
them through the given *casts*. By flattening, you can cast variables once
and use them many times, or dump a configuration to file in whatever format
you want.


YAML Tweaks
-----------

Confit uses the `PyYAML`_ module to parse YAML configuration files. However, it
deviates very slightly from the official YAML specification to provide a few
niceties suited to human-written configuration files. Those tweaks are:

.. _pyyaml: http://pyyaml.org/

- All strings are returned as Python Unicode objects.
- YAML maps are parsed as Python `OrderedDict`_ objects. This means that you
  can recover the order that the user wrote down a dictionary.
- Bare strings can begin with the % character. In stock PyYAML, this will throw
  a parse error.

.. _OrderedDict: http://docs.python.org/2/library/collections.html#collections.OrderedDict


Configuring Large Programs
--------------------------

One problem that must be solved by a configuration system is the issue
of global configuration for complex applications. In a large program
with many components and many configuration options, it can be unwieldy to
explicitly pass configuration values from component to component. You
quickly end up with monstrous function signatures with dozens of keyword
arguments, decreasing code legibility and testability.

In such systems, one option is to pass a single `Configuration` object
through to each component. To avoid even this, however, it's sometimes
appropriate to use a little bit of shared global state. As evil as
shared global state usually is, configuration is (in my opinion) one
valid use: since configuration is mostly read-only, it's relatively
unlikely to cause the sorts of problems that global values sometimes
can. And having a global repository for configuration options can vastly
reduce the amount of boilerplate threading-through needed to explicitly
pass configuration from call to call.

To use global configuration, consider creating a configuration object in
a well-known module (say, the root of a package). Since this object
will be initialized during module import, all built-in file sources in Confit
are lazy. (Doing complicated stuff like parsing YAML during module import is
generally considered a Bad Idea.)

Global state can cause problems for unit testing. To alleviate this,
consider adding code to your test fixtures (e.g., `setUp`_ in the
`unittest`_ module) that re-assigns the defaults to your module's
configuration. Your tests can then modify the global configuration values
without affecting other tests since these modifications will be cleared out
before the next test runs. This won't alleviate issues with concurrent tests,
however; that problem is fundamental to global state.


