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

Here's What Confit Does
-----------------------

* Seamless layering and overriding between multiple config files.
* Sensible errors are raised when config files are missing values or have
  incorrect types. No need to write ad-hoc validation code.
* Configuration defaults can be specified via an in-package
  `config_default.yaml` file.
* Platform-specific configuration paths (`$XDG_CONFIG_HOME` or `~/.config`
  on Unix; "Application Support" on Mac OS X; `%APPDATA%` on Windows).

What Confit Will Do
-------------------

* Declarative integration with command-line options ([optparse][] or
  [argparse][]).
* Read and write arbitrary files in your application's configuration directory.
* Easy modification of config files.

[optparse]: http://docs.python.org/dev/library/optparse.html
[argparse]: http://docs.python.org/dev/library/argparse.html
