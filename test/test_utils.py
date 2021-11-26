from __future__ import division, absolute_import, print_function

from argparse import Namespace
from collections import OrderedDict
import confuse
import unittest


class BuildDictTests(unittest.TestCase):
    def test_pure_dicts(self):
        config = {'foo': {'bar': 1}}
        result = confuse.util.build_dict(config)
        self.assertEqual(1, result['foo']['bar'])

    def test_namespaces(self):
        config = Namespace(foo=Namespace(bar=2), another=1)
        result = confuse.util.build_dict(config)
        self.assertEqual(2, result['foo']['bar'])
        self.assertEqual(1, result['another'])

    def test_dot_sep_keys(self):
        config = {'foo.bar': 1}
        result = confuse.util.build_dict(config.copy())
        self.assertEqual(1, result['foo.bar'])

        result = confuse.util.build_dict(config.copy(), sep='.')
        self.assertEqual(1, result['foo']['bar'])

    def test_dot_sep_keys_clobber(self):
        args = [('foo.bar', 1), ('foo.bar.zar', 2)]
        config = OrderedDict(args)
        result = confuse.util.build_dict(config.copy(), sep='.')
        self.assertEqual({'zar': 2}, result['foo']['bar'])
        self.assertEqual(2, result['foo']['bar']['zar'])

        # Reverse and do it again! (should be stable)
        args.reverse()
        config = OrderedDict(args)
        result = confuse.util.build_dict(config.copy(), sep='.')
        self.assertEqual({'zar': 2}, result['foo']['bar'])
        self.assertEqual(2, result['foo']['bar']['zar'])

    def test_dot_sep_keys_no_clobber(self):
        args = [('foo.bar', 1), ('foo.far', 2), ('foo.zar.dar', 4)]
        config = OrderedDict(args)
        result = confuse.util.build_dict(config.copy(), sep='.')
        self.assertEqual(1, result['foo']['bar'])
        self.assertEqual(2, result['foo']['far'])
        self.assertEqual(4, result['foo']['zar']['dar'])

    def test_adjacent_underscores_sep_keys(self):
        config = {'foo__bar_baz': 1}
        result = confuse.util.build_dict(config.copy())
        self.assertEqual(1, result['foo__bar_baz'])

        result = confuse.util.build_dict(config.copy(), sep='_')
        self.assertEqual(1, result['foo']['']['bar']['baz'])

        result = confuse.util.build_dict(config.copy(), sep='__')
        self.assertEqual(1, result['foo']['bar_baz'])

    def test_keep_none(self):
        config = {'foo': None}
        result = confuse.util.build_dict(config.copy())
        with self.assertRaises(KeyError):
            result['foo']

        result = confuse.util.build_dict(config.copy(), keep_none=True)
        self.assertIs(None, result['foo'])

    def test_keep_none_with_nested(self):
        config = {'foo': {'bar': None}}
        result = confuse.util.build_dict(config.copy())
        self.assertEqual({}, result['foo'])

        result = confuse.util.build_dict(config.copy(), keep_none=True)
        self.assertIs(None, result['foo']['bar'])
