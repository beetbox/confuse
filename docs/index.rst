Confit: Painless Configuration
==============================

`Confit`_ (*con-FEE*) is a straightforward, full-featured configuration system
for Python.

.. _Confit: https://github.com/sampsyo/confit


Using Confit
------------

To set up your configuration object, which provides unified access to
all of your application’s config settings, use ``confit.config()``::

    config = confit.config('MyGreatApp', __name__)

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


Command-Line Options
--------------------

Arguments to command-line programs can be seen as just another *source*
for configuration options. Just as options in a user-specific
configuration file should override those from a system-wide config,
command-line options should take priority over all configuration files.

You can use the `argparse`_ module from the standard library with Confit
to accomplish this. Root view objects have a ``arg_namespace`` property
that can be used with an ArgumentParser's `parse_args`_ method. Just
call it like this::

    parser.parse_args(namespace=config.arg_namespace)

and all of the options will become a top-level source in your
configuration. The key associated with each option in the parser will
become a key available in your configuration. For example, consider this
script::

    config = confit.config('myapp')
    parser = argparse.ArgumentParser()
    parser.add_argument('--foo', help='a parameter')
    parser.parse_args(namespace=config.arg_namespace)
    print(config['foo'].get())

This will allow the user to override the configured value for key
``foo`` by passing ``--foo <something>`` on the command line.

.. _argparse: http://docs.python.org/dev/library/argparse.html
.. _parse_args: http://docs.python.org/library/argparse.html#the-parse-args-method
