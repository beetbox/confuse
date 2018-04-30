from __future__ import division, absolute_import, print_function

import confuse
import argparse
from argparse import Namespace
import optparse
import unittest


class ArgparseTest(unittest.TestCase):
    def setUp(self):
        self.config = confuse.Configuration('test', read=False)
        self.parser = argparse.ArgumentParser()

    def _parse(self, args, **kwargs):
        args = self.parser.parse_args(args.split())
        self.config.set_args(args, **kwargs)

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

    def test_nested_destination_single(self):
        self.parser.add_argument('--one', dest='one.foo')
        self.parser.add_argument('--two', dest='one.two.foo')
        self._parse('--two TWO', dots=True)
        self.assertEqual(self.config['one']['two']['foo'].get(), 'TWO')

    def test_nested_destination_nested(self):
        self.parser.add_argument('--one', dest='one.foo')
        self.parser.add_argument('--two', dest='one.two.foo')
        self._parse('--two TWO --one ONE', dots=True)
        self.assertEqual(self.config['one']['foo'].get(), 'ONE')
        self.assertEqual(self.config['one']['two']['foo'].get(), 'TWO')

    def test_nested_destination_nested_rev(self):
        self.parser.add_argument('--one', dest='one.foo')
        self.parser.add_argument('--two', dest='one.two.foo')
        # Reverse to ensure order doesn't matter
        self._parse('--one ONE --two TWO', dots=True)
        self.assertEqual(self.config['one']['foo'].get(), 'ONE')
        self.assertEqual(self.config['one']['two']['foo'].get(), 'TWO')

    def test_nested_destination_clobber(self):
        self.parser.add_argument('--one', dest='one.two')
        self.parser.add_argument('--two', dest='one.two.foo')
        self._parse('--two TWO --one ONE', dots=True)
        # Clobbered
        self.assertEqual(self.config['one']['two'].get(), {'foo': 'TWO'})
        self.assertEqual(self.config['one']['two']['foo'].get(), 'TWO')

    def test_nested_destination_clobber_rev(self):
        # Reversed order
        self.parser.add_argument('--two', dest='one.two.foo')
        self.parser.add_argument('--one', dest='one.two')
        self._parse('--one ONE --two TWO', dots=True)
        # Clobbered just the same
        self.assertEqual(self.config['one']['two'].get(), {'foo': 'TWO'})
        self.assertEqual(self.config['one']['two']['foo'].get(), 'TWO')


class OptparseTest(unittest.TestCase):
    def setUp(self):
        self.config = confuse.Configuration('test', read=False)
        self.parser = optparse.OptionParser()

    def _parse(self, args, **kwargs):
        options, _ = self.parser.parse_args(args.split())
        self.config.set_args(options, **kwargs)

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

    def test_nested_destination_single(self):
        self.parser.add_option('--one', dest='one.foo')
        self.parser.add_option('--two', dest='one.two.foo')
        self._parse('--two TWO', dots=True)
        self.assertEqual(self.config['one']['two']['foo'].get(), 'TWO')

    def test_nested_destination_nested(self):
        self.parser.add_option('--one', dest='one.foo')
        self.parser.add_option('--two', dest='one.two.foo')
        self._parse('--two TWO --one ONE', dots=True)
        self.assertEqual(self.config['one']['foo'].get(), 'ONE')
        self.assertEqual(self.config['one']['two']['foo'].get(), 'TWO')

    def test_nested_destination_nested_rev(self):
        self.parser.add_option('--one', dest='one.foo')
        self.parser.add_option('--two', dest='one.two.foo')
        # Reverse to ensure order doesn't matter
        self._parse('--one ONE --two TWO', dots=True)
        self.assertEqual(self.config['one']['foo'].get(), 'ONE')
        self.assertEqual(self.config['one']['two']['foo'].get(), 'TWO')


class GenericNamespaceTest(unittest.TestCase):
    def setUp(self):
        self.config = confuse.Configuration('test', read=False)

    def test_value_added_to_root(self):
        self.config.set_args(Namespace(foo='bar'))
        self.assertEqual(self.config['foo'].get(), 'bar')

    def test_value_added_to_subview(self):
        self.config['baz'].set_args(Namespace(foo='bar'))
        self.assertEqual(self.config['baz']['foo'].get(), 'bar')

    def test_nested_namespace(self):
        args = Namespace(
            first="Hello",
            nested=Namespace(
                second="World"
            )
        )
        self.config.set_args(args, dots=True)
        self.assertEqual(self.config['first'].get(), 'Hello')
        self.assertEqual(self.config['nested']['second'].get(), 'World')
