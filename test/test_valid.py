import confit
from . import _root, unittest


class ValidConfigTest(unittest.TestCase):
    def test_validate_simple_dict(self):
        config = _root({'foo': 5})
        valid = config.validate({'foo': confit.Integer()})
        self.assertEqual(valid['foo'], 5)

    def test_default_value(self):
        config = _root({})
        valid = config.validate({'foo': confit.Integer(8)})
        self.assertEqual(valid['foo'], 8)

    def test_undeclared_key_raises_keyerror(self):
        config = _root({'foo': 5})
        valid = config.validate({'foo': confit.Integer()})
        with self.assertRaises(KeyError):
            valid['bar']

    def test_undeclared_key_ignored_from_input(self):
        config = _root({'foo': 5, 'bar': 6})
        valid = config.validate({'foo': confit.Integer()})
        with self.assertRaises(KeyError):
            valid['bar']

    def test_int_type_shortcut(self):
        config = _root({'foo': 5})
        valid = config.validate({'foo': int})
        self.assertEqual(valid['foo'], 5)

    def test_int_default_shortcut(self):
        config = _root({})
        valid = config.validate({'foo': 9})
        self.assertEqual(valid['foo'], 9)

    def test_attribute_access(self):
        config = _root({'foo': 5})
        valid = config.validate({'foo': confit.Integer()})
        self.assertEqual(valid.foo, 5)

    def test_missing_required_value_raises_error_on_validate(self):
        config = _root({})
        with self.assertRaises(confit.NotFoundError):
            config.validate({'foo': confit.Integer(required=True)})

    def test_wrong_type_raises_error_on_validate(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.ConfigError):
            config.validate({'foo': confit.Integer()})

    def test_validate_individual_value(self):
        config = _root({'foo': 5})
        valid = config['foo'].validate(confit.Integer())
        self.assertEqual(valid, 5)

    def test_nested_dict_template(self):
        config = _root({
            'foo': {'bar': 9},
        })
        valid = config.validate({
            'foo': {'bar': confit.Integer()},
        })
        self.assertEqual(valid['foo']['bar'], 9)


class AsTypeTest(unittest.TestCase):
    def test_plain_int_as_type(self):
        typ = confit.as_type(int)
        self.assertIsInstance(typ, confit.Integer)
        self.assertEqual(typ.default, None)

    def test_concrete_int_as_type(self):
        typ = confit.as_type(2)
        self.assertIsInstance(typ, confit.Integer)
        self.assertEqual(typ.default, 2)

    def test_dict_as_type(self):
        typ = confit.as_type({'key': 9})
        self.assertIsInstance(typ, confit.MappingTemplate)
        self.assertIsInstance(typ.template['key'], confit.Integer)
        self.assertEqual(typ.template['key'].default, 9)

    def test_nested_dict_as_type(self):
        typ = confit.as_type({'outer': {'inner': 2}})
        self.assertIsInstance(typ, confit.MappingTemplate)
        self.assertIsInstance(typ.template['outer'], confit.MappingTemplate)
        self.assertIsInstance(typ.template['outer'].template['inner'],
                              confit.Integer)
        self.assertEqual(typ.template['outer'].template['inner'].default, 2)
