from __future__ import division, absolute_import, print_function

import confuse
from confuse import CachedConfigView, CachedHandle, CachedRootView
import sys
import unittest

from confuse.exceptions import ConfigHandleInvalidatedError
from confuse.templates import Sequence

PY3 = sys.version_info[0] == 3


class CachedViewTest(unittest.TestCase):

    def setUp(self) -> None:
        self.config = CachedRootView([confuse.ConfigSource.of(
            {"a": ["b", "c"],
             "x": {"y": [1, 2], "w": "z"}})])
        return super().setUp()

    def test_basic(self):
        view: CachedConfigView = self.config['x']['y']
        handle: CachedHandle = view.get_handle(Sequence(int))
        self.assertEqual(handle.get(), [1, 2])

    def test_update(self):
        view: CachedConfigView = self.config['x']['y']
        handle: CachedHandle = view.get_handle(Sequence(int))
        self.config['x']['y'] = [4, 5]
        self.assertEqual(handle.get(), [4, 5])

    def test_subview_update(self):
        view: CachedConfigView = self.config['x']['y']
        handle: CachedHandle = view.get_handle(Sequence(int))
        self.config['x'] = {'y': [4, 5]}
        self.assertEqual(handle.get(), [4, 5])

    def test_invalidation(self):
        view: CachedConfigView = self.config['x']['y']
        handle: CachedHandle = view.get_handle(Sequence(int))

        self.config['x'] = {'p': [4, 5]}
        # new dict doesn't have a 'y' key
        with self.assertRaises(ConfigHandleInvalidatedError):
            handle.get()

    def test_multi_handle_invalidation(self):
        view: CachedConfigView = self.config['x']['w']
        handle = view.get_handle(str)
        self.assertEqual(handle.get(), 'z')

        self.config['x'] = {'y': [4, 5]}
        # new dict doesn't have a 'w' key
        with self.assertRaises(ConfigHandleInvalidatedError):
            handle.get()

    def test_list_update(self):
        pass

    def test_root_update(self):
        pass

    def test_root_invalidated(self):
        pass
