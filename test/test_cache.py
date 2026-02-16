import unittest

import confuse
from confuse.cache import CachedConfigView, CachedHandle, CachedRootView
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

    def test_missing(self):
        view: CachedConfigView = self.config['x']['y']
        handle: CachedHandle = view.get_handle(Sequence(int))

        self.config['x'] = {'p': [4, 5]}
        # new dict doesn't have a 'y' key, but according to the view-theory,
        # it will get the value from the older view that has been shadowed.
        self.assertEqual(handle.get(), [1, 2])

    def test_missing2(self):
        view: CachedConfigView = self.config['x']['w']
        handle = view.get_handle(str)
        self.assertEqual(handle.get(), 'z')

        self.config['x'] = {'y': [4, 5]}
        self.assertEqual(handle.get(), 'z')

    def test_list_update(self):
        view: CachedConfigView = self.config['a'][1]
        handle = view.get_handle(str)
        self.assertEqual(handle.get(), 'c')
        self.config['a'][1] = 'd'
        self.assertEqual(handle.get(), 'd')

    def test_root_update(self):
        root = self.config
        handle = self.config.get_handle({'a': Sequence(str)})
        self.assertDictEqual(handle.get(), {'a': ['b', 'c']})
        root['a'] = ['c', 'd']
        self.assertDictEqual(handle.get(), {'a': ['c', 'd']})

    def test_parent_invalidation(self):
        view: CachedConfigView = self.config['x']['p']
        handle = view.get_handle(dict)
        self.assertEqual(handle.get(), {'q': 3})
        self.config['x']['p']['q'] = 4
        self.assertEqual(handle.get(), {'q': 4})
