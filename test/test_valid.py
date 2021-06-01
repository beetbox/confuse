from __future__ import division, absolute_import, print_function

try:
    import enum
    SUPPORTS_ENUM = True
except ImportError:
    SUPPORTS_ENUM = False

try:
    from collections.abc import Mapping, Sequence
except ImportError:
    from collections import Mapping, Sequence

import confuse
import os
import unittest
from . import _root


class ValidConfigTest(unittest.TestCase):
    def test_validate_simple_dict(self):
        config = _root({'foo': 5})
        valid = config.get({'foo': confuse.Integer()})
        self.assertEqual(valid['foo'], 5)

    def test_default_value(self):
        config = _root({})
        valid = config.get({'foo': confuse.Integer(8)})
        self.assertEqual(valid['foo'], 8)

    def test_undeclared_key_raises_keyerror(self):
        config = _root({'foo': 5})
        valid = config.get({'foo': confuse.Integer()})
        with self.assertRaises(KeyError):
            valid['bar']

    def test_undeclared_key_ignored_from_input(self):
        config = _root({'foo': 5, 'bar': 6})
        valid = config.get({'foo': confuse.Integer()})
        with self.assertRaises(KeyError):
            valid['bar']

    def test_int_template_shortcut(self):
        config = _root({'foo': 5})
        valid = config.get({'foo': int})
        self.assertEqual(valid['foo'], 5)

    def test_int_default_shortcut(self):
        config = _root({})
        valid = config.get({'foo': 9})
        self.assertEqual(valid['foo'], 9)

    def test_attribute_access(self):
        config = _root({'foo': 5})
        valid = config.get({'foo': confuse.Integer()})
        self.assertEqual(valid.foo, 5)

    def test_missing_required_value_raises_error_on_validate(self):
        config = _root({})
        with self.assertRaises(confuse.NotFoundError):
            config.get({'foo': confuse.Integer()})

    def test_none_as_default(self):
        config = _root({})
        valid = config.get({'foo': confuse.Integer(None)})
        self.assertIsNone(valid['foo'])

    def test_wrong_type_raises_error_on_validate(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confuse.ConfigTypeError):
            config.get({'foo': confuse.Integer()})

    def test_validate_individual_value(self):
        config = _root({'foo': 5})
        valid = config['foo'].get(confuse.Integer())
        self.assertEqual(valid, 5)

    def test_nested_dict_template(self):
        config = _root({
            'foo': {'bar': 9},
        })
        valid = config.get({
            'foo': {'bar': confuse.Integer()},
        })
        self.assertEqual(valid['foo']['bar'], 9)

    def test_nested_attribute_access(self):
        config = _root({
            'foo': {'bar': 8},
        })
        valid = config.get({
            'foo': {'bar': confuse.Integer()},
        })
        self.assertEqual(valid.foo.bar, 8)


class AsTemplateTest(unittest.TestCase):
    def test_plain_int_as_template(self):
        typ = confuse.as_template(int)
        self.assertIsInstance(typ, confuse.Integer)
        self.assertEqual(typ.default, confuse.REQUIRED)

    def test_concrete_int_as_template(self):
        typ = confuse.as_template(2)
        self.assertIsInstance(typ, confuse.Integer)
        self.assertEqual(typ.default, 2)

    def test_plain_string_as_template(self):
        typ = confuse.as_template(str)
        self.assertIsInstance(typ, confuse.String)
        self.assertEqual(typ.default, confuse.REQUIRED)

    def test_concrete_string_as_template(self):
        typ = confuse.as_template('foo')
        self.assertIsInstance(typ, confuse.String)
        self.assertEqual(typ.default, 'foo')

    @unittest.skipIf(confuse.PY3, "unicode only present in Python 2")
    def test_unicode_type_as_template(self):
        typ = confuse.as_template(unicode)  # noqa ignore=F821
        self.assertIsInstance(typ, confuse.String)
        self.assertEqual(typ.default, confuse.REQUIRED)

    @unittest.skipIf(confuse.PY3, "basestring only present in Python 2")
    def test_basestring_as_template(self):
        typ = confuse.as_template(basestring)  # noqa ignore=F821
        self.assertIsInstance(typ, confuse.String)
        self.assertEqual(typ.default, confuse.REQUIRED)

    def test_dict_as_template(self):
        typ = confuse.as_template({'key': 9})
        self.assertIsInstance(typ, confuse.MappingTemplate)
        self.assertIsInstance(typ.subtemplates['key'], confuse.Integer)
        self.assertEqual(typ.subtemplates['key'].default, 9)

    def test_nested_dict_as_template(self):
        typ = confuse.as_template({'outer': {'inner': 2}})
        self.assertIsInstance(typ, confuse.MappingTemplate)
        self.assertIsInstance(typ.subtemplates['outer'],
                              confuse.MappingTemplate)
        self.assertIsInstance(typ.subtemplates['outer'].subtemplates['inner'],
                              confuse.Integer)
        self.assertEqual(typ.subtemplates['outer'].subtemplates['inner']
                         .default, 2)

    def test_list_as_template(self):
        typ = confuse.as_template(list())
        self.assertIsInstance(typ, confuse.OneOf)
        self.assertEqual(typ.default, confuse.REQUIRED)

    def test_set_as_template(self):
        typ = confuse.as_template(set())
        self.assertIsInstance(typ, confuse.Choice)

    @unittest.skipUnless(SUPPORTS_ENUM,
                         "enum not supported in this version of Python.")
    def test_enum_type_as_template(self):
        typ = confuse.as_template(enum.Enum)
        self.assertIsInstance(typ, confuse.Choice)

    def test_float_type_as_tempalte(self):
        typ = confuse.as_template(float)
        self.assertIsInstance(typ, confuse.Number)
        self.assertEqual(typ.default, confuse.REQUIRED)

    def test_concrete_float_as_template(self):
        typ = confuse.as_template(2.)
        self.assertIsInstance(typ, confuse.Number)
        self.assertEqual(typ.default, 2.)

    def test_none_as_template(self):
        typ = confuse.as_template(None)
        self.assertIs(type(typ), confuse.Template)
        self.assertEqual(typ.default, None)

    def test_required_as_template(self):
        typ = confuse.as_template(confuse.REQUIRED)
        self.assertIs(type(typ), confuse.Template)
        self.assertEqual(typ.default, confuse.REQUIRED)

    def test_dict_type_as_template(self):
        typ = confuse.as_template(dict)
        self.assertIsInstance(typ, confuse.TypeTemplate)
        self.assertEqual(typ.typ, Mapping)
        self.assertEqual(typ.default, confuse.REQUIRED)

    def test_list_type_as_template(self):
        typ = confuse.as_template(list)
        self.assertIsInstance(typ, confuse.TypeTemplate)
        self.assertEqual(typ.typ, Sequence)
        self.assertEqual(typ.default, confuse.REQUIRED)

    def test_set_type_as_template(self):
        typ = confuse.as_template(set)
        self.assertIsInstance(typ, confuse.TypeTemplate)
        self.assertEqual(typ.typ, set)
        self.assertEqual(typ.default, confuse.REQUIRED)

    def test_other_type_as_template(self):
        class MyClass(object):
            pass
        typ = confuse.as_template(MyClass)
        self.assertIsInstance(typ, confuse.TypeTemplate)
        self.assertEqual(typ.typ, MyClass)
        self.assertEqual(typ.default, confuse.REQUIRED)


class StringTemplateTest(unittest.TestCase):
    def test_validate_string(self):
        config = _root({'foo': 'bar'})
        valid = config.get({'foo': confuse.String()})
        self.assertEqual(valid['foo'], 'bar')

    def test_string_default_value(self):
        config = _root({})
        valid = config.get({'foo': confuse.String('baz')})
        self.assertEqual(valid['foo'], 'baz')

    def test_pattern_matching(self):
        config = _root({'foo': 'bar', 'baz': 'zab'})
        valid = config.get({'foo': confuse.String(pattern='^ba.$')})
        self.assertEqual(valid['foo'], 'bar')
        with self.assertRaises(confuse.ConfigValueError):
            config.get({'baz': confuse.String(pattern='!')})

    def test_string_template_shortcut(self):
        config = _root({'foo': 'bar'})
        valid = config.get({'foo': str})
        self.assertEqual(valid['foo'], 'bar')

    def test_string_default_shortcut(self):
        config = _root({})
        valid = config.get({'foo': 'bar'})
        self.assertEqual(valid['foo'], 'bar')

    def test_check_string_type(self):
        config = _root({'foo': 5})
        with self.assertRaises(confuse.ConfigTypeError):
            config.get({'foo': confuse.String()})


class NumberTest(unittest.TestCase):
    def test_validate_int_as_number(self):
        config = _root({'foo': 2})
        valid = config['foo'].get(confuse.Number())
        self.assertIsInstance(valid, int)
        self.assertEqual(valid, 2)

    def test_validate_float_as_number(self):
        config = _root({'foo': 3.0})
        valid = config['foo'].get(confuse.Number())
        self.assertIsInstance(valid, float)
        self.assertEqual(valid, 3.0)

    def test_validate_string_as_number(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].get(confuse.Number())


class ChoiceTest(unittest.TestCase):
    def test_validate_good_choice_in_list(self):
        config = _root({'foo': 2})
        valid = config['foo'].get(confuse.Choice([1, 2, 4, 8, 16]))
        self.assertEqual(valid, 2)

    def test_validate_bad_choice_in_list(self):
        config = _root({'foo': 3})
        with self.assertRaises(confuse.ConfigValueError):
            config['foo'].get(confuse.Choice([1, 2, 4, 8, 16]))

    def test_validate_good_choice_in_dict(self):
        config = _root({'foo': 2})
        valid = config['foo'].get(confuse.Choice({2: 'two', 4: 'four'}))
        self.assertEqual(valid, 'two')

    def test_validate_bad_choice_in_dict(self):
        config = _root({'foo': 3})
        with self.assertRaises(confuse.ConfigValueError):
            config['foo'].get(confuse.Choice({2: 'two', 4: 'four'}))


class OneOfTest(unittest.TestCase):
    def test_default_value(self):
        config = _root({})
        valid = config['foo'].get(confuse.OneOf([], default='bar'))
        self.assertEqual(valid, 'bar')

    def test_validate_good_choice_in_list(self):
        config = _root({'foo': 2})
        valid = config['foo'].get(confuse.OneOf([
            confuse.String(),
            confuse.Integer(),
        ]))
        self.assertEqual(valid, 2)

    def test_validate_first_good_choice_in_list(self):
        config = _root({'foo': 3.14})
        valid = config['foo'].get(confuse.OneOf([
            confuse.Integer(),
            confuse.Number(),
        ]))
        self.assertEqual(valid, 3)

    def test_validate_no_choice_in_list(self):
        config = _root({'foo': None})
        with self.assertRaises(confuse.ConfigValueError):
            config['foo'].get(confuse.OneOf([
                confuse.String(),
                confuse.Integer(),
            ]))

    def test_validate_bad_template(self):
        class BadTemplate(object):
            pass
        config = _root({})
        with self.assertRaises(confuse.ConfigTemplateError):
            config.get(confuse.OneOf([BadTemplate()]))
        del BadTemplate


class StrSeqTest(unittest.TestCase):
    def test_string_list(self):
        config = _root({'foo': ['bar', 'baz']})
        valid = config['foo'].get(confuse.StrSeq())
        self.assertEqual(valid, ['bar', 'baz'])

    def test_string_tuple(self):
        config = _root({'foo': ('bar', 'baz')})
        valid = config['foo'].get(confuse.StrSeq())
        self.assertEqual(valid, ['bar', 'baz'])

    def test_whitespace_separated_string(self):
        config = _root({'foo': 'bar   baz'})
        valid = config['foo'].get(confuse.StrSeq())
        self.assertEqual(valid, ['bar', 'baz'])

    def test_invalid_type(self):
        config = _root({'foo': 9})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].get(confuse.StrSeq())

    def test_invalid_sequence_type(self):
        config = _root({'foo': ['bar', 2126]})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].get(confuse.StrSeq())


class FilenameTest(unittest.TestCase):
    def test_default_value(self):
        config = _root({})
        valid = config['foo'].get(confuse.Filename('foo/bar'))
        self.assertEqual(valid, 'foo/bar')

    def test_default_none(self):
        config = _root({})
        valid = config['foo'].get(confuse.Filename(None))
        self.assertEqual(valid, None)

    def test_missing_required_value(self):
        config = _root({})
        with self.assertRaises(confuse.NotFoundError):
            config['foo'].get(confuse.Filename())

    def test_filename_relative_to_working_dir(self):
        config = _root({'foo': 'bar'})
        valid = config['foo'].get(confuse.Filename(cwd='/dev/null'))
        self.assertEqual(valid, os.path.realpath('/dev/null/bar'))

    def test_filename_relative_to_sibling(self):
        config = _root({'foo': '/', 'bar': 'baz'})
        valid = config.get({
            'foo': confuse.Filename(),
            'bar': confuse.Filename(relative_to='foo')
        })
        self.assertEqual(valid.foo, os.path.realpath('/'))
        self.assertEqual(valid.bar, os.path.realpath('/baz'))

    def test_filename_working_dir_overrides_sibling(self):
        config = _root({'foo': 'bar'})
        valid = config.get({
            'foo': confuse.Filename(cwd='/dev/null', relative_to='baz')
        })
        self.assertEqual(valid.foo, os.path.realpath('/dev/null/bar'))

    def test_filename_relative_to_sibling_with_recursion(self):
        config = _root({'foo': '/', 'bar': 'r', 'baz': 'z'})
        with self.assertRaises(confuse.ConfigTemplateError):
            config.get({
                'foo': confuse.Filename(relative_to='bar'),
                'bar': confuse.Filename(relative_to='baz'),
                'baz': confuse.Filename(relative_to='foo')
            })

    def test_filename_relative_to_self(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confuse.ConfigTemplateError):
            config.get({
                'foo': confuse.Filename(relative_to='foo')
            })

    def test_filename_relative_to_sibling_needs_siblings(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confuse.ConfigTemplateError):
            config['foo'].get(confuse.Filename(relative_to='bar'))

    def test_filename_relative_to_sibling_needs_template(self):
        config = _root({'foo': '/', 'bar': 'baz'})
        with self.assertRaises(confuse.ConfigTemplateError):
            config.get({
                'bar': confuse.Filename(relative_to='foo')
            })

    def test_filename_with_non_file_source(self):
        config = _root({'foo': 'foo/bar'})
        valid = config['foo'].get(confuse.Filename())
        self.assertEqual(valid, os.path.join(os.getcwd(), 'foo', 'bar'))

    def test_filename_with_file_source(self):
        source = confuse.ConfigSource({'foo': 'foo/bar'},
                                      filename='/baz/config.yaml')
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        valid = config['foo'].get(confuse.Filename())
        self.assertEqual(valid, os.path.realpath('/config/path/foo/bar'))

    def test_filename_with_default_source(self):
        source = confuse.ConfigSource({'foo': 'foo/bar'},
                                      filename='/baz/config.yaml',
                                      default=True)
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        valid = config['foo'].get(confuse.Filename())
        self.assertEqual(valid, os.path.realpath('/config/path/foo/bar'))

    def test_filename_use_config_source_dir(self):
        source = confuse.ConfigSource({'foo': 'foo/bar'},
                                      filename='/baz/config.yaml',
                                      base_for_paths=True)
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        valid = config['foo'].get(confuse.Filename())
        self.assertEqual(valid, os.path.realpath('/baz/foo/bar'))

    def test_filename_in_source_dir(self):
        source = confuse.ConfigSource({'foo': 'foo/bar'},
                                      filename='/baz/config.yaml')
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        valid = config['foo'].get(confuse.Filename(in_source_dir=True))
        self.assertEqual(valid, os.path.realpath('/baz/foo/bar'))

    def test_filename_in_source_dir_overrides_in_app_dir(self):
        source = confuse.ConfigSource({'foo': 'foo/bar'},
                                      filename='/baz/config.yaml')
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        valid = config['foo'].get(confuse.Filename(in_source_dir=True,
                                                   in_app_dir=True))
        self.assertEqual(valid, os.path.realpath('/baz/foo/bar'))

    def test_filename_in_app_dir_non_file_source(self):
        source = confuse.ConfigSource({'foo': 'foo/bar'})
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        valid = config['foo'].get(confuse.Filename(in_app_dir=True))
        self.assertEqual(valid, os.path.realpath('/config/path/foo/bar'))

    def test_filename_in_app_dir_overrides_config_source_dir(self):
        source = confuse.ConfigSource({'foo': 'foo/bar'},
                                      filename='/baz/config.yaml',
                                      base_for_paths=True)
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        valid = config['foo'].get(confuse.Filename(in_app_dir=True))
        self.assertEqual(valid, os.path.realpath('/config/path/foo/bar'))

    def test_filename_wrong_type(self):
        config = _root({'foo': 8})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].get(confuse.Filename())


class PathTest(unittest.TestCase):
    def test_path_value(self):
        import pathlib
        config = _root({'foo': 'foo/bar'})
        valid = config['foo'].get(confuse.Path())
        self.assertEqual(valid, pathlib.Path(os.path.abspath('foo/bar')))

    def test_default_value(self):
        import pathlib
        config = _root({})
        valid = config['foo'].get(confuse.Path('foo/bar'))
        self.assertEqual(valid, pathlib.Path('foo/bar'))

    def test_default_none(self):
        config = _root({})
        valid = config['foo'].get(confuse.Path(None))
        self.assertEqual(valid, None)

    def test_missing_required_value(self):
        config = _root({})
        with self.assertRaises(confuse.NotFoundError):
            config['foo'].get(confuse.Path())


class BaseTemplateTest(unittest.TestCase):
    def test_base_template_accepts_any_value(self):
        config = _root({'foo': 4.2})
        valid = config['foo'].get(confuse.Template())
        self.assertEqual(valid, 4.2)

    def test_base_template_required(self):
        config = _root({})
        with self.assertRaises(confuse.NotFoundError):
            config['foo'].get(confuse.Template())

    def test_base_template_with_default(self):
        config = _root({})
        valid = config['foo'].get(confuse.Template('bar'))
        self.assertEqual(valid, 'bar')


class TypeTemplateTest(unittest.TestCase):
    def test_correct_type(self):
        config = _root({'foo': set()})
        valid = config['foo'].get(confuse.TypeTemplate(set))
        self.assertEqual(valid, set())

    def test_incorrect_type(self):
        config = _root({'foo': dict()})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].get(confuse.TypeTemplate(set))

    def test_missing_required_value(self):
        config = _root({})
        with self.assertRaises(confuse.NotFoundError):
            config['foo'].get(confuse.TypeTemplate(set))

    def test_default_value(self):
        config = _root({})
        valid = config['foo'].get(confuse.TypeTemplate(set, set([1, 2])))
        self.assertEqual(valid, set([1, 2]))


class SequenceTest(unittest.TestCase):
    def test_int_list(self):
        config = _root({'foo': [1, 2, 3]})
        valid = config['foo'].get(confuse.Sequence(int))
        self.assertEqual(valid, [1, 2, 3])

    def test_dict_list(self):
        config = _root({'foo': [{'bar': 1, 'baz': 2}, {'bar': 3, 'baz': 4}]})
        valid = config['foo'].get(confuse.Sequence(
            {'bar': int, 'baz': int}
        ))
        self.assertEqual(valid, [
            {'bar': 1, 'baz': 2}, {'bar': 3, 'baz': 4}
        ])

    def test_invalid_item(self):
        config = _root({'foo': [{'bar': 1, 'baz': 2}, {'bar': 3, 'bak': 4}]})
        with self.assertRaises(confuse.NotFoundError):
            config['foo'].get(confuse.Sequence(
                {'bar': int, 'baz': int}
            ))

    def test_wrong_type(self):
        config = _root({'foo': {'one': 1, 'two': 2, 'three': 3}})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].get(confuse.Sequence(int))

    def test_missing(self):
        config = _root({'foo': [1, 2, 3]})
        valid = config['bar'].get(confuse.Sequence(int))
        self.assertEqual(valid, [])


class MappingValuesTest(unittest.TestCase):
    def test_int_dict(self):
        config = _root({'foo': {'one': 1, 'two': 2, 'three': 3}})
        valid = config['foo'].get(confuse.MappingValues(int))
        self.assertEqual(valid, {'one': 1, 'two': 2, 'three': 3})

    def test_dict_dict(self):
        config = _root({'foo': {'first': {'bar': 1, 'baz': 2},
                                'second': {'bar': 3, 'baz': 4}}})
        valid = config['foo'].get(confuse.MappingValues(
            {'bar': int, 'baz': int}
        ))
        self.assertEqual(valid, {
            'first': {'bar': 1, 'baz': 2},
            'second': {'bar': 3, 'baz': 4},
        })

    def test_invalid_item(self):
        config = _root({'foo': {'first': {'bar': 1, 'baz': 2},
                                'second': {'bar': 3, 'bak': 4}}})
        with self.assertRaises(confuse.NotFoundError):
            config['foo'].get(confuse.MappingValues(
                {'bar': int, 'baz': int}
            ))

    def test_wrong_type(self):
        config = _root({'foo': [1, 2, 3]})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].get(confuse.MappingValues(int))

    def test_missing(self):
        config = _root({'foo': {'one': 1, 'two': 2, 'three': 3}})
        valid = config['bar'].get(confuse.MappingValues(int))
        self.assertEqual(valid, {})


class OptionalTest(unittest.TestCase):
    def test_optional_string_valid_type(self):
        config = _root({'foo': 'bar'})
        valid = config['foo'].get(confuse.Optional(confuse.String()))
        self.assertEqual(valid, 'bar')

    def test_optional_string_invalid_type(self):
        config = _root({'foo': 5})
        with self.assertRaises(confuse.ConfigTypeError):
            config['foo'].get(confuse.Optional(confuse.String()))

    def test_optional_string_null(self):
        config = _root({'foo': None})
        valid = config['foo'].get(confuse.Optional(confuse.String()))
        self.assertIsNone(valid)

    def test_optional_string_null_default_value(self):
        config = _root({'foo': None})
        valid = config['foo'].get(confuse.Optional(confuse.String(), 'baz'))
        self.assertEqual(valid, 'baz')

    def test_optional_string_null_string_provides_default(self):
        config = _root({'foo': None})
        valid = config['foo'].get(confuse.Optional(confuse.String('baz')))
        self.assertEqual(valid, 'baz')

    def test_optional_string_null_string_default_override(self):
        config = _root({'foo': None})
        valid = config['foo'].get(confuse.Optional(confuse.String('baz'),
                                                   default='bar'))
        self.assertEqual(valid, 'bar')

    def test_optional_string_allow_missing_no_explicit_default(self):
        config = _root({})
        valid = config['foo'].get(confuse.Optional(confuse.String()))
        self.assertIsNone(valid)

    def test_optional_string_allow_missing_default_value(self):
        config = _root({})
        valid = config['foo'].get(confuse.Optional(confuse.String(), 'baz'))
        self.assertEqual(valid, 'baz')

    def test_optional_string_missing_not_allowed(self):
        config = _root({})
        with self.assertRaises(confuse.NotFoundError):
            config['foo'].get(
                confuse.Optional(confuse.String(), allow_missing=False)
            )

    def test_optional_string_null_missing_not_allowed(self):
        config = _root({'foo': None})
        valid = config['foo'].get(
            confuse.Optional(confuse.String(), allow_missing=False)
        )
        self.assertIsNone(valid)

    def test_optional_mapping_template_valid(self):
        config = _root({'foo': {'bar': 5, 'baz': 'bak'}})
        template = {'bar': confuse.Integer(), 'baz': confuse.String()}
        valid = config.get({'foo': confuse.Optional(template)})
        self.assertEqual(valid['foo']['bar'], 5)
        self.assertEqual(valid['foo']['baz'], 'bak')

    def test_optional_mapping_template_invalid(self):
        config = _root({'foo': {'bar': 5, 'baz': 10}})
        template = {'bar': confuse.Integer(), 'baz': confuse.String()}
        with self.assertRaises(confuse.ConfigTypeError):
            config.get({'foo': confuse.Optional(template)})

    def test_optional_mapping_template_null(self):
        config = _root({'foo': None})
        template = {'bar': confuse.Integer(), 'baz': confuse.String()}
        valid = config.get({'foo': confuse.Optional(template)})
        self.assertIsNone(valid['foo'])

    def test_optional_mapping_template_null_default_value(self):
        config = _root({'foo': None})
        template = {'bar': confuse.Integer(), 'baz': confuse.String()}
        valid = config.get({'foo': confuse.Optional(template, {})})
        self.assertIsInstance(valid['foo'], dict)

    def test_optional_mapping_template_allow_missing_no_explicit_default(self):
        config = _root({})
        template = {'bar': confuse.Integer(), 'baz': confuse.String()}
        valid = config.get({'foo': confuse.Optional(template)})
        self.assertIsNone(valid['foo'])

    def test_optional_mapping_template_allow_missing_default_value(self):
        config = _root({})
        template = {'bar': confuse.Integer(), 'baz': confuse.String()}
        valid = config.get({'foo': confuse.Optional(template, {})})
        self.assertIsInstance(valid['foo'], dict)

    def test_optional_mapping_template_missing_not_allowed(self):
        config = _root({})
        template = {'bar': confuse.Integer(), 'baz': confuse.String()}
        with self.assertRaises(confuse.NotFoundError):
            config.get({'foo': confuse.Optional(template,
                                                allow_missing=False)})

    def test_optional_mapping_template_null_missing_not_allowed(self):
        config = _root({'foo': None})
        template = {'bar': confuse.Integer(), 'baz': confuse.String()}
        valid = config.get({'foo': confuse.Optional(template,
                                                    allow_missing=False)})
        self.assertIsNone(valid['foo'])
