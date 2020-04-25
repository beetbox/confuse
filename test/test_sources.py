from __future__ import division, absolute_import, print_function

import os
import confuse
import sys
import unittest

PY3 = sys.version_info[0] == 3


class ConfigSourceTest(unittest.TestCase):
    def _load_yaml(self, file):
        return {'a': 5, 'file': file}

    def setUp(self):
        self._orig_load_yaml = confuse.load_yaml
        confuse.load_yaml = self._load_yaml

    def tearDown(self):
        confuse.load_yaml = self._orig_load_yaml

    def test_source_conversion(self):
        # test pure dict source
        src = confuse.ConfigSource.of({'a': 5})
        self.assertIsInstance(src, confuse.ConfigSource)
        self.assertEqual(src.loaded, True)
        # test yaml filename
        src = confuse.ConfigSource.of('asdf/asfdd.yml')
        self.assertIsInstance(src, confuse.YamlSource)
        self.assertEqual(src.loaded, False)
        self.assertEqual(src.exists, False)
        self.assertEqual(src.config_dir(create=False), 'asdf')

    def test_explicit_load(self):
        src = confuse.ConfigSource.of('asdf.yml')
        self.assertEqual(src.loaded, False)
        src.load()
        self.assertEqual(src.loaded, True)
        self.assertEqual(src['a'], 5)

    def test_load_getitem(self):
        src = confuse.ConfigSource.of('asdf.yml')
        self.assertEqual(src.loaded, False)
        self.assertEqual(src['a'], 5)
        self.assertEqual(src.loaded, True)

    def test_load_cast_dict(self):
        src = confuse.ConfigSource.of('asdf.yml')
        self.assertEqual(src.loaded, False)
        self.assertEqual(dict(src), {'a': 5, 'file': 'asdf.yml'})
        self.assertEqual(src.loaded, True)

    def test_load_keys(self):
        src = confuse.ConfigSource.of('asdf.yml')
        self.assertEqual(src.loaded, False)
        self.assertEqual(set(src.keys()), {'a', 'file'})
        self.assertEqual(src.loaded, True)


class EnvSourceTest(unittest.TestCase):
    def setenv(self, *a, **kw):
        for dct in a + (kw,):
            os.environ.update({k: str(v) for k, v in dct.items()})

    def test_env_var_load(self):
        prefix = 'asdf'
        expected = {'a': {'b': '5', 'c': '6'}, 'b': '7'}

        # setup environment
        before = set(os.environ.keys())
        self.setenv({prefix + 'a__b': 5, prefix + 'a__c': 6, prefix + 'b': 7})
        self.assertGreater(len(set(os.environ.keys()) - before), 0)

        src = confuse.EnvSource(prefix)
        self.assertEqual(src.loaded, False)
        src.load()
        self.assertEqual(src.loaded, True)
        print(src)
        self.assertEqual(dict(src), expected)
