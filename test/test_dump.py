import os
import sys
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
        self.assertEqual(yaml, 'foo: true')

    def test_dump_false(self):
        config = confit.Configuration('myapp', read=False)
        config.add({'foo': False})
        yaml = config.dump().strip()
        self.assertEqual(yaml, 'foo: false')

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

    def test_dump_sans_defaults(self):
        config = confit.Configuration('myapp', read=False)
        config.add({'foo': 'bar'})
        config.sources[0].default = True
        config.add({'baz': 'qux'})

        yaml = config.dump().strip()
        self.assertEqual(yaml, "foo: bar\nbaz: qux")

        yaml = config.dump(full=False).strip()
        self.assertEqual(yaml, "baz: qux")


class RedactTest(unittest.TestCase):
    def test_no_redaction(self):
        config = _root({'foo': 'bar'})
        data = config.flatten(redact=True)
        self.assertEqual(data, {'foo': 'bar'})

    def test_redact_key(self):
        config = _root({'foo': 'bar'})
        config['foo'].redact = True
        data = config.flatten(redact=True)
        self.assertEqual(data, {'foo': 'REDACTED'})

    def test_unredact(self):
        config = _root({'foo': 'bar'})
        config['foo'].redact = True
        config['foo'].redact = False
        data = config.flatten(redact=True)
        self.assertEqual(data, {'foo': 'bar'})

    def test_dump_redacted(self):
        config = confit.Configuration('myapp', read=False)
        config.add({'foo': 'bar'})
        config['foo'].redact = True
        yaml = config.dump(redact=True).strip()
        self.assertEqual(yaml, 'foo: REDACTED')

    def test_dump_unredacted(self):
        config = confit.Configuration('myapp', read=False)
        config.add({'foo': 'bar'})
        config['foo'].redact = True
        yaml = config.dump(redact=False).strip()
        self.assertEqual(yaml, 'foo: bar')

    def test_dump_redacted_sans_defaults(self):
        config = confit.Configuration('myapp', read=False)
        config.add({'foo': 'bar'})
        config.sources[0].default = True
        config.add({'baz': 'qux'})
        config['baz'].redact = True

        yaml = config.dump(redact=True, full=False).strip()
        self.assertEqual(yaml, "baz: REDACTED")

    @unittest.skipIf(sys.version_info <= (2, 7), reason="Unsupprted Python version!")
    def test_dump_comments(self):
        # self.maxDiff = None
        config = confit.Configuration("myapp",
                                      file="%s" % os.path.join(confit.get_parent_folder(__file__), 'comment-yaml.yml'))

        self.assertEqual(config.dump(default_flow_style=False).strip(), textwrap.dedent("""
############################################################
# +------------------------------------------------------+ #
# |                 Essentials (Global)                  | #
# +------------------------------------------------------+ #
############################################################

# A color code between 0-9 or a-f. Set to 'none' to disable.
ops-name-color: '4'
        """).strip())

        notes_yaml = os.path.join(confit.get_parent_folder(__file__), 'notes.yml')
        # print("Notes-Yaml: ", notes_yaml)
        config.add(confit.ConfigSource.from_file(notes_yaml))
        self.assertEqual(config.dump(default_flow_style=False).strip(), textwrap.dedent("""
        ############################################################
# +------------------------------------------------------+ #
# |                 Essentials (Global)                  | #
# +------------------------------------------------------+ #
############################################################

# A color code between 0-9 or a-f. Set to 'none' to disable.
ops-name-color: '4'
############################################################
# +------------------------------------------------------+ #
# |                       Notes                          | #
# +------------------------------------------------------+ #
############################################################
always-finish-her-first: true""").strip())
