from __future__ import division, absolute_import, print_function

import os
import functools
from .util import BASESTRING
from . import yaml_util

__all__ = ['ConfigSource', 'YamlSource']


UNSET = object()  # sentinel


def _load_first(func):
    '''Call self.load() before the function is called - used for lazy source
    loading'''
    def inner(self, *a, **kw):
        self.load()
        return func(self, *a, **kw)

    try:
        return functools.wraps(func)(inner)
    except AttributeError:
        # in v2 they don't ignore missing attributes
        # v3: https://github.com/python/cpython/blob/3.8/Lib/functools.py
        # v2: https://github.com/python/cpython/blob/2.7/Lib/functools.py
        inner.__name__ = func.__name__
        return inner


class ConfigSource(dict):
    '''A dictionary augmented with metadata about the source of the
    configuration.
    '''
    def __getattribute__(self, k):
        x = super(ConfigSource, self).__getattribute__(k)
        if k == 'keys':
            # HACK: in 2.7, it appears that doing dict(source) only checks for
            #       the existance of a keys attribute and doesn't actually cast
            #       to a dict, so we never get the chance to load. My goal
            #       is to remove this entirely ASAP.
            x()
        return x

    def __init__(self, value=UNSET, filename=None, default=False,
                 retry=False):
        # track whether a config source has been set yet
        self.loaded = value is not UNSET
        self.retry = retry
        super(ConfigSource, self).__init__(value if self.loaded else {})
        if (filename is not None
                and not isinstance(filename, BASESTRING)):
            raise TypeError(u'filename must be a string or None')
        self.filename = filename
        self.default = default

    def __repr__(self):
        return '{}({}, filename={}, default={})'.format(
            self.__class__.__name__,
            dict.__repr__(self)
            if self.loaded else '[Unloaded]'
            if self.exists else "[Source doesn't exist]",
            self.filename, self.default)

    @property
    def exists(self):
        """Does this config have access to usable configuration values?"""
        return self.loaded or self.filename and os.path.isfile(self.filename)

    def load(self):
        """Ensure that the source is loaded."""
        if not self.loaded:
            self.config_dir()
            self.loaded = self._load() is not False or not self.retry
        return self

    def _load(self):
        """Load config from source and update self.
        If it doesn't load, return False to keep it marked as unloaded.
        Otherwise it will be assumed to be loaded.
        """

    def config_dir(self, create=True):
        """Create the config dir, if there's a filename associated with the
        source."""
        if self.filename:
            dirname = os.path.dirname(self.filename)
            if create and dirname and not os.path.isdir(dirname):
                os.makedirs(dirname)
            return dirname
        return None

    # overriding dict methods so that the configuration is loaded before any
    # of them are run
    __getitem__ = _load_first(dict.__getitem__)
    __iter__ = _load_first(dict.__iter__)
    # __len__ = _load_first(dict.__len__)
    keys = _load_first(dict.keys)
    values = _load_first(dict.values)

    @classmethod
    def isoftype(cls, value, **kw):
        return False

    @classmethod
    def of(cls, value, **kw):
        """Try to convert value to a `ConfigSource` object. This lets a
        function accept values that are convertable to a source.
        """
        # ignore if already a source
        if isinstance(value, ConfigSource):
            return value

        # if it's a yaml file
        if YamlSource.isoftype(value, **kw):
            return YamlSource(value, **kw)

        # if it's an explicit config dict
        if isinstance(value, dict):
            return ConfigSource(value, **kw)

        # none of the above
        raise TypeError(
            u'ConfigSource.of value unable to cast to ConfigSource.')


class YamlSource(ConfigSource):
    """A config source pulled from yaml files."""
    EXTENSIONS = '.yaml', '.yml'

    def __init__(self, filename=None, value=UNSET, optional=False,
                 loader=yaml_util.Loader, **kw):
        self.optional = optional
        self.loader = loader
        super(YamlSource, self).__init__(value, filename, **kw)

    @classmethod
    def isoftype(cls, value, **kw):
        return (isinstance(value, BASESTRING)
                and os.path.splitext(value)[1] in YamlSource.EXTENSIONS)

    def _load(self):
        '''Load the file if it exists.'''
        if self.optional and not os.path.isfile(self.filename):
            return False
        self.update(yaml_util.load_yaml(self.filename, loader=self.loader))
