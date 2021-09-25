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
            self.assertTrue('test_config.yaml' in exc.filename)
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
