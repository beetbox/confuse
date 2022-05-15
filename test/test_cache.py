import unittest

import confuse
from confuse.cache import CachedConfigView, CachedHandle, CachedRootView
from confuse.exceptions import NotFoundError
from confuse.templates import Sequence


class CachedViewTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = CachedRootView([confuse.ConfigSource.of(
            {"a": ["b", "c"],
             "x": {"y": [1, 2], "w": "z", "p": {"q": 3}}})])
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
        with self.assertRaises(NotFoundError):
            handle.get()

    def test_multi_handle_invalidation(self):
        view: CachedConfigView = self.config['x']['w']
        handle = view.get_handle(str)
        self.assertEqual(handle.get(), 'z')

        self.config['x'] = {'y': [4, 5]}
        # new dict doesn't have a 'w' key
        with self.assertRaises(NotFoundError):
            handle.get()

    def test_list_update(self):
        pass

    def test_root_update(self):
        root = self.config
        handle = self.config.get_handle({'a': Sequence(str)})
        self.assertDictEqual(handle.get(), {'a': ['b', 'c']})
        root['a'] = ['c', 'd']
        self.assertDictEqual(handle.get(), {'a': ['c', 'd']})

    def test_invalidate_then_set(self):
        pass

    def test_parent_unset(self):
        view: CachedConfigView = self.config['x']['p']
        handle = view.get_handle(dict)
        self.assertEqual(handle.get(), {'q': 3})
        self.config['x']['p']['q'] = 4
        self.assertEqual(handle.get(), {'q': 4})
