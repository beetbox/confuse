Template Examples
=================

These examples demonstrate how the confuse templates work to validate
configuration values.


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
