import confuse
import enum
import os
import unittest
from . import _root


class TypeCheckTest(unittest.TestCase):
    def test_str_type_correct(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].get(str)
        self.assertEqual(value, 'bar')

    def test_str_type_incorrect(self):
        config = _root({'foo': 2})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].get(str)

    def test_int_type_correct(self):
        config = _root({'foo': 2})
        value = config['foo'].get(int)
        self.assertEqual(value, 2)

    def test_int_type_incorrect(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].get(int)


class BuiltInValidatorTest(unittest.TestCase):
    def test_as_filename_with_non_file_source(self):
        config = _root({'foo': 'foo/bar'})
        value = config['foo'].as_filename()
        self.assertEqual(value, os.path.join(os.getcwd(), 'foo', 'bar'))

    def test_as_filename_with_file_source(self):
        source = confuse.ConfigSource({'foo': 'foo/bar'},
                                      filename='/baz/config.yaml')
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        value = config['foo'].as_filename()
        self.assertEqual(value, os.path.realpath('/config/path/foo/bar'))

    def test_as_filename_with_default_source(self):
        source = confuse.ConfigSource({'foo': 'foo/bar'},
                                      filename='/baz/config.yaml',
                                      default=True)
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        value = config['foo'].as_filename()
        self.assertEqual(value, os.path.realpath('/config/path/foo/bar'))

    def test_as_filename_wrong_type(self):
        config = _root({'foo': None})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].as_filename()

    def test_as_path(self):
        config = _root({'foo': 'foo/bar'})
        path = os.path.join(os.getcwd(), 'foo', 'bar')
        try:
            import pathlib
        except ImportError:
            with self.assertRaises(ImportError):
                value = config['foo'].as_path()
        else:
            value = config['foo'].as_path()
            path = pathlib.Path(path)
            self.assertEqual(value, path)

    def test_as_choice_correct(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].as_choice(['foo', 'bar', 'baz'])
        self.assertEqual(value, 'bar')

    def test_as_choice_error(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confuse.ConfigValueError):
            config['foo'].as_choice(['foo', 'baz'])

    def test_as_choice_with_dict(self):
        config = _root({'foo': 'bar'})
        res = config['foo'].as_choice({
            'bar': 'baz',
            'x': 'y',
        })
        self.assertEqual(res, 'baz')

    def test_as_choice_with_enum(self):
        class Foobar(enum.Enum):
            Foo = 'bar'

        config = _root({'foo': Foobar.Foo.value})
        res = config['foo'].as_choice(Foobar)
        self.assertEqual(res, Foobar.Foo)

    def test_as_choice_with_enum_error(self):
        class Foobar(enum.Enum):
            Foo = 'bar'

        config = _root({'foo': 'foo'})
        with self.assertRaises(confuse.ConfigValueError):
            config['foo'].as_choice(Foobar)

    def test_as_number_float(self):
        config = _root({'f': 1.0})
        config['f'].as_number()

    def test_as_number_int(self):
        config = _root({'i': 2})
        config['i'].as_number()

    def test_as_number_string(self):
        config = _root({'s': 'a'})
        with self.assertRaises(confuse.ConfigTypeError):
            config['s'].as_number()

    def test_as_str_seq_str(self):
        config = _root({'k': 'a b c'})
        self.assertEqual(
            config['k'].as_str_seq(),
            ['a', 'b', 'c']
        )

    def test_as_str_seq_list(self):
        config = _root({'k': ['a b', 'c']})
        self.assertEqual(
            config['k'].as_str_seq(),
            ['a b', 'c']
        )

    def test_as_str(self):
        config = _root({'s': 'foo'})
        config['s'].as_str()

    def test_as_str_non_string(self):
        config = _root({'f': 1.0})
        with self.assertRaises(confuse.ConfigTypeError):
            config['f'].as_str()

    def test_as_str_expanded(self):
        config = _root({'s': '${CONFUSE_TEST_VAR}/bar'})
        os.environ["CONFUSE_TEST_VAR"] = 'foo'
        self.assertEqual(config['s'].as_str_expanded(), 'foo/bar')

    def test_as_pairs(self):
        config = _root({'k': [{'a': 'A'}, 'b', ['c', 'C']]})
        self.assertEqual(
            [('a', 'A'), ('b', None), ('c', 'C')],
            config['k'].as_pairs()
        )
