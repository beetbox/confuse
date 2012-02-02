class ConfigError(Exception):
    pass
class NotFoundError(ConfigError):
    pass
class ConfigTypeError(ConfigError, TypeError):
    pass

class ConfigView(object):
    def get_all(self):
        raise NotImplementedError

    def name(self):
        raise NotImplementedError

    def get(self, typ=None):
        values = self.get_all()

        # Get the first value.
        try:
            value = iter(values).next()
        except StopIteration:
            raise NotFoundError(u"%s not found" % self.name())

        # Check the type.
        if typ is not None and not isinstance(value, typ):
            raise ConfigTypeError(u"%s must by of type %s" %
                                 (self.name(), unicode(typ)))

        return value

    def __repr__(self):
        return '<ConfigView: %s>' % self.name()

    # Magical conversions.

    def __getitem__(self, key):
        return Subview(self, key)

    def __str__(self):
        return str(self.get())
    
    def __unicode__(self):
        return unicode(self.get())
    
    def __nonzero__(self):
        return bool(self.get())

    def __iter__(self):
        for container in self.get_all():
            try:
                it = iter(container)
            except TypeError:
                raise ConfigTypeError(u'%s must be a container' %
                                     self.name())
            for value in it:
                yield value

    def __len__(self):
        length = 0
        for container in self.get_all():
            try:
                length += len(container)
            except TypeError:
                raise ConfigTypeError(u'%s (of type %s) has no length' %
                                    (self.name(), unicode(type(container))))
        return length

    def __contains__(self, item):
        for container in self.get_all():
            try:
                if item in container:
                    return True
            except TypeError:
                raise ConfigTypeError(u'%s must be a container' %
                                     self.name())
        return False

class RootView(ConfigView):
    def __init__(self, sources):
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
                raise ConfigTypeError(u"%s must be a collection" %
                                     self.parent.name())

            yield value

    def name(self):
        return u"%s[%s]" % (self.parent.name(), repr(self.key))
