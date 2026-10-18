import textwrap
import unittest
from collections import OrderedDict

import pytest
import yaml

import confuse

from . import _root


class PrettyDumpTest(unittest.TestCase):
    def test_dump_null(self):
        config = confuse.Configuration("myapp", read=False)
        config.add({"foo": None})
        yaml = config.dump().strip()
        assert yaml == "foo:"

    def test_dump_true(self):
        config = confuse.Configuration("myapp", read=False)
        config.add({"foo": True})
        yaml = config.dump().strip()
        assert yaml == "foo: yes"

    def test_dump_false(self):
        config = confuse.Configuration("myapp", read=False)
        config.add({"foo": False})
        yaml = config.dump().strip()
        assert yaml == "foo: no"

    def test_dump_short_list(self):
        config = confuse.Configuration("myapp", read=False)
        config.add({"foo": ["bar", "baz"]})
        yaml = config.dump().strip()
        assert yaml == "foo: [bar, baz]"

    def test_dump_ordered_dict(self):
        odict = OrderedDict()
        odict["foo"] = "bar"
        odict["bar"] = "baz"
        odict["baz"] = "qux"

        config = confuse.Configuration("myapp", read=False)
        config.add({"key": odict})
        yaml = config.dump().strip()
        assert (
            yaml
            == textwrap.dedent("""
            key:
                foo: bar
                bar: baz
                baz: qux
        """).strip()
        )

    def test_dump_sans_defaults(self):
        config = confuse.Configuration("myapp", read=False)
        config.add({"foo": "bar"})
        config.sources[0].default = True
        config.add({"baz": "qux"})

        yaml = config.dump().strip()
        assert yaml == "foo: bar\nbaz: qux"

        yaml = config.dump(full=False).strip()
        assert yaml == "baz: qux"


class RedactTest(unittest.TestCase):
    def test_no_redaction(self):
        config = _root({"foo": "bar"})
        data = config.flatten(redact=True)
        assert data == {"foo": "bar"}

    def test_redact_key(self):
        config = _root({"foo": "bar"})
        config["foo"].redact = True
        data = config.flatten(redact=True)
        assert data == {"foo": "REDACTED"}

    def test_unredact(self):
        config = _root({"foo": "bar"})
        config["foo"].redact = True
        config["foo"].redact = False
        data = config.flatten(redact=True)
        assert data == {"foo": "bar"}

    def test_dump_redacted(self):
        config = confuse.Configuration("myapp", read=False)
        config.add({"foo": "bar"})
        config["foo"].redact = True
        yaml = config.dump(redact=True).strip()
        assert yaml == "foo: REDACTED"

    def test_dump_unredacted(self):
        config = confuse.Configuration("myapp", read=False)
        config.add({"foo": "bar"})
        config["foo"].redact = True
        yaml = config.dump(redact=False).strip()
        assert yaml == "foo: bar"

    def test_dump_redacted_sans_defaults(self):
        config = confuse.Configuration("myapp", read=False)
        config.add({"foo": "bar"})
        config.sources[0].default = True
        config.add({"baz": "qux"})
        config["baz"].redact = True

        yaml = config.dump(redact=True, full=False).strip()
        assert yaml == "baz: REDACTED"


@pytest.mark.parametrize(
    "suffix", ["# trailing", "# trailing\n", "\n", "\n# trailing\n\n"]
)
def test_dump_defaults_with_trailing_comments(tmp_path, suffix):
    path = tmp_path / "config_default.yaml"
    path.write_text("# foo comment\nfoo: 42\n" + suffix, encoding="utf-8")
    config = confuse.Configuration("myapp", read=False)
    config.add(confuse.YamlSource(str(path), default=True))
    config.set({"foo": 43})
    assert config.dump() == "# foo comment\nfoo: 43\n"


@pytest.mark.parametrize("style", ["|", ">"])
def test_dump_defaults_preserves_block_scalar(tmp_path, style):
    default_data = f"text: {style}\n  # scalar content\n  value\nother: 1\n"
    path = tmp_path / "config_default.yaml"
    path.write_text(default_data, encoding="utf-8")
    config = confuse.Configuration("myapp", read=False)
    config.add(confuse.YamlSource(str(path), default=True))
    assert yaml.safe_load(config.dump()) == yaml.safe_load(default_data)
