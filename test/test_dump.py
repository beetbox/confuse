import confit
import textwrap
from . import unittest, _root


class PrettyDumpTest(unittest.TestCase):
    def test_dump_null(self):
        config = confit.Configuration('myapp', read=False)
        config.add({'foo': None})
        yaml = config.dump().strip()
        self.assertEqual(yaml, 'foo:')

    def test_dump_true(self):
        config = confit.Configuration('myapp', read=False)
        config.add({'foo': True})
        yaml = config.dump().strip()
        self.assertEqual(yaml, 'foo: yes')

    def test_dump_false(self):
        config = confit.Configuration('myapp', read=False)
        config.add({'foo': False})
        yaml = config.dump().strip()
        self.assertEqual(yaml, 'foo: no')

    def test_dump_short_list(self):
        config = confit.Configuration('myapp', read=False)
        config.add({'foo': ['bar', 'baz']})
        yaml = config.dump().strip()
        self.assertEqual(yaml, 'foo: [bar, baz]')

    def test_dump_ordered_dict(self):
        odict = confit.OrderedDict()
        odict['foo'] = 'bar'
        odict['bar'] = 'baz'
        odict['baz'] = 'qux'

        config = confit.Configuration('myapp', read=False)
        config.add({'key': odict})
        yaml = config.dump().strip()
        self.assertEqual(yaml, textwrap.dedent("""
            key:
                foo: bar
                bar: baz
                baz: qux
        """).strip())
