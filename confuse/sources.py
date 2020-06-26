from __future__ import division, absolute_import, print_function

from .util import BASESTRING

__all__ = ['ConfigSource']


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
