import confuse
import unittest


class PersistentConfigTest(unittest.TestCase):

    def test_add(self):
        config = confuse.PersistentConfig('myapp', read=False)
        config.add({'foo': False})
        del config

        config_test = confuse.Configuration('myapp', read=True)
        yaml_dump = config_test.dump().strip()
        assert yaml_dump == 'foo: no'

    def test_set(self):
        config = confuse.PersistentConfig('myapp', read=False)
        config['s'] = 'string'
        config.set({'abc': 6})
        del config

        config_test = confuse.Configuration('myapp', read=True)
        yaml_dump = config_test.dump().strip()
        assert yaml_dump == 'abc: 6\ns: string'
