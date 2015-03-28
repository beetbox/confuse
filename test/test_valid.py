import confit
import os
import collections
from . import _root, unittest


class ValidConfigTest(unittest.TestCase):
    def test_validate_simple_dict(self):
        config = _root({'foo': 5})
        valid = config.get({'foo': confit.Integer()})
        self.assertEqual(valid['foo'], 5)

    def test_default_value(self):
        config = _root({})
        valid = config.get({'foo': confit.Integer(8)})
        self.assertEqual(valid['foo'], 8)

    def test_undeclared_key_raises_keyerror(self):
        config = _root({'foo': 5})
        valid = config.get({'foo': confit.Integer()})
        with self.assertRaises(KeyError):
            valid['bar']

    def test_undeclared_key_ignored_from_input(self):
        config = _root({'foo': 5, 'bar': 6})
        valid = config.get({'foo': confit.Integer()})
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
        valid = config.get({'foo': confit.Integer()})
        self.assertEqual(valid.foo, 5)

    def test_missing_required_value_raises_error_on_validate(self):
        config = _root({})
        with self.assertRaises(confit.NotFoundError):
            config.get({'foo': confit.Integer()})

    def test_none_as_default(self):
        config = _root({})
        valid = config.get({'foo': confit.Integer(None)})
        self.assertIsNone(valid['foo'])

    def test_wrong_type_raises_error_on_validate(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigTypeError):
            config.get({'foo': confit.Integer()})

    def test_validate_individual_value(self):
        config = _root({'foo': 5})
        valid = config['foo'].get(confit.Integer())
        self.assertEqual(valid, 5)

    def test_nested_dict_template(self):
        config = _root({
            'foo': {'bar': 9},
        })
        valid = config.get({
            'foo': {'bar': confit.Integer()},
        })
        self.assertEqual(valid['foo']['bar'], 9)

    def test_nested_attribute_access(self):
        config = _root({
            'foo': {'bar': 8},
        })
        valid = config.get({
            'foo': {'bar': confit.Integer()},
        })
        self.assertEqual(valid.foo.bar, 8)


class AsTemplateTest(unittest.TestCase):
    def test_plain_int_as_template(self):
        typ = confit.as_template(int)
        self.assertIsInstance(typ, confit.Integer)
        self.assertEqual(typ.default, confit.REQUIRED)

    def test_concrete_int_as_template(self):
        typ = confit.as_template(2)
        self.assertIsInstance(typ, confit.Integer)
        self.assertEqual(typ.default, 2)

    def test_plain_string_as_template(self):
        typ = confit.as_template(str)
        self.assertIsInstance(typ, confit.String)
        self.assertEqual(typ.default, confit.REQUIRED)

    def test_concrete_string_as_template(self):
        typ = confit.as_template('foo')
        self.assertIsInstance(typ, confit.String)
        self.assertEqual(typ.default, 'foo')

    @unittest.skipIf(confit.PY3, "unicode only present in Python 2")
    def test_unicode_type_as_template(self):
        typ = confit.as_template(unicode)
        self.assertIsInstance(typ, confit.String)
        self.assertEqual(typ.default, confit.REQUIRED)

    @unittest.skipIf(confit.PY3, "basestring only present in Python 2")
    def test_basestring_as_template(self):
        typ = confit.as_template(basestring)
        self.assertIsInstance(typ, confit.String)
        self.assertEqual(typ.default, confit.REQUIRED)

    def test_dict_as_template(self):
        typ = confit.as_template({'key': 9})
        self.assertIsInstance(typ, confit.MappingTemplate)
        self.assertIsInstance(typ.subtemplates['key'], confit.Integer)
        self.assertEqual(typ.subtemplates['key'].default, 9)

    def test_nested_dict_as_template(self):
        typ = confit.as_template({'outer': {'inner': 2}})
        self.assertIsInstance(typ, confit.MappingTemplate)
        self.assertIsInstance(typ.subtemplates['outer'],
                              confit.MappingTemplate)
        self.assertIsInstance(typ.subtemplates['outer'].subtemplates['inner'],
                              confit.Integer)
        self.assertEqual(typ.subtemplates['outer'].subtemplates['inner']
                         .default, 2)

    def test_list_as_template(self):
        typ = confit.as_template(list())
        self.assertIsInstance(typ, confit.OneOf)
        self.assertEqual(typ.default, confit.REQUIRED)

    def test_set_as_template(self):
        typ = confit.as_template(set())
        self.assertIsInstance(typ, confit.Choice)

    def test_float_type_as_tempalte(self):
        typ = confit.as_template(float)
        self.assertIsInstance(typ, confit.Number)
        self.assertEqual(typ.default, confit.REQUIRED)

    def test_none_as_template(self):
        typ = confit.as_template(None)
        self.assertIs(type(typ), confit.Template)
        self.assertEqual(typ.default, confit.REQUIRED)

    def test_dict_type_as_template(self):
        typ = confit.as_template(dict)
        self.assertIsInstance(typ, confit.TypeTemplate)
        self.assertEqual(typ.typ, collections.Mapping)
        self.assertEqual(typ.default, confit.REQUIRED)

    def test_list_type_as_template(self):
        typ = confit.as_template(list)
        self.assertIsInstance(typ, confit.TypeTemplate)
        self.assertEqual(typ.typ, collections.Sequence)
        self.assertEqual(typ.default, confit.REQUIRED)

    def test_set_type_as_template(self):
        typ = confit.as_template(set)
        self.assertIsInstance(typ, confit.TypeTemplate)
        self.assertEqual(typ.typ, set)
        self.assertEqual(typ.default, confit.REQUIRED)

    def test_other_type_as_template(self):
        class MyClass(object):
            pass
        typ = confit.as_template(MyClass)
        self.assertIsInstance(typ, confit.TypeTemplate)
        self.assertEqual(typ.typ, MyClass)
        self.assertEqual(typ.default, confit.REQUIRED)


class StringTemplateTest(unittest.TestCase):
    def test_validate_string(self):
        config = _root({'foo': 'bar'})
        valid = config.get({'foo': confit.String()})
        self.assertEqual(valid['foo'], 'bar')

    def test_string_default_value(self):
        config = _root({})
        valid = config.get({'foo': confit.String('baz')})
        self.assertEqual(valid['foo'], 'baz')

    def test_pattern_matching(self):
        config = _root({'foo': 'bar', 'baz': 'zab'})
        valid = config.get({'foo': confit.String(pattern='^ba.$')})
        self.assertEqual(valid['foo'], 'bar')
        with self.assertRaises(confit.ConfigValueError):
            config.get({'baz': confit.String(pattern='!')})

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
        with self.assertRaises(confit.ConfigTypeError):
            config.get({'foo': confit.String()})


class NumberTest(unittest.TestCase):
    def test_validate_int_as_number(self):
        config = _root({'foo': 2})
        valid = config['foo'].get(confit.Number())
        self.assertIsInstance(valid, int)
        self.assertEqual(valid, 2)

    def test_validate_float_as_number(self):
        config = _root({'foo': 3.0})
        valid = config['foo'].get(confit.Number())
        self.assertIsInstance(valid, float)
        self.assertEqual(valid, 3.0)

    def test_validate_string_as_number(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(confit.Number())


class ChoiceTest(unittest.TestCase):
    def test_validate_good_choice_in_list(self):
        config = _root({'foo': 2})
        valid = config['foo'].get(confit.Choice([1, 2, 4, 8, 16]))
        self.assertEqual(valid, 2)

    def test_validate_bad_choice_in_list(self):
        config = _root({'foo': 3})
        with self.assertRaises(confit.ConfigValueError):
            config['foo'].get(confit.Choice([1, 2, 4, 8, 16]))

    def test_validate_good_choice_in_dict(self):
        config = _root({'foo': 2})
        valid = config['foo'].get(confit.Choice({2: 'two', 4: 'four'}))
        self.assertEqual(valid, 'two')

    def test_validate_bad_choice_in_dict(self):
        config = _root({'foo': 3})
        with self.assertRaises(confit.ConfigValueError):
            config['foo'].get(confit.Choice({2: 'two', 4: 'four'}))


class OneOfTest(unittest.TestCase):
    def test_default_value(self):
        config = _root({})
        valid = config['foo'].get(confit.OneOf([], default='bar'))
        self.assertEqual(valid, 'bar')

    def test_validate_good_choice_in_list(self):
        config = _root({'foo': 2})
        valid = config['foo'].get(confit.OneOf([
            confit.String(),
            confit.Integer(),
        ]))
        self.assertEqual(valid, 2)

    def test_validate_first_good_choice_in_list(self):
        config = _root({'foo': 3.14})
        valid = config['foo'].get(confit.OneOf([
            confit.Integer(),
            confit.Number(),
        ]))
        self.assertEqual(valid, 3)

    def test_validate_no_choice_in_list(self):
        config = _root({'foo': None})
        with self.assertRaises(confit.ConfigValueError):
            config['foo'].get(confit.OneOf([
                confit.String(),
                confit.Integer(),
            ]))

    def test_validate_bad_template(self):
        class BadTemplate(object):
            pass
        config = _root({})
        with self.assertRaises(confit.ConfigTemplateError):
            config.get(confit.OneOf([BadTemplate()]))
        del BadTemplate


class StrSeqTest(unittest.TestCase):
    def test_string_list(self):
        config = _root({'foo': ['bar', 'baz']})
        valid = config['foo'].get(confit.StrSeq())
        self.assertEqual(valid, ['bar', 'baz'])

    def test_string_tuple(self):
        config = _root({'foo': ('bar', 'baz')})
        valid = config['foo'].get(confit.StrSeq())
        self.assertEqual(valid, ['bar', 'baz'])

    def test_whitespace_separated_string(self):
        config = _root({'foo': 'bar   baz'})
        valid = config['foo'].get(confit.StrSeq())
        self.assertEqual(valid, ['bar', 'baz'])

    def test_invalid_type(self):
        config = _root({'foo': 9})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(confit.StrSeq())

    def test_invalid_sequence_type(self):
        config = _root({'foo': ['bar', 2126]})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(confit.StrSeq())


class FilenameTest(unittest.TestCase):
    def test_filename_relative_to_working_dir(self):
        config = _root({'foo': 'bar'})
        valid = config['foo'].get(confit.Filename(cwd='/dev/null'))
        self.assertEqual(valid, os.path.realpath('/dev/null/bar'))

    def test_filename_relative_to_sibling(self):
        config = _root({'foo': '/', 'bar': 'baz'})
        valid = config.get({
            'foo': confit.Filename(),
            'bar': confit.Filename(relative_to='foo')
        })
        self.assertEqual(valid.foo, os.path.realpath('/'))
        self.assertEqual(valid.bar, os.path.realpath('/baz'))

    def test_filename_working_dir_overrides_sibling(self):
        config = _root({'foo': 'bar'})
        valid = config.get({
            'foo': confit.Filename(cwd='/dev/null', relative_to='baz')
        })
        self.assertEqual(valid.foo, os.path.realpath('/dev/null/bar'))

    def test_filename_relative_to_sibling_with_recursion(self):
        config = _root({'foo': '/', 'bar': 'r', 'baz': 'z'})
        with self.assertRaises(confit.ConfigTemplateError):
            config.get({
                'foo': confit.Filename(relative_to='bar'),
                'bar': confit.Filename(relative_to='baz'),
                'baz': confit.Filename(relative_to='foo')
            })

    def test_filename_relative_to_self(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigTemplateError):
            config.get({
                'foo': confit.Filename(relative_to='foo')
            })

    def test_filename_relative_to_sibling_needs_siblings(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigTemplateError):
            config['foo'].get(confit.Filename(relative_to='bar'))

    def test_filename_relative_to_sibling_needs_template(self):
        config = _root({'foo': '/', 'bar': 'baz'})
        with self.assertRaises(confit.ConfigTemplateError):
            config.get({
                'bar': confit.Filename(relative_to='foo')
            })

    def test_filename_with_non_file_source(self):
        config = _root({'foo': 'foo/bar'})
        valid = config['foo'].get(confit.Filename())
        self.assertEqual(valid, os.path.join(os.getcwd(), 'foo', 'bar'))

    def test_filename_with_file_source(self):
        source = confit.ConfigSource({'foo': 'foo/bar'},
                                     filename='/baz/config.yaml')
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        valid = config['foo'].get(confit.Filename())
        self.assertEqual(valid, os.path.realpath('/config/path/foo/bar'))

    def test_filename_with_default_source(self):
        source = confit.ConfigSource({'foo': 'foo/bar'},
                                     filename='/baz/config.yaml',
                                     default=True)
        config = _root(source)
        config.config_dir = lambda: '/config/path'
        valid = config['foo'].get(confit.Filename())
        self.assertEqual(valid, os.path.realpath('/config/path/foo/bar'))

    def test_filename_wrong_type(self):
        config = _root({'foo': 8})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(confit.Filename())


class BaseTemplateTest(unittest.TestCase):
    def test_base_template_accepts_any_value(self):
        config = _root({'foo': 4.2})
        valid = config['foo'].get(confit.Template())
        self.assertEqual(valid, 4.2)

    def test_base_template_required(self):
        config = _root({})
        with self.assertRaises(confit.NotFoundError):
            config['foo'].get(confit.Template())

    def test_base_template_with_default(self):
        config = _root({})
        valid = config['foo'].get(confit.Template('bar'))
        self.assertEqual(valid, 'bar')


class TypeTemplateTest(unittest.TestCase):
    def test_correct_type(self):
        config = _root({'foo': set()})
        valid = config['foo'].get(confit.TypeTemplate(set))
        self.assertEqual(valid, set())

    def test_incorrect_type(self):
        config = _root({'foo': dict()})
        with self.assertRaises(confit.ConfigTypeError):
            config['foo'].get(confit.TypeTemplate(set))

    def test_missing_required_value(self):
        config = _root({})
        with self.assertRaises(confit.NotFoundError):
            config['foo'].get(confit.TypeTemplate(set))

    def test_default_value(self):
        config = _root({})
        valid = config['foo'].get(confit.TypeTemplate(set, set([1, 2])))
        self.assertEqual(valid, set([1, 2]))
