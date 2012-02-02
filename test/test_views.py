import unittest
import confit

def _root(*sources):
    return confit.RootView(sources)

class ViewTest(unittest.TestCase):
    def test_key_access(self):
        config = _root({'foo': 'bar'})
        value = config['foo'].get()
        self.assertEqual(value, 'bar')
