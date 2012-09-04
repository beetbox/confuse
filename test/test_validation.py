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
        value = config['foo'].as_filename()
        self.assertEqual(value, os.path.join(os.getcwd(), 'foo/bar'))

    def test_as_choice_correct(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].as_choice(['foo', 'bar', 'baz'])
        self.assertEqual(value, 'bar')

    def test_as_choice_error(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigValueError):
            config['foo'].as_choice(['foo', 'baz'])

    def test_as_number_float(self):
        config = _root({'f': 1.0})
        config['f'].as_number()

    def test_as_number_int(self):
        config = _root({'i': 2})
        config['i'].as_number()

    def test_as_number_long_in_py2(self):
        # A no-op on Python 3, which doesn't have a long type.
        if not confit.PY3:
            config = _root({'l': long(3)})
            config['l'].as_number()

    def test_as_number_string(self):
        config = _root({'s': 'a'})
        with self.assertRaises(confit.ConfigTypeError):
            config['s'].as_number()
