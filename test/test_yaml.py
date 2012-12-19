import confit
import yaml
from . import unittest

def load(s):
    return yaml.load(s, Loader=confit.Loader)

class ParseTest(unittest.TestCase):
    def test_dict_parsed_as_ordereddict(self):
        v = load("a: b\nc: d")
        self.assertTrue(isinstance(v, confit.OrderedDict))
        self.assertEqual(list(v), ['a', 'c'])

    def test_string_beginning_with_percent(self):
        v = load("foo: %bar")
        self.assertEqual(v['foo'], '%bar')
