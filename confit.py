class ConfigError(Exception):
    pass
class NotFoundError(ConfigError):
    pass
class WrongTypeError(ConfigError):
    pass

class View(object):
    def get_all(self):
        raise NotImplementedError

    def get(self, typ=None):
        values = self.get_all()

        # Get the first value.
        try:
            value = iter(values).next()
        except StopIteration:
            raise NotFoundError()

        # Check the type.
        if typ is not None and not isinstance(value, typ):
                raise WrongTypeError()

        return value

    def __getitem__(self, key):
        return Subview(self, key)

class RootView(View):
    def __init__(self, sources):
        if not sources:
            raise ValueError('no sources supplied')
        self.sources = sources

    def get_all(self):
        return self.sources

class Subview(View):
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
                raise WrongTypeError()

            yield value
