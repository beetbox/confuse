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
