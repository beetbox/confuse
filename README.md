Confit: painless YAML config files that Just Work
=================================================

I'm tired of fiddling around with [ConfigParser][]. I don't even really like INI
syntax. I'm tired of writing boilerplate code to check for missing values, fall
back to defaults, override config values with command-line options, and all
that. I think a configuration library should be able to handle a lot more for
me.

So I'm writing **Confit** to magically take care of defaults, overrides, type
checking, command-line integration, human-readable errors, and standard
OS-specific locations. The configuration files will be based on [YAML][], which
is a great syntax for writing down data.

[ConfigParser]: http://docs.python.org/library/configparser.html
[YAML]: http://yaml.org/


What It Does
------------

Here's what Confit brings to the table:

* An **utterly sensible API** resembling dictionary-and-list structures but
  providing **transparent validation** without lots of boilerplate code. Type
  `config['num_goats'].get(int)` to get the configured number of goats and
  ensure that it's an integer.

* Combine configuration data from **multiple sources**. Using *layering*,
  Confit allows user-specific configuration to seamlessly override system-wide
  configuration, which in turn overrides built-in defaults. An in-package
  `config_default.yaml` can be used to provide bottom-layer defaults using the
  same syntax that users will see.

* Look for configuration files in **platform-specific paths**. Like
  `$XDG_DATA_HOME` or `~/.config` on Unix; "Application Support" on Mac OS X;
  `%APPDATA%` on Windows. Your program gets its own directory, which you can
  use to store additional (non-configuration) data.

And what it will do (some not-yet-implemented goals):

* Extensible validation. It should be easy to ensure that a file or directory
  exists, for example.
* Declarative integration with command-line options ([optparse][] or
  [argparse][]). Command-line options should be able to easily form another
  "layer" on top of config files.
* Helpers to create a platform-specific data directory if it doesn't exist yet.
* A pattern for easily creating singleton configuration objects. It should be
  easy for any part of the code to access the current configuration---and even
  for code that *uses the configured program as a library* to get its
  configuration. There are two ways I can imagine doing this:
    * Like [logging][python logging], provide a `confit.get_config(name)`
      function to get singleton configuration objects by name.
    * Encourage developers to put `config = confit.make_config(...)` in their
      root module (or somewhere else well-known). Then each client can just say
      `import myapp; myapp.config`.

[python logging]: http://docs.python.org/library/logging.html
[optparse]: http://docs.python.org/dev/library/optparse.html
[argparse]: http://docs.python.org/dev/library/argparse.html


Using Confit
------------

To set up your configuration object, which provides unified access to all of
your application's config settings, use `confit.config()`:

    config = confit.config('MyGreatApp', __name__)

The first parameter is required; it's the name of your application that will be
used to search the system for config files. The second parameter is optional:
it's the name of a module that will guide the search for a *defaults* file. Use
this if you want to include a `config_defaults.yaml` file inside your package.
(The included `example` package does exactly this.)

Now, you can access your configuration data as if it were a simple structure
consisting of nested dicts and lists—except that you need to call the method
`.get()` on the leaf of this tree to get the result as a value:

    value = config['foo'][2]['bar'].get()

Under the hood, accessing items in your configuration tree builds up a *view*
into your app's configuration. Then, `get()` flattens this view into a file,
performing a search through each configuration data source to find an answer.
More on view later.

If you know that a configuration value should have a specific type, just pass that type to `get()`:

    int_value = config['number_of_goats'].get(int)

This way, Confit will either give you an integer or raise a `ConfigTypeError`
if the user has messed up the configuration. You're safe to assume after this
call that `int_value` has the right type. If the key doesn't exist in any
configuration file, Confit will raise a `NotFoundError`. Together, catching
these exceptions (both subclasses of `confit.ConfigError`) lets you painlessly
validate the user's configuration as you go.

### View Theory

The Confit API is based on the concept of *views*. You can think of a view as
a *place to look* in a config file: for example, one view might say "get the
value for key `number_of_goats`". Another might say "get the value at index 8
inside the sequence for key `animal_counts`". To get the value for a given
view, you *resolve* it by calling the `get()` method.

This concept separates the specification of a location from the mechanism for
retrieving data from a location. (In this sense, it's a little like [XPath][]:
you specify a path to data you want and *then* you retrieve it.)

Using views, you can write `config['animal_counts'][8]` and know that no
exceptions will be raised until you call `get()`, even if the `animal_counts`
key does not exist. More importantly, it lets you write a single expression to
search many different data sources without preemtively merging all sources
together into a single data structure.

Views also solve an important problem with overriding collections. Imagine, for
example, that you have a dictionary called `deliciousness` in your config file
that maps food names to tastiness ratings. If the default configuration gives
carrots a rating of 8 and the user's config rates them a 10, then clearly
`config['deliciousness']['carrots'].get()` should return 10. But what if the
two data sources have different sets of vegetables? If the user provides a
value for broccoli and zucchini but not carrots, should carrots have a default
deliciousness value of 8 or should Confit just throw an exception? With
Confit's views, the application gets to decide.

The above expression, `config['deliciousness']['carrots'].get()`, returns 10
(falling back on the default). However, you can also write
`config['deliciousness'].get()`. This expression will cause the *entire*
user-specified mapping to override the default one, providing a dict object
like `{'broccoli': 7, 'zucchini': 9}`. As a rule, then, resolve a view at the
same granularity you want config files to override each other.


[XPath]: http://www.w3.org/TR/xpath/


Author
------

Confit is being developed by [Adrian Sampson][adrian]. It's not done yet, but
you're welcome to use it under the terms of the [MIT license][]. I'm making
Confit to use it with a future version of [beets][].

[MIT license]: http://www.opensource.org/licenses/mit-license.php
[adrian]: https://github.com/sampsyo
[beets]: https://github.com/sampsyo/beets
