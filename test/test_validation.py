import unittest
import confit
import os
from . import _root

class TypeCheckTest(unittest.TestCase):
    def test_str_type_correct(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].get(str)
        self.assertEqual(value, 'bar')

    def test_str_type_incorrect(self):
        config = _root({'foo': 2})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(str)

    def test_int_type_correct(self):
        config = _root({'foo': 2})
        value = config['foo'].get(int)
        self.assertEqual(value, 2)

    def test_int_type_incorrect(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(int)

class BuiltInValidatorTest(unittest.TestCase):
    def test_as_filename(self):
        config = _root({'foo': 'foo/bar'})
        value = config['foo'].get(confit.as_filename)
        self.assertEqual(value, os.path.join(os.getcwd(), 'foo/bar'))

    def test_as_choice_correct(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].get(confit.as_choice(['foo', 'bar', 'baz']))
        self.assertEqual(value, 'bar')

    def test_as_choice_error(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigValueError):
            config['foo'].get(confit.as_choice(['foo', 'baz']))
