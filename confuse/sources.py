from __future__ import division, absolute_import, print_function

from .util import BASESTRING
from . import yaml_util
import os


class ConfigSource(dict):
    """A dictionary augmented with metadata about the source of the
    configuration.
    """
    def __init__(self, value, filename=None, default=False):
        super(ConfigSource, self).__init__(value)
        if (filename is not None
                and not isinstance(filename, BASESTRING)):
            raise TypeError(u'filename must be a string or None')
        self.filename = filename
        self.default = default

    def __repr__(self):
        return 'ConfigSource({0!r}, {1!r}, {2!r})'.format(
            super(ConfigSource, self),
            self.filename,
            self.default,
        )

    @classmethod
    def of(cls, value):
        """Given either a dictionary or a `ConfigSource` object, return
        a `ConfigSource` object. This lets a function accept either type
        of object as an argument.
        """
        if isinstance(value, ConfigSource):
            return value
        elif isinstance(value, dict):
            return ConfigSource(value)
        else:
            raise TypeError(u'source value must be a dict')


class YamlSource(ConfigSource):
    """A configuration data source that reads from a YAML file.
    """

    def __init__(self, filename=None, default=False,
                 optional=False, loader=yaml_util.Loader):
        """Create a YAML data source by reading data from a file.

        May raise a `ConfigReadError`. However, if `optional` is
        enabled, this exception will not be raised in the case when the
        file does not exist---instead, the source will be silently
        empty.
        """
        filename = os.path.abspath(filename)
        super(YamlSource, self).__init__({}, filename, default)
        self.loader = loader
        self.optional = optional
        self.load()

    def load(self):
        """Load YAML data from the source's filename.
        """
        if self.optional and not os.path.isfile(self.filename):
            value = {}
        else:
            value = yaml_util.load_yaml(self.filename,
                                        loader=self.loader) or {}
        self.update(value)
