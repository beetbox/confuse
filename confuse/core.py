# -*- coding: utf-8 -*-
# This file is part of Confuse.
# Copyright 2016, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Worry-free YAML configuration files.
"""
from __future__ import division, absolute_import, print_function

import os
import yaml
from collections import OrderedDict

from . import util
from . import templates
from . import yaml_util
from .sources import ConfigSource
from .exceptions import ConfigTypeError, NotFoundError, ConfigError

CONFIG_FILENAME = 'config.yaml'
DEFAULT_FILENAME = 'config_default.yaml'
ROOT_NAME = 'root'

REDACTED_TOMBSTONE = 'REDACTED'


# Views and sources.


class ConfigView(object):
    """A configuration "view" is a query into a program's configuration
    data. A view represents a hypothetical location in the configuration
    tree; to extract the data from the location, a client typically
    calls the ``view.get()`` method. The client can access children in
    the tree (subviews) by subscripting the parent view (i.e.,
    ``view[key]``).
    """

    name = None
    """The name of the view, depicting the path taken through the
    configuration in Python-like syntax (e.g., ``foo['bar'][42]``).
    """

    def resolve(self):
        """The core (internal) data retrieval method. Generates (value,
        source) pairs for each source that contains a value for this
        view. May raise `ConfigTypeError` if a type error occurs while
        traversing a source.
        """
        raise NotImplementedError

    def first(self):
        """Return a (value, source) pair for the first object found for
        this view. This amounts to the first element returned by
        `resolve`. If no values are available, a `NotFoundError` is
        raised.
        """
        pairs = self.resolve()
        try:
            return util.iter_first(pairs)
        except ValueError:
            raise NotFoundError(u"{0} not found".format(self.name))

    def exists(self):
        """Determine whether the view has a setting in any source.
        """
        try:
            self.first()
        except NotFoundError:
            return False
        return True

    def add(self, value):
        """Set the *default* value for this configuration view. The
        specified value is added as the lowest-priority configuration
        data source.
        """
        raise NotImplementedError

    def set(self, value):
        """*Override* the value for this configuration view. The
        specified value is added as the highest-priority configuration
        data source.
        """
        raise NotImplementedError

    def root(self):
        """The RootView object from which this view is descended.
        """
        raise NotImplementedError

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)

    def __iter__(self):
        """Iterate over the keys of a dictionary view or the *subviews*
        of a list view.
        """
        # Try getting the keys, if this is a dictionary view.
        try:
            keys = self.keys()
            for key in keys:
                yield key

        except ConfigTypeError:
            # Otherwise, try iterating over a list.
            collection = self.get()
            if not isinstance(collection, (list, tuple)):
                raise ConfigTypeError(
                    u'{0} must be a dictionary or a list, not {1}'.format(
                        self.name, type(collection).__name__
                    )
                )

            # Yield all the indices in the list.
            for index in range(len(collection)):
                yield self[index]

    def __getitem__(self, key):
        """Get a subview of this view."""
        return Subview(self, key)

    def __setitem__(self, key, value):
        """Create an overlay source to assign a given key under this
        view.
        """
        self.set({key: value})

    def __contains__(self, key):
        return self[key].exists()

    @classmethod
    def _build_namespace_dict(cls, obj, dots=False):
        """Recursively replaces all argparse.Namespace and optparse.Values
        with dicts and drops any keys with None values.

        Additionally, if dots is True, will expand any dot delimited
        keys.

        :param obj: Namespace, Values, or dict to iterate over. Other
            values will simply be returned.
        :type obj: argparse.Namespace or optparse.Values or dict or *
        :param dots: If True, any properties on obj that contain dots (.)
            will be broken down into child dictionaries.
        :return: A new dictionary or the value passed if obj was not a
            dict, Namespace, or Values.
        :rtype: dict or *
        """
        # We expect our root object to be a dict, but it may come in as
        # a namespace
        obj = util.namespace_to_dict(obj)
        # We only deal with dictionaries
        if not isinstance(obj, dict):
            return obj

        # Get keys iterator
        keys = obj.keys() if util.PY3 else obj.iterkeys()
        if dots:
            # Dots needs sorted keys to prevent parents from
            # clobbering children
            keys = sorted(list(keys))

        output = {}
        for key in keys:
            value = obj[key]
            if value is None:  # Avoid unset options.
                continue

            save_to = output
            result = cls._build_namespace_dict(value, dots)
            if dots:
                # Split keys by dots as this signifies nesting
                split = key.split('.')
                if len(split) > 1:
                    # The last index will be the key we assign result to
                    key = split.pop()
                    # Build the dict tree if needed and change where
                    # we're saving to
                    for child_key in split:
                        if child_key in save_to and \
                                isinstance(save_to[child_key], dict):
                            save_to = save_to[child_key]
                        else:
                            # Clobber or create
                            save_to[child_key] = {}
                            save_to = save_to[child_key]

            # Save
            if key in save_to:
                save_to[key].update(result)
            else:
                save_to[key] = result
        return output

    def set_args(self, namespace, dots=False):
        """Overlay parsed command-line arguments, generated by a library
        like argparse or optparse, onto this view's value.

        :param namespace: Dictionary or Namespace to overlay this config with.
            Supports nested Dictionaries and Namespaces.
        :type namespace: dict or Namespace
        :param dots: If True, any properties on namespace that contain dots (.)
            will be broken down into child dictionaries.
            :Example:

            {'foo.bar': 'car'}
            # Will be turned into
            {'foo': {'bar': 'car'}}
        :type dots: bool
        """
        self.set(self._build_namespace_dict(namespace, dots))

    # Magical conversions. These special methods make it possible to use
    # View objects somewhat transparently in certain circumstances. For
    # example, rather than using ``view.get(bool)``, it's possible to
    # just say ``bool(view)`` or use ``view`` in a conditional.

    def __str__(self):
        """Get the value for this view as a bytestring.
        """
        if util.PY3:
            return self.__unicode__()
        else:
            return bytes(self.get())

    def __unicode__(self):
        """Get the value for this view as a Unicode string.
        """
        return util.STRING(self.get())

    def __nonzero__(self):
        """Gets the value for this view as a boolean. (Python 2 only.)
        """
        return self.__bool__()

    def __bool__(self):
        """Gets the value for this view as a boolean. (Python 3 only.)
        """
        return bool(self.get())

    # Dictionary emulation methods.

    def keys(self):
        """Returns a list containing all the keys available as subviews
        of the current views. This enumerates all the keys in *all*
        dictionaries matching the current view, in contrast to
        ``view.get(dict).keys()``, which gets all the keys for the
        *first* dict matching the view. If the object for this view in
        any source is not a dict, then a `ConfigTypeError` is raised. The
        keys are ordered according to how they appear in each source.
        """
        keys = []

        for dic, _ in self.resolve():
            try:
                cur_keys = dic.keys()
            except AttributeError:
                raise ConfigTypeError(
                    u'{0} must be a dict, not {1}'.format(
                        self.name, type(dic).__name__
                    )
                )

            for key in cur_keys:
                if key not in keys:
                    keys.append(key)

        return keys

    def items(self):
        """Iterates over (key, subview) pairs contained in dictionaries
        from *all* sources at this view. If the object for this view in
        any source is not a dict, then a `ConfigTypeError` is raised.
        """
        for key in self.keys():
            yield key, self[key]

    def values(self):
        """Iterates over all the subviews contained in dictionaries from
        *all* sources at this view. If the object for this view in any
        source is not a dict, then a `ConfigTypeError` is raised.
        """
        for key in self.keys():
            yield self[key]

    # List/sequence emulation.

    def all_contents(self):
        """Iterates over all subviews from collections at this view from
        *all* sources. If the object for this view in any source is not
        iterable, then a `ConfigTypeError` is raised. This method is
        intended to be used when the view indicates a list; this method
        will concatenate the contents of the list from all sources.
        """
        for collection, _ in self.resolve():
            try:
                it = iter(collection)
            except TypeError:
                raise ConfigTypeError(
                    u'{0} must be an iterable, not {1}'.format(
                        self.name, type(collection).__name__
                    )
                )
            for value in it:
                yield value

    # Validation and conversion.

    def flatten(self, redact=False):
        """Create a hierarchy of OrderedDicts containing the data from
        this view, recursively reifying all views to get their
        represented values.

        If `redact` is set, then sensitive values are replaced with
        the string "REDACTED".
        """
        od = OrderedDict()
        for key, view in self.items():
            if redact and view.redact:
                od[key] = REDACTED_TOMBSTONE
            else:
                try:
                    od[key] = view.flatten(redact=redact)
                except ConfigTypeError:
                    od[key] = view.get()
        return od

    def get(self, template=templates.REQUIRED):
        """Retrieve the value for this view according to the template.

        The `template` against which the values are checked can be
        anything convertible to a `Template` using `as_template`. This
        means you can pass in a default integer or string value, for
        example, or a type to just check that something matches the type
        you expect.

        May raise a `ConfigValueError` (or its subclass,
        `ConfigTypeError`) or a `NotFoundError` when the configuration
        doesn't satisfy the template.
        """
        return templates.as_template(template).value(self, template)

    # Shortcuts for common templates.

    def as_filename(self):
        """Get the value as a path. Equivalent to `get(Filename())`.
        """
        return self.get(templates.Filename())

    def as_path(self):
        """Get the value as a `pathlib.Path` object. Equivalent to `get(Path())`.
        """
        return self.get(templates.Path())

    def as_choice(self, choices):
        """Get the value from a list of choices. Equivalent to
        `get(Choice(choices))`.
        """
        return self.get(templates.Choice(choices))

    def as_number(self):
        """Get the value as any number type: int or float. Equivalent to
        `get(Number())`.
        """
        return self.get(templates.Number())

    def as_str_seq(self, split=True):
        """Get the value as a sequence of strings. Equivalent to
        `get(StrSeq(split=split))`.
        """
        return self.get(templates.StrSeq(split=split))

    def as_pairs(self, default_value=None):
        """Get the value as a sequence of pairs of two strings. Equivalent to
        `get(Pairs(default_value=default_value))`.
        """
        return self.get(templates.Pairs(default_value=default_value))

    def as_str(self):
        """Get the value as a (Unicode) string. Equivalent to
        `get(unicode)` on Python 2 and `get(str)` on Python 3.
        """
        return self.get(templates.String())

    def as_str_expanded(self):
        """Get the value as a (Unicode) string, with env vars
        expanded by `os.path.expandvars()`.
        """
        return self.get(templates.String(expand_vars=True))

    # Redaction.

    @property
    def redact(self):
        """Whether the view contains sensitive information and should be
        redacted from output.
        """
        return () in self.get_redactions()

    @redact.setter
    def redact(self, flag):
        self.set_redaction((), flag)

    def set_redaction(self, path, flag):
        """Add or remove a redaction for a key path, which should be an
        iterable of keys.
        """
        raise NotImplementedError()

    def get_redactions(self):
        """Get the set of currently-redacted sub-key-paths at this view.
        """
        raise NotImplementedError()


class RootView(ConfigView):
    """The base of a view hierarchy. This view keeps track of the
    sources that may be accessed by subviews.
    """
    def __init__(self, sources):
        """Create a configuration hierarchy for a list of sources. At
        least one source must be provided. The first source in the list
        has the highest priority.
        """
        self.sources = list(sources)
        self.name = ROOT_NAME
        self.redactions = set()

    def add(self, obj, skip_missing=False, **kw):
        src = ConfigSource.of(obj, **kw)
        if not skip_missing or src.exists:
            self.sources.append(src)

    def set(self, value, skip_missing=False, **kw):
        src = ConfigSource.of(value, **kw)
        if not skip_missing or src.exists:
            self.sources.insert(0, src)

    def resolve(self):
        return ((dict(s), s) for s in self.sources)

    def clear(self):
        """Remove all sources (and redactions) from this
        configuration.
        """
        del self.sources[:]
        self.redactions.clear()

    def root(self):
        return self

    def set_redaction(self, path, flag):
        if flag:
            self.redactions.add(path)
        elif path in self.redactions:
            self.redactions.remove(path)

    def get_redactions(self):
        return self.redactions


class Subview(ConfigView):
    """A subview accessed via a subscript of a parent view."""
    def __init__(self, parent, key):
        """Make a subview of a parent view for a given subscript key.
        """
        self.parent = parent
        self.key = key

        # Choose a human-readable name for this view.
        if isinstance(self.parent, RootView):
            self.name = ''
        else:
            self.name = self.parent.name
            if not isinstance(self.key, int):
                self.name += '.'
        if isinstance(self.key, int):
            self.name += u'#{0}'.format(self.key)
        elif isinstance(self.key, bytes):
            self.name += self.key.decode('utf-8')
        elif isinstance(self.key, util.STRING):
            self.name += self.key
        else:
            self.name += repr(self.key)

    def resolve(self):
        for collection, source in self.parent.resolve():
            try:
                value = collection[self.key]
            except IndexError:
                # List index out of bounds.
                continue
            except KeyError:
                # Dict key does not exist.
                continue
            except TypeError:
                # Not subscriptable.
                raise ConfigTypeError(
                    u"{0} must be a collection, not {1}".format(
                        self.parent.name, type(collection).__name__
                    )
                )
            yield value, source

    def set(self, value):
        self.parent.set({self.key: value})

    def add(self, value):
        self.parent.add({self.key: value})

    def root(self):
        return self.parent.root()

    def set_redaction(self, path, flag):
        self.parent.set_redaction((self.key,) + path, flag)

    def get_redactions(self):
        return (kp[1:] for kp in self.parent.get_redactions()
                if kp and kp[0] == self.key)

# Main interface.


class Configuration(RootView):
    def __init__(self, appname, modname=None, read=True,
                 loader=yaml_util.Loader):
        """Create a configuration object by reading the
        automatically-discovered config files for the application for a
        given name. If `modname` is specified, it should be the import
        name of a module whose package will be searched for a default
        config file. (Otherwise, no defaults are used.) Pass `False` for
        `read` to disable automatic reading of all discovered
        configuration files. Use this when creating a configuration
        object at module load time and then call the `read` method
        later. Specify the Loader class as `loader`.
        """
        super(Configuration, self).__init__([])
        self.appname = appname
        self.modname = modname
        self.loader = loader

        # Resolve default source location. We do this ahead of time to
        # avoid unexpected problems if the working directory changes.
        if self.modname:
            self._package_path = util.find_package_path(self.modname)
        else:
            self._package_path = None

        self._env_var = '{0}DIR'.format(self.appname.upper())

        if read:
            self.read()

    def user_config_path(self):
        """Points to the location of the user configuration.

        The file may not exist.
        """
        return os.path.join(self.config_dir(), CONFIG_FILENAME)

    def _add_user_source(self):
        """Add the configuration options from the YAML file in the
        user's configuration directory (given by `config_dir`) if it
        exists.
        """
        self.add(
            self.user_config_path(), loader=self.loader, skip_missing=False)

    def _add_default_source(self):
        """Add the package's default configuration settings. This looks
        for a YAML file located inside the package for the module
        `modname` if it was given.
        """
        if self._package_path:
            self.add(
                os.path.join(self._package_path, DEFAULT_FILENAME),
                loader=self.loader, default=True, skip_missing=False)

    def read(self, user=True, defaults=True):
        """Find and read the files for this configuration and set them
        as the sources for this configuration. To disable either
        discovered user configuration files or the in-package defaults,
        set `user` or `defaults` to `False`.
        """
        if user:
            self._add_user_source()
        if defaults:
            self._add_default_source()
        for s in self.sources:
            s.load()

    def config_dir(self):
        """Get the path to the user configuration directory. The
        directory is guaranteed to exist as a postcondition (one may be
        created if none exist).

        If the application's ``...DIR`` environment variable is set, it
        is used as the configuration directory. Otherwise,
        platform-specific standard configuration locations are searched
        for a ``config.yaml`` file. If no configuration file is found, a
        fallback path is used.
        """
        # If environment variable is set, use it.
        if self._env_var in os.environ:
            appdir = os.environ[self._env_var]
            appdir = os.path.abspath(os.path.expanduser(appdir))
            if os.path.isfile(appdir):
                raise ConfigError(u'{0} must be a directory'.format(
                    self._env_var
                ))

        else:
            # Search platform-specific locations. If no config file is
            # found, fall back to the first directory in the list.
            configdirs = util.config_dirs()
            for confdir in configdirs:
                appdir = os.path.join(confdir, self.appname)
                if os.path.isfile(os.path.join(appdir, CONFIG_FILENAME)):
                    break
            else:
                appdir = os.path.join(configdirs[0], self.appname)

        # Ensure that the directory exists.
        if not os.path.isdir(appdir):
            os.makedirs(appdir)
        return appdir

    def set_file(self, filename):
        """Parses the file as YAML and inserts it into the configuration
        sources with highest priority.
        """
        self.set(os.path.abspath(filename), loader=self.loader)

    def dump(self, full=True, redact=False):
        """Dump the Configuration object to a YAML file.

        The order of the keys is determined from the default
        configuration file. All keys not in the default configuration
        will be appended to the end of the file.

        :param full:      Dump settings that don't differ from the defaults
                          as well
        :param redact:    Remove sensitive information (views with the `redact`
                          flag set) from the output
        """
        if full:
            out_dict = self.flatten(redact=redact)
        else:
            # Exclude defaults when flattening.
            sources = [s for s in self.sources if not s.default]
            temp_root = RootView(sources)
            temp_root.redactions = self.redactions
            out_dict = temp_root.flatten(redact=redact)

        yaml_out = yaml.dump(out_dict, Dumper=yaml_util.Dumper,
                             default_flow_style=None, indent=4,
                             width=1000)

        # Restore comments to the YAML text.
        default_source = None
        for source in self.sources:
            if source.default:
                default_source = source
                break
        if default_source and default_source.filename:
            with open(default_source.filename, 'rb') as fp:
                default_data = fp.read()
            yaml_out = yaml_util.restore_yaml_comments(
                yaml_out, default_data.decode('utf-8'))

        return yaml_out


class LazyConfig(Configuration):
    """A Configuration at reads files on demand when it is first
    accessed. This is appropriate for using as a global config object at
    the module level.
    """
    def __init__(self, appname, modname=None):
        super(LazyConfig, self).__init__(appname, modname, read=False)
