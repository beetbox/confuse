from __future__ import division, absolute_import, print_function

import confuse
import yaml
import unittest
from . import TempDir


def load(s):
    return yaml.load(s, Loader=confuse.Loader)


class ParseTest(unittest.TestCase):
    def test_dict_parsed_as_ordereddict(self):
        v = load("a: b\nc: d")
        self.assertTrue(isinstance(v, confuse.OrderedDict))
        self.assertEqual(list(v), ['a', 'c'])

    def test_string_beginning_with_percent(self):
        v = load("foo: %bar")
        self.assertEqual(v['foo'], '%bar')


class FileParseTest(unittest.TestCase):
    def _parse_contents(self, contents):
        with TempDir() as temp:
            path = temp.sub('test_config.yaml', contents)
            return confuse.load_yaml(path)

    def test_load_file(self):
        v = self._parse_contents(b'foo: bar')
        self.assertEqual(v['foo'], 'bar')

    def test_syntax_error(self):
        try:
            self._parse_contents(b':')
        except confuse.ConfigError as exc:
            self.assertTrue('test_config.yaml' in exc.name)
        else:
            self.fail('ConfigError not raised')

    def test_reload_conf(self):
        with TempDir() as temp:
            path = temp.sub('test_config.yaml', b'foo: bar')
            config = confuse.Configuration('test', __name__)
            config.set_file(filename=path)
            self.assertEqual(config['foo'].get(), 'bar')
            temp.sub('test_config.yaml', b'foo: bar2\ntest: hello world')
            config.reload()
            self.assertEqual(config['foo'].get(), 'bar2')
            self.assertEqual(config['test'].get(), 'hello world')

    def test_tab_indentation_error(self):
        try:
            self._parse_contents(b"foo:\n\tbar: baz")
        except confuse.ConfigError as exc:
            self.assertTrue('found tab' in exc.args[0])
        else:
            self.fail('ConfigError not raised')


class StringParseTest(unittest.TestCase):
    def test_load_string(self):
        v = confuse.load_yaml_string('foo: bar', 'test')
        self.assertEqual(v['foo'], 'bar')

    def test_string_syntax_error(self):
        try:
            confuse.load_yaml_string(':', 'test')
        except confuse.ConfigError as exc:
            self.assertTrue('test' in exc.name)
        else:
            self.fail('ConfigError not raised')

    def test_string_tab_indentation_error(self):
        try:
            confuse.load_yaml_string('foo:\n\tbar: baz', 'test')
        except confuse.ConfigError as exc:
            self.assertTrue('found tab' in exc.args[0])
        else:
            self.fail('ConfigError not raised')


class ParseAsScalarTest(unittest.TestCase):
    def test_text_string(self):
        v = confuse.yaml_util.parse_as_scalar('foo', confuse.Loader)
        self.assertEqual(v, 'foo')

    def test_number_string_to_int(self):
        v = confuse.yaml_util.parse_as_scalar('1', confuse.Loader)
        self.assertIsInstance(v, int)
        self.assertEqual(v, 1)

    def test_number_string_to_float(self):
        v = confuse.yaml_util.parse_as_scalar('1.0', confuse.Loader)
        self.assertIsInstance(v, float)
        self.assertEqual(v, 1.0)

    def test_bool_string_to_bool(self):
        v = confuse.yaml_util.parse_as_scalar('true', confuse.Loader)
        self.assertIs(v, True)

    def test_empty_string_to_none(self):
        v = confuse.yaml_util.parse_as_scalar('', confuse.Loader)
        self.assertIs(v, None)

    def test_null_string_to_none(self):
        v = confuse.yaml_util.parse_as_scalar('null', confuse.Loader)
        self.assertIs(v, None)

    def test_dict_string_unchanged(self):
        v = confuse.yaml_util.parse_as_scalar('{"foo": "bar"}', confuse.Loader)
        self.assertEqual(v, '{"foo": "bar"}')

    def test_dict_unchanged(self):
        v = confuse.yaml_util.parse_as_scalar({'foo': 'bar'}, confuse.Loader)
        self.assertEqual(v, {'foo': 'bar'})

    def test_list_string_unchanged(self):
        v = confuse.yaml_util.parse_as_scalar('["foo", "bar"]', confuse.Loader)
        self.assertEqual(v, '["foo", "bar"]')

    def test_list_unchanged(self):
        v = confuse.yaml_util.parse_as_scalar(['foo', 'bar'], confuse.Loader)
        self.assertEqual(v, ['foo', 'bar'])

    def test_invalid_yaml_string_unchanged(self):
        v = confuse.yaml_util.parse_as_scalar('!', confuse.Loader)
        self.assertEqual(v, '!')
