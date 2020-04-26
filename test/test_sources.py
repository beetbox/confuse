from __future__ import division, absolute_import, print_function

import confuse
import unittest


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

    # def test_load_cast_dict(self):
    #     src = confuse.ConfigSource.of('asdf.yml')
    #     self.assertEqual(src.loaded, False)
    #     self.assertEqual(dict(src), {'a': 5, 'file': 'asdf.yml'})
    #     self.assertEqual(src.loaded, True)

    def test_load_keys(self):
        src = confuse.ConfigSource.of('asdf.yml')
        self.assertEqual(src.loaded, False)
        self.assertEqual(set(src.keys()), {'a', 'file'})
        self.assertEqual(src.loaded, True)
