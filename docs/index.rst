Confit: Painless Configuration
==============================

`Confit`_ (*con-FEE*) is a straightforward, full-featured configuration system
for Python.

.. _Confit: https://github.com/sampsyo/confit


Using Confit
------------

Set up your Configuration object, which provides unified access to
all of your application’s config settings::

    config = confit.Configuration('MyGreatApp', __name__)

The first parameter is required; it’s the name of your application that
will be used to search the system for config files. The second parameter
is optional: it’s the name of a module that will guide the search for a
*defaults* file. Use this if you want to include a
``config_defaults.yaml`` file inside your package. (The included
``example`` package does exactly this.)

Now, you can access your configuration data as if it were a simple
structure consisting of nested dicts and lists—except that you need to
call the method ``.get()`` on the leaf of this tree to get the result as
a value::

    value = config['foo'][2]['bar'].get()

Under the hood, accessing items in your configuration tree builds up a
*view* into your app’s configuration. Then, ``get()`` flattens this view
into a file, performing a search through each configuration data source
to find an answer. More on view later.

If you know that a configuration value should have a specific type, just
pass that type to ``get()``::

    int_value = config['number_of_goats'].get(int)

This way, Confit will either give you an integer or raise a
``ConfigTypeError`` if the user has messed up the configuration. You’re
safe to assume after this call that ``int_value`` has the right type. If
the key doesn’t exist in any configuration file, Confit will raise a
``NotFoundError``. Together, catching these exceptions (both subclasses
of ``confit.ConfigError``) lets you painlessly validate the user’s
configuration as you go.


View Theory
-----------

The Confit API is based on the concept of *views*. You can think of a
view as a *place to look* in a config file: for example, one view might
say “get the value for key ``number_of_goats``”. Another might say “get
the value at index 8 inside the sequence for key ``animal_counts``”. To
get the value for a given view, you *resolve* it by calling the
``get()`` method.

This concept separates the specification of a location from the
mechanism for retrieving data from a location. (In this sense, it’s a
little like `XPath`_: you specify a path to data you want and *then* you
retrieve it.)

Using views, you can write ``config['animal_counts'][8]`` and know that
no exceptions will be raised until you call ``get()``, even if the
``animal_counts`` key does not exist. More importantly, it lets you
write a single expression to search many different data sources without
preemtively merging all sources together into a single data structure.

Views also solve an important problem with overriding collections.
Imagine, for example, that you have a dictionary called
``deliciousness`` in your config file that maps food names to tastiness
ratings. If the default configuration gives carrots a rating of 8 and
the user’s config rates them a 10, then clearly
``config['deliciousness']['carrots'].get()`` should return 10. But what
if the two data sources have different sets of vegetables? If the user
provides a value for broccoli and zucchini but not carrots, should
carrots have a default deliciousness value of 8 or should Confit just
throw an exception? With Confit’s views, the application gets to decide.

The above expression, ``config['deliciousness']['carrots'].get()``,
returns 10 (falling back on the default). However, you can also write
``config['deliciousness'].get()``. This expression will cause the
*entire* user-specified mapping to override the default one, providing a
dict object like ``{'broccoli': 7, 'zucchini': 9}``. As a rule, then,
resolve a view at the same granularity you want config files to override
each other.

.. _XPath: http://www.w3.org/TR/xpath/


Validation
----------

We saw above that you can easily assert that a configuration value has a
certain type by passing that type to ``get()``. But sometimes you need
to do more than just type checking. For this reason, Confit provides a
few methods on views that perform fancier validation or even
conversion:

* ``as_filename()``: Normalize a filename, substituting tildes and
  absolute-ifying relative paths.
* ``as_choice(choices)``: Check that a value is one of the provided
  choices. The argument should be a list of possible values.
* ``as_number()``: Raise an exception unless the value is of a numeric
  type.
* ``as_pairs()``: Get a collection as a list of pairs. The collection
  should be a list of elements that are either pairs (i.e., two-element
  lists) already or single-entry dicts. This can be helpful because, in
  YAML, lists of single-element mappings have a simple syntax (``- key:
  value``) and, unlike real mappings, preserve order.

For example, ``config['path'].as_filename()`` ensures that you get a
reasonable filename string from the configuration. And calling
``config['direction'].as_choice(['up', 'down'])`` will raise a
``ConfigValueError`` unless the ``direction`` value is either "up" or
"down".


Command-Line Options
--------------------

Arguments to command-line programs can be seen as just another *source*
for configuration options. Just as options in a user-specific
configuration file should override those from a system-wide config,
command-line options should take priority over all configuration files.

You can use the `argparse`_ and `optparse`_ modules from the standard
library with Confit to accomplish this. Just call the ``add_args``
method on your Configuration object and pass in the object returned by the
command-line parsing library. For example, with argparse::

    args = parser.parse_args()
    config.add_args(args)

Correspondingly, with optparse::

    options, args = parser.parse_args()
    config.add_args(options)

This call will turn all of the command-line options into a top-level
source in your configuration. The key associated with each option in the
parser will become a key available in your configuration. For example,
consider this argparse script::

    config = confit.Configuration('myapp')
    parser = argparse.ArgumentParser()
    parser.add_argument('--foo', help='a parameter')
    args = parser.parse_args()
    config.add_args(args)
    print(config['foo'].get())

This will allow the user to override the configured value for key
``foo`` by passing ``--foo <something>`` on the command line.

.. _argparse: http://docs.python.org/dev/library/argparse.html
.. _parse_args: http://docs.python.org/library/argparse.html#the-parse-args-method
.. _optparse: http://docs.python.org/library/optparse.html

Note that, while you can use the full power of your favorite
command-line parsing library, you'll probably want to avoid specifying
defaults in your argparse or optparse setup. This way, Confit can use
other configuration sources---possibly your
``config_defaults.yaml``---to fill in values for unspecified
command-line switches. Otherwise, the argparse/optparse default value
will hide options configured elsewhere.


Search Paths
------------

Confit looks in a number of locations for your application's
configurations. The locations are determined by the platform. For each
platform, Confit has a list of directories in which it looks for a
directory named after the application. For example, the first search
location on Unix-y systems is ``$XDG_CONFIG_HOME/AppName`` for an
application called ``AppName``.

Users can also add an override configuration directory with an
environment variable. The variable name is the application name in
capitals with "DIR" appended: for an application named ``AppName``, the
environment variable is ``APPNAMEDIR``.


Your Application Directory
--------------------------

Confit provides a simple helper, ``Configuration.config_dir()``, that
gives you a directory used to store your application's configuration. If
a configuration file exists in any of the searched locations, then the
highest-priority directory containing a config file is used. Otherwise,
a directory is created for you and returned. So you can always expect
this method to give you a directory that actually exists.

As an example, you may want to migrate a user's settings to Confit from
an older configuration system such as `ConfigParser`_. Just do something
like this::

    config_filename = os.path.join(config.config_dir(),
                                   confit.CONFIG_FILENAME)
    with open(config_filename, 'w') as f:
        yaml.dump(migrated_config, f)

.. _ConfigParser: http://docs.python.org/library/configparser.html


Transient Updates
-----------------

Occasionally, a program will need to modify its configuration while it's
running. For example, an interactive prompt from the user might cause
the program to change a setting for the current execution only. Or the
program might need to add a *derived* configuration value that the user
doesn't specify.

To facilitate this, Confit uses a *transient overlay* system. You can
set the value at any view using ordinary Python assignment. This setting
will add to an overlay that precedes all other configuration sources in
priority. Here's an example of programmatically setting a configuration
value based on a ``DEBUG`` constant::

    if DEBUG:
        config['verbosity'] = 100
    ...
    my_logger.setLevel(config['verbosity'].get(int))

This example allows the constant to override the default verbosity
level, which would otherwise come from a configuration file.
