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


@pytest.mark.parametrize("full", [True, False])
def test_dump_validated_sequence(full):
    config = confuse.Configuration("myapp", read=False)
    config.add(
        confuse.ConfigSource(
            {
                "servers": [
                    {"host": "one.example.com"},
                    {"host": "two.example.com", "port": 8000},
                ],
                "default_only": "retained",
            },
            default=True,
        )
    )
    valid = config.get(
        {"servers": confuse.Sequence({"host": str, "port": confuse.Integer(80)})}
    )
    config.set(
        {"servers": [*valid.servers, {"host": "three.example.com", "port": 8080}]}
    )

    dumped = yaml.safe_load(config.dump(full=full))

    expected: dict[str, object] = {
        "servers": [
            {"host": "one.example.com", "port": 80},
            {"host": "two.example.com", "port": 8000},
            {"host": "three.example.com", "port": 8080},
        ]
    }
    if full:
        expected["default_only"] = "retained"
    assert dumped == expected
    assert list(dumped["servers"][0]) == ["host", "port"]
    assert isinstance(valid.servers[0], confuse.AttrDict)
    assert valid.servers[0].port == 80


@pytest.mark.parametrize("full", [True, False])
def test_dump_nested_validated_mappings(full):
    config = confuse.Configuration("myapp", read=False)
    config.set(
        {"groups": [{"name": "first", "servers": [{"host": "one.example.com"}]}]}
    )
    valid = config.get(
        {
            "groups": confuse.Sequence(
                {
                    "name": str,
                    "servers": confuse.Sequence(
                        {
                            "host": str,
                            "options": confuse.MappingTemplate(
                                {"port": confuse.Integer(80)}
                            ),
                        }
                    ),
                }
            )
        }
    )
    config.set(valid)

    dumped = yaml.safe_load(config.dump(full=full))

    assert dumped == {
        "groups": [
            {
                "name": "first",
                "servers": [{"host": "one.example.com", "options": {"port": 80}}],
            }
        ]
    }
    assert isinstance(valid.groups[0], confuse.AttrDict)
    assert isinstance(valid.groups[0].servers[0].options, confuse.AttrDict)
    assert valid.groups[0].servers[0].options.port == 80


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
