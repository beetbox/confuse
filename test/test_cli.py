import confuse
import argparse
import optparse
from . import unittest

class ArgparseTest(unittest.TestCase):
    def setUp(self):
        self.config = confuse.Configuration('test', read=False)
        self.parser = argparse.ArgumentParser()

    def _parse(self, args):
        args = self.parser.parse_args(args.split())
        self.config.set_args(args)

    def test_text_argument_parsed(self):
        self.parser.add_argument('--foo', metavar='BAR')
        self._parse('--foo bar')
        self.assertEqual(self.config['foo'].get(), 'bar')

    def test_boolean_argument_parsed(self):
        self.parser.add_argument('--foo', action='store_true')
        self._parse('--foo')
        self.assertEqual(self.config['foo'].get(), True)

    def test_missing_optional_argument_not_included(self):
        self.parser.add_argument('--foo', metavar='BAR')
        self._parse('')
        with self.assertRaises(confuse.NotFoundError):
            self.config['foo'].get()

    def test_argument_overrides_default(self):
        self.config.add({'foo': 'baz'})

        self.parser.add_argument('--foo', metavar='BAR')
        self._parse('--foo bar')
        self.assertEqual(self.config['foo'].get(), 'bar')

class OptparseTest(unittest.TestCase):
    def setUp(self):
        self.config = confuse.Configuration('test', read=False)
        self.parser = optparse.OptionParser()

    def _parse(self, args):
        options, _ = self.parser.parse_args(args.split())
        self.config.set_args(options)

    def test_text_argument_parsed(self):
        self.parser.add_option('--foo', metavar='BAR')
        self._parse('--foo bar')
        self.assertEqual(self.config['foo'].get(), 'bar')

    def test_boolean_argument_parsed(self):
        self.parser.add_option('--foo', action='store_true')
        self._parse('--foo')
        self.assertEqual(self.config['foo'].get(), True)

    def test_missing_optional_argument_not_included(self):
        self.parser.add_option('--foo', metavar='BAR')
        self._parse('')
        with self.assertRaises(confuse.NotFoundError):
            self.config['foo'].get()

    def test_argument_overrides_default(self):
        self.config.add({'foo': 'baz'})

        self.parser.add_option('--foo', metavar='BAR')
        self._parse('--foo bar')
        self.assertEqual(self.config['foo'].get(), 'bar')

class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class GenericNamespaceTest(unittest.TestCase):
    def setUp(self):
        self.config = confuse.Configuration('test', read=False)

    def test_value_added_to_root(self):
        self.config.set_args(Namespace(foo='bar'))
        self.assertEqual(self.config['foo'].get(), 'bar')

    def test_value_added_to_subview(self):
        self.config['baz'].set_args(Namespace(foo='bar'))
        self.assertEqual(self.config['baz']['foo'].get(), 'bar')
