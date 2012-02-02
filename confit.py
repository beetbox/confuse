"""Worry-free YAML configuration files.
"""

class ConfigError(Exception):
    """Base class for exceptions raised when querying a configuration.
    """
    pass
class NotFoundError(ConfigError):
    """A requested value could not be found in the configuration trees.
    """
    pass
class ConfigTypeError(ConfigError, TypeError):
    """The value in the configuration did not match the expected type.
    """
    pass

class ConfigView(object):
    """A configuration "view" is a query into a program's configuration
    data. A view represents a hypothetical location in the configuration
    tree; to extract the data from the location, a client typically
    calls the ``view.get()`` method. The client can access children in
    the tree (subviews) by subscripting the parent view (i.e.,
    ``view[key]``).
    """
    def get_all(self):
        """Generates all available values for the view in the order of
        the configuration's sources. (Each source may have at most one
        value for each view.) If no values are available, no values are
        generated. If a type error is encountered when traversing a
        source to resolve the view, a ConfigTypeError may be raised.
        """
        raise NotImplementedError

    def get(self, typ=None):
        """Returns the canonical value for the view. This amounts to the
        first item in ``view.get_all()``. If the view cannot be
        resolved, this method raises a NotFoundError.
        """
        values = self.get_all()

        # Get the first value.
        try:
            value = iter(values).next()
        except StopIteration:
            raise NotFoundError(u"%s not found" % self.name())

        # Check the type.
        if typ is not None and not isinstance(value, typ):
            raise ConfigTypeError(u"%s must by of type %s, not %s" %
                                  (self.name(), unicode(typ),
                                  unicode(type(value))))

        return value

    def name(self):
        """Returns the name of the view, depicting the path taken
        through the configuration in Python-like syntax (e.g.,
        ``foo['bar'][42]``).
        """
        raise NotImplementedError

    def __repr__(self):
        return '<ConfigView: %s>' % self.name()

    def __getitem__(self, key):
        """Get a subview of this view."""
        return Subview(self, key)

    # Magical conversions. These special methods make it possible to use
    # View objects somewhat transparently in certain circumstances. For
    # example, rather than using ``view.get(bool)``, it's possible to
    # just say ``bool(view)`` or use ``view`` in a conditional.

    def __str__(self):
        """Gets the value for this view as a byte string."""
        return str(self.get())
    
    def __unicode__(self):
        """Gets the value for this view as a unicode string."""
        return unicode(self.get())
    
    def __nonzero__(self):
        """Gets the value for this view as a boolean."""
        return bool(self.get())

    # Collection methods. These allow a view to behave as a Python
    # iterable, containing all the objects that *all* sources contain.
    # Note that this differs from resolving the view and then iterating
    # over the result. That is, ``list(view)`` will result in a
    # different set of values from ``view.get(list)``. Namely, the
    # former gives everything contained in every list from every source,
    # while the latter gets the list in the first source.

    def __iter__(self):
        """Iterates over all of the values accessible through this view
        (from all sources).
        """
        for collection in self.get_all():
            try:
                it = iter(collection)
            except TypeError:
                raise ConfigTypeError(u'%s must be a collection, not %s' %
                                      (self.name(), unicode(type(collection))))
            for value in it:
                yield value

    def __len__(self):
        """Gives the number of the values accessible as children of this
        view.
        """
        length = 0
        for collection in self.get_all():
            try:
                length += len(collection)
            except TypeError:
                raise ConfigTypeError(u'%s (of type %s) has no length' %
                                    (self.name(), unicode(type(collection))))
        return length

    def __contains__(self, item):
        """Determines whether a value is a child of this view.
        """
        for collection in self.get_all():
            try:
                if item in collection:
                    return True
            except TypeError:
                raise ConfigTypeError(u'%s must be a collection, not %s' %
                                      (self.name(), unicode(type(collection))))
        return False

class RootView(ConfigView):
    """The base of a view hierarchy. This view keeps track of the
    sources that may be accessed by subviews.
    """
    def __init__(self, sources):
        """Create a configuration hierarchy for a list of sources. At
        least one source must be provided. The first source in the list
        has the highest priority.
        """
        if not sources:
            raise ValueError('no sources supplied')
        self.sources = sources

    def get_all(self):
        return self.sources

    def name(self):
        return u"root"

class Subview(ConfigView):
    """A subview accessed via a subscript of a parent view."""
    def __init__(self, parent, key):
        """Make a subview of a parent view for a given subscript key.
        """
        self.parent = parent
        self.key = key

    def get_all(self):
        for collection in self.parent.get_all():
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
                raise ConfigTypeError(u"%s must be a collection, not %s" %
                                      (self.parent.name(),
                                       unicode(type(collection))))
            yield value

    def name(self):
        return u"%s[%s]" % (self.parent.name(), repr(self.key))
