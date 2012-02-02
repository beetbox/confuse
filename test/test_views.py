import unittest
import confit

def _root(*sources):
    return confit.RootView(sources)

class SingleSourceTest(unittest.TestCase):
    def test_dict_access(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].get()
        self.assertEqual(value, 'bar')

    def test_list_access(self):
        config = _root(['foo', 'bar'])
        value = config[1].get()
        self.assertEqual(value, 'bar')

    def test_nested_dict_list_access(self):
        config = _root({'foo': ['bar', 'baz']})
        value = config['foo'][1].get()
        self.assertEqual(value, 'baz')

    def test_nested_list_dict_access(self):
        config = _root([{'foo': 'bar'}, {'baz': 'qux'}])
        value = config[1]['baz'].get()
        self.assertEqual(value, 'qux')

    def test_missing_key(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.NotFoundError):
            config['baz'].get()

    def test_missing_index(self):
        config = _root(['foo', 'bar'])
        with self.assertRaises(confit.NotFoundError):
            config[5].get()

class TypeCheckTest(unittest.TestCase):
    def test_str_type_correct(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].get(str)
        self.assertEqual(value, 'bar')

    def test_str_type_incorrect(self):
        config = _root({'foo': 2})
        with self.assertRaises(confit.WrongTypeError):
            config['foo'].get(str)

    def test_int_type_correct(self):
        config = _root({'foo': 2})
        value = config['foo'].get(int)
        self.assertEqual(value, 2)

    def test_int_type_incorrect(self):
        config = _root({'foo': 'bar'})
        with self.assertRaises(confit.WrongTypeError):
            config['foo'].get(int)
