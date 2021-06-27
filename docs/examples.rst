Template Examples
=================

These examples demonstrate how the confuse templates work to validate
configuration values.


Sequence
--------

A ``Sequence`` template allows validation of a sequence of configuration items
that all must match a subtemplate. The items in the sequence can be simple
values or more complex objects, as defined by the subtemplate. When the view
is defined in multiple sources, the highest priority source will override the
entire list of items, rather than appending new items to the list from lower
sources. If the view is not defined in any source of the configuration, an
empty list will be returned.

As an example of using the ``Sequence`` template, consider a configuration that
includes a list of servers, where each server is required to have a host string
and an optional port number that defaults to 80. For this example, an initial
configuration file named ``servers_example.yaml`` has the following contents:

.. code-block:: yaml

    servers:
      - host: one.example.com
      - host: two.example.com
        port: 8000
      - host: three.example.com
        port: 8080

Validation of this configuration could be performed like this:

>>> import confuse
>>> import pprint
>>> source = confuse.YamlSource('servers_example.yaml')
>>> config = confuse.RootView([source])
>>> template = {
...     'servers': confuse.Sequence({
...         'host': str,
...         'port': 80,
...     }),
... }
>>> valid_config = config.get(template)
>>> pprint.pprint(valid_config)
{'servers': [{'host': 'one.example.com', 'port': 80},
             {'host': 'two.example.com', 'port': 8000},
             {'host': 'three.example.com', 'port': 8080}]}

The list of items in the initial configuration can be overridden by setting a
higher priority source. Continuing the previous example:

>>> config.set({
...     'servers': [
...         {'host': 'four.example.org'},
...         {'host': 'five.example.org', 'port': 9000},
...     ],
... })
>>> updated_config = config.get(template)
>>> pprint.pprint(updated_config)
{'servers': [{'host': 'four.example.org', 'port': 80},
             {'host': 'five.example.org', 'port': 9000}]}

If the requested view is missing, ``Sequence`` returns an empty list:

>>> config.clear()
>>> config.get(template)
{'servers': []}

However, if an item within the sequence does not match the subtemplate
provided to ``Sequence``, then an error will be raised:

>>> config.set({
...     'servers': [
...         {'host': 'bad_port.example.net', 'port': 'default'}
...     ]
... })
>>> try:
...     config.get(template)
... except confuse.ConfigError as err:
...     print(err)
...
servers#0.port: must be a number

.. note::
    A python list is not the shortcut for defining a ``Sequence`` template but
    will instead produce a ``OneOf`` template. For example,
    ``config.get([str])`` is equivalent to ``config.get(confuse.OneOf([str]))``
    and *not* ``config.get(confuse.Sequence(str))``.


MappingValues
-------------

A ``MappingValues`` template allows validation of a mapping of configuration
items where the keys can be arbitrary but all the values need to match a
subtemplate. Use cases include simple user-defined key:value pairs or larger
configuration blocks that all follow the same structure, but where the keys
naming each block are user-defined. In addition, individual items in the
mapping can be overridden and new items can be added by higher priority
configuration sources. This is in contrast to the ``Sequence`` template, in
which a higher priority source overrides the entire list of configuration items
provided by a lower source.

In the following example, a hypothetical todo list program can be configured
with user-defined colors and category labels. Colors are required to be in hex
format. For each category, a description is required and a priority level is
optional, with a default value of 0. An initial configuration file named
``todo_example.yaml`` has the following contents:

.. code-block:: yaml

    colors:
      red: '#FF0000'
      green: '#00FF00'
      blue: '#0000FF'
    categories:
      default:
        description: Things to do
      high:
        description: These are important
        priority: 50
      low:
        description: Will get to it eventually
        priority: -10

Validation of this configuration could be performed like this:

>>> import confuse
>>> import pprint
>>> source = confuse.YamlSource('todo_example.yaml')
>>> config = confuse.RootView([source])
>>> template = {
...     'colors': confuse.MappingValues(
...         confuse.String(pattern='#[0-9a-fA-F]{6,6}')
...     ),
...     'categories': confuse.MappingValues({
...         'description': str,
...         'priority': 0,
...     }),
... }
>>> valid_config = config.get(template)
>>> pprint.pprint(valid_config)
{'categories': {'default': {'description': 'Things to do', 'priority': 0},
                'high': {'description': 'These are important', 'priority': 50},
                'low': {'description': 'Will get to it eventually',
                        'priority': -10}},
 'colors': {'blue': '#0000FF', 'green': '#00FF00', 'red': '#FF0000'}}

Items in the initial configuration can be overridden and the mapping can be
extended by setting a higher priority source. Continuing the previous example:

>>> config.set({
...     'colors': {
...         'green': '#008000',
...         'orange': '#FFA500',
...     },
...     'categories': {
...         'urgent': {
...             'description': 'Must get done now',
...             'priority': 100,
...         },
...         'high': {
...             'description': 'Important, but not urgent',
...             'priority': 20,
...         },
...     },
... })
>>> updated_config = config.get(template)
>>> pprint.pprint(updated_config)
{'categories': {'default': {'description': 'Things to do', 'priority': 0},
                'high': {'description': 'Important, but not urgent',
                         'priority': 20},
                'low': {'description': 'Will get to it eventually',
                        'priority': -10},
                'urgent': {'description': 'Must get done now',
                           'priority': 100}},
 'colors': {'blue': '#0000FF',
            'green': '#008000',
            'orange': '#FFA500',
            'red': '#FF0000'}}

If the requested view is missing, ``MappingValues`` returns an empty dict:

>>> config.clear()
>>> config.get(template)
{'colors': {}, 'categories': {}}

However, if an item within the mapping does not match the subtemplate
provided to ``MappingValues``, then an error will be raised:

>>> config.set({
...     'categories': {
...         'no_description': {
...              'priority': 10,
...         },
...     },
... })
>>> try:
...     config.get(template)
... except confuse.ConfigError as err:
...     print(err)
...
categories.no_description.description not found


Filename
--------

A ``Filename`` template validates a string as a filename, which is normalized
and returned as an absolute, tilde-free path. By default, relative path values
that are provided in config files are resolved relative to the application's
configuration directory, as returned by ``Configuration.config_dir()``, while
relative paths from command-line options are resolved from the current working
directory. However, these default relative path behaviors can be changed using
the ``cwd``, ``relative_to``, ``in_app_dir``, or ``in_source_dir`` parameters
to the ``Filename`` template. In addition, relative path resolution for an
entire source file can be changed by creating a ``ConfigSource`` with the
``base_for_paths`` parameter set to True. Setting the behavior at the
source-level can be useful when all ``Filename`` templates should be relative
to the source. The template-level parameters provide more fine-grained control.

While the directory used for resolving relative paths can be controlled, the
``Filename`` template should not be used to guarantee that a file is contained
within a given directory, because an absolute path may be provided and will not
be subject to resolution. In addition, ``Filename`` validation only ensures
that the filename is a valid path on the platform where the application is
running, not that the file or any parent directories exist or could be created.

.. note::
    Running the example below will create the application config directory
    ``~/.config/ExampleApp/`` on MacOS and Unix machines or
    ``%APPDATA%\ExampleApp\`` on Windows machines. The filenames in the sample
    output will also be different on your own machine because the paths to
    the config files and the current working directory will be different.

For this example, we will validate a configuration with filenames that should
be resolved as follows:

* ``library``: a filename that should always be resolved relative to the
  application's config directory
* ``media_dir``: a directory that should always be resolved relative to the
  source config file that provides that value
* ``photo_dir`` and ``video_dir``: subdirectories that should be resolved
  relative of the value of ``media_dir``
* ``temp_dir``: a directory that should be resolved relative to ``/tmp/``
* ``log``: a filename that follows the default ``Filename`` template behavior

The initial user config file will be at ``~/.config/ExampleApp/config.yaml``,
where it will be discovered automatically using the :ref:`Search Paths`, and
has the following contents:

.. code-block:: yaml

    library: library.db
    media_dir: media
    photo_dir: my_photos
    video_dir: my_videos
    temp_dir: example_tmp
    log: example.log

Validation of this initial user configuration could be performed as follows:

>>> import confuse
>>> import pprint
>>> config = confuse.Configuration('ExampleApp', __name__)  # Loads user config
>>> print(config.config_dir())  # Application config directory
/home/user/.config/ExampleApp
>>> template = {
...     'library': confuse.Filename(in_app_dir=True),
...     'media_dir': confuse.Filename(in_source_dir=True),
...     'photo_dir': confuse.Filename(relative_to='media_dir'),
...     'video_dir': confuse.Filename(relative_to='media_dir'),
...     'temp_dir': confuse.Filename(cwd='/tmp'),
...     'log': confuse.Filename(),
... }
>>> valid_config = config.get(template)
>>> pprint.pprint(valid_config)
{'library': '/home/user/.config/ExampleApp/library.db',
 'log': '/home/user/.config/ExampleApp/example.log',
 'media_dir': '/home/user/.config/ExampleApp/media',
 'photo_dir': '/home/user/.config/ExampleApp/media/my_photos',
 'temp_dir': '/tmp/example_tmp',
 'video_dir': '/home/user/.config/ExampleApp/media/my_videos'}

Because the user configuration file ``config.yaml`` was in the application's
configuration directory of ``/home/user/.config/ExampleApp/``, all of the
filenames are below ``/home/user/.config/ExampleApp/`` except for ``temp_dir``,
whose template used the ``cwd`` parameter. However, if the following YAML file
is then loaded from ``/var/tmp/example/config.yaml`` as a higher-level source,
some of the paths will no longer be relative to the application config
directory:

.. code-block:: yaml

    library: new_library.db
    media_dir: new_media
    photo_dir: new_photos
    # video_dir: my_videos  # Not overridden
    temp_dir: ./new_example_tmp
    log: new_example.log

Continuing the example code from above:

>>> config.set_file('/var/tmp/example/config.yaml')
>>> updated_config = config.get(template)
>>> pprint.pprint(updated_config)
{'library': '/home/user/.config/ExampleApp/new_library.db',
 'log': '/home/user/.config/ExampleApp/new_example.log',
 'media_dir': '/var/tmp/example/new_media',
 'photo_dir': '/var/tmp/example/new_media/new_photos',
 'temp_dir': '/tmp/new_example_tmp',
 'video_dir': '/var/tmp/example/new_media/my_videos'}

Now, the ``media_dir`` and its subdirectories are relative to the directory
containing the new source file, because the ``media_dir`` template used the
``in_source_dir`` parameter. However, ``log`` remains in the application config
directory because it uses the default ``Filename`` template behavior. The base
directories for the ``library`` and ``temp_dir`` items are also not affected.

If the previous YAML file is instead loaded with the ``base_for_paths``
parameter set to True, then a default ``Filename`` template will use that
config file's directory as the base for resolving relative paths:

>>> config.set_file('/var/tmp/example/config.yaml', base_for_paths=True)
>>> updated_config = config.get(template)
>>> pprint.pprint(updated_config)
{'library': '/home/user/.config/ExampleApp/new_library.db',
 'log': '/var/tmp/example/new_example.log',
 'media_dir': '/var/tmp/example/new_media',
 'photo_dir': '/var/tmp/example/new_media/new_photos',
 'temp_dir': '/tmp/new_example_tmp',
 'video_dir': '/var/tmp/example/new_media/my_videos'}

The filename for ``log`` is now within the directory containing the new source
file. However, the directory for the ``library`` file has not changed since its
template uses the ``in_app_dir`` parameter, which takes precedence over the
source's ``base_for_paths`` setting. The template-level ``cwd`` parameter, used
with ``temp_dir``, also takes precedence over the source setting.

For configuration values set from command-line options, relative paths will be
resolved from the current working directory by default, but the ``cwd``,
``relative_to``, and ``in_app_dir`` template parameters alter that behavior.
Continuing the example code from above, command-line options are mimicked here
by splitting a mock command line string and parsing it with ``argparse``:

>>> import os
>>> print(os.getcwd())  # Current working directory
/home/user
>>> import argparse
>>> parser = argparse.ArgumentParser()
>>> parser.add_argument('--library')
>>> parser.add_argument('--media_dir')
>>> parser.add_argument('--photo_dir')
>>> parser.add_argument('--temp_dir')
>>> parser.add_argument('--log')
>>> cmd_line=('--library cmd_line_library --media_dir cmd_line_media '
...           '--photo_dir cmd_line_photo --temp_dir cmd_line_tmp '
...           '--log cmd_line_log')
>>> args = parser.parse_args(cmd_line.split())
>>> config.set_args(args)
>>> config_with_cmdline = config.get(template)
>>> pprint.pprint(config_with_cmdline)
{'library': '/home/user/.config/ExampleApp/cmd_line_library',
 'log': '/home/user/cmd_line_log',
 'media_dir': '/home/user/cmd_line_media',
 'photo_dir': '/home/user/cmd_line_media/cmd_line_photo',
 'temp_dir': '/tmp/cmd_line_tmp',
 'video_dir': '/home/user/cmd_line_media/my_videos'}

Now the ``log`` and ``media_dir`` paths are relative to the current working
directory of ``/home/user``, while the ``photo_dir`` and ``video_dir`` paths
remain relative to the updated ``media_dir`` path. The ``library`` and
``temp_dir`` paths are still resolved as before, because those templates used
``in_app_dir`` and ``cwd``, respectively.

If a configuration value is provided as an absolute path, the path will be
normalized but otherwise unchanged. Here is an example of overridding earlier
values with absolute paths:

>>> config.set({
...     'library': '~/home_library.db',
...     'media_dir': '/media',
...     'video_dir': '/video_not_under_media',
...     'temp_dir': '/var/./remove_me/..//tmp',
...     'log': '/var/log/example.log',
... })
>>> absolute_config = config.get(template)
>>> pprint.pprint(absolute_config)
{'library': '/home/user/home_library.db',
 'log': '/var/log/example.log',
 'media_dir': '/media',
 'photo_dir': '/media/cmd_line_photo',
 'temp_dir': '/var/tmp',
 'video_dir': '/video_not_under_media'}

The paths for ``library`` and ``temp_dir`` have been normalized, but are not
impacted by their template parameters. Since ``photo_dir`` was not overridden,
the previous relative path value is now being resolved from the new
``media_dir`` absolute path. However, the ``video_dir`` was set to an absolute
path and is no longer a subdirectory of ``media_dir``.


Path
----

A ``Path`` template works the same as a ``Filename`` template, but returns
a ``pathlib.Path`` object instead of a string. Using the same initial example
as above for ``Filename`` but with ``Path`` templates gives the following:

>>> import confuse
>>> import pprint
>>> config = confuse.Configuration('ExampleApp', __name__)
>>> print(config.config_dir())  # Application config directory
/home/user/.config/ExampleApp
>>> template = {
...     'library': confuse.Path(in_app_dir=True),
...     'media_dir': confuse.Path(in_source_dir=True),
...     'photo_dir': confuse.Path(relative_to='media_dir'),
...     'video_dir': confuse.Path(relative_to='media_dir'),
...     'temp_dir': confuse.Path(cwd='/tmp'),
...     'log': confuse.Path(),
... }
>>> valid_config = config.get(template)
>>> pprint.pprint(valid_config)
{'library': PosixPath('/home/user/.config/ExampleApp/library.db'),
 'log': PosixPath('/home/user/.config/ExampleApp/example.log'),
 'media_dir': PosixPath('/home/user/.config/ExampleApp/media'),
 'photo_dir': PosixPath('/home/user/.config/ExampleApp/media/my_photos'),
 'temp_dir': PosixPath('/tmp/example_tmp'),
 'video_dir': PosixPath('/home/user/.config/ExampleApp/media/my_videos')}


Optional
--------

While many templates like ``Integer`` and ``String`` can be configured to
return a default value if the requested view is missing, validation with these
templates will fail if the value is left blank in the YAML file or explicitly
set to ``null`` in YAML (ie, ``None`` in python). The ``Optional`` template
can be used with other templates to allow its subtemplate to accept ``null``
as valid and return a default value. The default behavior of ``Optional``
allows the requested view to be missing, but this behavior can be changed by
passing ``allow_missing=False``, in which case the view must be present but its
value can still be ``null``. In all cases, any value other than ``null`` will
be passed to the subtemplate for validation, and an appropriate ``ConfigError``
will be raised if validation fails. ``Optional`` can also be used with more
complex templates like ``MappingTemplate`` to make entire sections of the
configuration optional.

Consider a configuration where ``log`` can be set to a filename to enable
logging to that file or set to ``null`` or not included in the configuration to
indicate logging to the console. All of the following are valid configurations
using the ``Optional`` template with ``Filename`` as the subtemplate:

>>> import sys
>>> import confuse
>>> def get_log_output(config):
...     output = config['log'].get(confuse.Optional(confuse.Filename()))
...     if output is None:
...         return sys.stderr
...     return output
...
>>> config = confuse.RootView([])
>>> config.set({'log': '/tmp/log.txt'})  # `log` set to a filename
>>> get_log_output(config)
'/tmp/log.txt'
>>> config.set({'log': None})  # `log` set to None (ie, null in YAML)
>>> get_log_output(config)
<_io.TextIOWrapper name='<stderr>' mode='w' encoding='UTF-8'>
>>> config.clear()  # Clear config so that `log` is missing
>>> get_log_output(config)
<_io.TextIOWrapper name='<stderr>' mode='w' encoding='UTF-8'>

However, validation will still fail with ``Optional`` if a value is given that
is invalid for the subtemplate:

>>> config.set({'log': True})
>>> try:
...     get_log_output(config)
... except confuse.ConfigError as err:
...     print(err)
...
log: must be a filename, not bool

And without wrapping the ``Filename`` subtemplate in ``Optional``, ``null``
values are not valid:

>>> config.set({'log': None})
>>> try:
...     config['log'].get(confuse.Filename())
... except confuse.ConfigError as err:
...     print(err)
...
log: must be a filename, not NoneType

If a program wants to require an item to be present in the configuration, while
still allowing ``null`` to be valid, pass ``allow_missing=False`` when
creating the ``Optional`` template:

>>> def get_log_output_no_missing(config):
...     output = config['log'].get(confuse.Optional(confuse.Filename(),
...                                                 allow_missing=False))
...     if output is None:
...         return sys.stderr
...     return output
...
>>> config.set({'log': None})  # `log` set to None is still OK...
>>> get_log_output_no_missing(config)
<_io.TextIOWrapper name='<stderr>' mode='w' encoding='UTF-8'>
>>> config.clear()  # but `log` missing now raises an error
>>> try:
...     get_log_output_no_missing(config)
... except confuse.ConfigError as err:
...     print(err)
...
log not found

The default value returned by ``Optional`` can be set explicitly by passing a
value to its ``default`` parameter. However, if no explicit default is passed
to ``Optional`` and the subtemplate has a default value defined, then
``Optional`` will return the subtemplate's default value. For subtemplates that
do not define default values, like ``MappingTemplate``, ``None`` will be
returned as the default unless an explicit default is provided.

In the following example, ``Optional`` is used to make an ``Integer`` template
more lenient, allowing blank values to validate. In addition, the entire
``extra_config`` block can be left out without causing validation errors. If
we have a file named ``optional.yaml`` with the following contents:

.. code-block:: yaml

    favorite_number: # No favorite number provided, but that's OK
    # This part of the configuration is optional. Uncomment to include.
    # extra_config:
    #   fruit: apple
    #   number: 10

Then the configuration can be validated as follows:

>>> import confuse
>>> source = confuse.YamlSource('optional.yaml')
>>> config = confuse.RootView([source])
>>> # The following `Optional` templates are all equivalent
... config['favorite_number'].get(confuse.Optional(5))
5
>>> config['favorite_number'].get(confuse.Optional(confuse.Integer(5)))
5
>>> config['favorite_number'].get(confuse.Optional(int, default=5))
5
>>> # But a default passed to `Optional` takes precedence and can be any type
... config['favorite_number'].get(confuse.Optional(5, default='five'))
'five'
>>> # `Optional` with `MappingTemplate` returns `None` by default
... extra_config = config['extra_config'].get(confuse.Optional(
...     {'fruit': str, 'number': int},
... ))
>>> print(extra_config is None)
True
>>> # But any default value can be provided, like an empty dict...
... config['extra_config'].get(confuse.Optional(
...     {'fruit': str, 'number': int},
...     default={},
... ))
{}
>>> # or a dict with default values
... config['extra_config'].get(confuse.Optional(
...     {'fruit': str, 'number': int},
...     default={'fruit': 'orange', 'number': 3},
... ))
{'fruit': 'orange', 'number': 3}

Without the ``Optional`` template wrapping the ``Integer``, the blank value
in the YAML file will cause an error:

>>> try:
...     config['favorite_number'].get(5)
... except confuse.ConfigError as err:
...     print(err)
...
favorite_number: must be a number

If the ``extra_config`` for this example configuration is supplied, it must
still match the subtemplate. Therefore, this will fail:

>>> config.set({'extra_config': {}})
>>> try:
...     config['extra_config'].get(confuse.Optional(
...         {'fruit': str, 'number': int},
...     ))
... except confuse.ConfigError as err:
...     print(err)
...
extra_config.fruit not found

But this override of the example configuration will validate:

>>> config.set({'extra_config': {'fruit': 'banana', 'number': 1}})
>>> config['extra_config'].get(confuse.Optional(
...     {'fruit': str, 'number': int},
... ))
{'fruit': 'banana', 'number': 1}
