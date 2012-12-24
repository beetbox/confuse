import confit

# Use unittest2 on Python < 2.7.
try:
    import unittest2 as unittest
except ImportError:
    import unittest

def _root(*sources):
    return confit.RootView([confit.ConfigSource.of(s) for s in sources])
