import unittest

import pytest
import yaml

import confuse

from . import TempDir


def load(s):
    return yaml.load(s, Loader=confuse.Loader)


class ParseTest(unittest.TestCase):
    def test_dict_parsed_as_ordereddict(self):
        v = load("a: b\nc: d")
        assert isinstance(v, confuse.OrderedDict)
        assert list(v) == ["a", "c"]

    def test_string_beginning_with_percent(self):
        v = load("foo: %bar")
        assert v["foo"] == "%bar"


class FileParseTest(unittest.TestCase):
    def _parse_contents(self, contents):
        with TempDir() as temp:
            path = temp.sub("test_config.yaml", contents)
            return confuse.load_yaml(path)

    def test_load_file(self):
        v = self._parse_contents(b"foo: bar")
        assert v["foo"] == "bar"

    def test_syntax_error(self):
        with pytest.raises(confuse.ConfigError, match=r"test_config\.yaml"):
            self._parse_contents(b":")

    def test_reload_conf(self):
        with TempDir() as temp:
            path = temp.sub("test_config.yaml", b"foo: bar")
            config = confuse.Configuration("test", __name__)
            config.set_file(filename=path)
            assert config["foo"].get() == "bar"
            temp.sub("test_config.yaml", b"foo: bar2\ntest: hello world")
            config.reload()
            assert config["foo"].get() == "bar2"
            assert config["test"].get() == "hello world"

    def test_tab_indentation_error(self):
        with pytest.raises(confuse.ConfigError, match="found tab"):
            self._parse_contents(b"foo:\n\tbar: baz")


class StringParseTest(unittest.TestCase):
    def test_load_string(self):
        v = confuse.load_yaml_string("foo: bar", "test")
        assert v["foo"] == "bar"

    def test_string_syntax_error(self):
        with pytest.raises(confuse.ConfigError, match="test"):
            confuse.load_yaml_string(":", "test")

    def test_string_tab_indentation_error(self):
        with pytest.raises(confuse.ConfigError, match="found tab"):
            confuse.load_yaml_string("foo:\n\tbar: baz", "test")


class ParseAsScalarTest(unittest.TestCase):
    def test_text_string(self):
        v = confuse.yaml_util.parse_as_scalar("foo", confuse.Loader)
        assert v == "foo"

    def test_number_string_to_int(self):
        v = confuse.yaml_util.parse_as_scalar("1", confuse.Loader)
        assert isinstance(v, int)
        assert v == 1

    def test_number_string_to_float(self):
        v = confuse.yaml_util.parse_as_scalar("1.0", confuse.Loader)
        assert isinstance(v, float)
        assert v == 1.0

    def test_bool_string_to_bool(self):
        v = confuse.yaml_util.parse_as_scalar("true", confuse.Loader)
        assert v is True

    def test_empty_string_to_none(self):
        v = confuse.yaml_util.parse_as_scalar("", confuse.Loader)
        assert v is None

    def test_null_string_to_none(self):
        v = confuse.yaml_util.parse_as_scalar("null", confuse.Loader)
        assert v is None

    def test_dict_string_unchanged(self):
        v = confuse.yaml_util.parse_as_scalar('{"foo": "bar"}', confuse.Loader)
        assert v == '{"foo": "bar"}'

    def test_dict_unchanged(self):
        v = confuse.yaml_util.parse_as_scalar({"foo": "bar"}, confuse.Loader)
        assert v == {"foo": "bar"}

    def test_list_string_unchanged(self):
        v = confuse.yaml_util.parse_as_scalar('["foo", "bar"]', confuse.Loader)
        assert v == '["foo", "bar"]'

    def test_list_unchanged(self):
        v = confuse.yaml_util.parse_as_scalar(["foo", "bar"], confuse.Loader)
        assert v == ["foo", "bar"]

    def test_invalid_yaml_string_unchanged(self):
        v = confuse.yaml_util.parse_as_scalar("!", confuse.Loader)
        assert v == "!"
