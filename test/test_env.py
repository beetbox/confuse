import os
import unittest

import pytest

import confuse

from . import _root

ENVIRON = os.environ


class EnvSourceTest(unittest.TestCase):
    def setUp(self):
        os.environ = {}

    def tearDown(self):
        os.environ = ENVIRON

    def test_prefix(self):
        os.environ["TEST_FOO"] = "a"
        os.environ["BAR"] = "b"
        config = _root(confuse.EnvSource("TEST_"))
        assert config.get() == {"foo": "a"}

    def test_number_type_conversion(self):
        os.environ["TEST_FOO"] = "1"
        os.environ["TEST_BAR"] = "2.0"
        config = _root(confuse.EnvSource("TEST_"))
        foo = config["foo"].get()
        bar = config["bar"].get()
        assert isinstance(foo, int)
        assert foo == 1
        assert isinstance(bar, float)
        assert bar == 2.0

    def test_bool_type_conversion(self):
        os.environ["TEST_FOO"] = "true"
        os.environ["TEST_BAR"] = "FALSE"
        config = _root(confuse.EnvSource("TEST_"))
        assert config["foo"].get() is True
        assert config["bar"].get() is False

    def test_null_type_conversion(self):
        os.environ["TEST_FOO"] = "null"
        os.environ["TEST_BAR"] = ""
        config = _root(confuse.EnvSource("TEST_"))
        assert config["foo"].get() is None
        assert config["bar"].get() is None

    def test_unset_lower_config(self):
        os.environ["TEST_FOO"] = "null"
        config = _root({"foo": "bar"})
        assert config["foo"].get() == "bar"
        config.set(confuse.EnvSource("TEST_"))
        assert config["foo"].get() is None

    def test_sep_default(self):
        os.environ["TEST_FOO__BAR"] = "a"
        os.environ["TEST_FOO_BAZ"] = "b"
        config = _root(confuse.EnvSource("TEST_"))
        assert config["foo"]["bar"].get() == "a"
        assert config["foo_baz"].get() == "b"

    def test_sep_single_underscore_adjacent_seperators(self):
        os.environ["TEST_FOO__BAR"] = "a"
        os.environ["TEST_FOO_BAZ"] = "b"
        config = _root(confuse.EnvSource("TEST_", sep="_"))
        assert config["foo"][""]["bar"].get() == "a"
        assert config["foo"]["baz"].get() == "b"

    def test_nested(self):
        os.environ["TEST_FOO__BAR"] = "a"
        os.environ["TEST_FOO__BAZ__QUX"] = "b"
        config = _root(confuse.EnvSource("TEST_"))
        assert config["foo"]["bar"].get() == "a"
        assert config["foo"]["baz"]["qux"].get() == "b"

    def test_nested_rev(self):
        # Reverse to ensure order doesn't matter
        os.environ["TEST_FOO__BAZ__QUX"] = "b"
        os.environ["TEST_FOO__BAR"] = "a"
        config = _root(confuse.EnvSource("TEST_"))
        assert config["foo"]["bar"].get() == "a"
        assert config["foo"]["baz"]["qux"].get() == "b"

    def test_nested_clobber(self):
        os.environ["TEST_FOO__BAR"] = "a"
        os.environ["TEST_FOO__BAR__BAZ"] = "b"
        config = _root(confuse.EnvSource("TEST_"))
        # Clobbered
        assert config["foo"]["bar"].get() == {"baz": "b"}
        assert config["foo"]["bar"]["baz"].get() == "b"

    def test_nested_clobber_rev(self):
        # Reverse to ensure order doesn't matter
        os.environ["TEST_FOO__BAR__BAZ"] = "b"
        os.environ["TEST_FOO__BAR"] = "a"
        config = _root(confuse.EnvSource("TEST_"))
        # Clobbered
        assert config["foo"]["bar"].get() == {"baz": "b"}
        assert config["foo"]["bar"]["baz"].get() == "b"

    def test_lower_applied_after_prefix_match(self):
        os.environ["TEST_FOO"] = "a"
        config = _root(confuse.EnvSource("test_", lower=True))
        assert config.get() == {}

    def test_lower_already_lowercase(self):
        os.environ["TEST_foo"] = "a"
        config = _root(confuse.EnvSource("TEST_", lower=True))
        assert config.get() == {"foo": "a"}

    def test_lower_does_not_alter_value(self):
        os.environ["TEST_FOO"] = "UPPER"
        config = _root(confuse.EnvSource("TEST_", lower=True))
        assert config.get() == {"foo": "UPPER"}

    def test_lower_false(self):
        os.environ["TEST_FOO"] = "a"
        config = _root(confuse.EnvSource("TEST_", lower=False))
        assert config.get() == {"FOO": "a"}

    def test_handle_lists_good_list(self):
        os.environ["TEST_FOO__0"] = "a"
        os.environ["TEST_FOO__1"] = "b"
        os.environ["TEST_FOO__2"] = "c"
        config = _root(confuse.EnvSource("TEST_", handle_lists=True))
        assert config["foo"].get() == ["a", "b", "c"]

    def test_handle_lists_good_list_rev(self):
        # Reverse to ensure order doesn't matter
        os.environ["TEST_FOO__2"] = "c"
        os.environ["TEST_FOO__1"] = "b"
        os.environ["TEST_FOO__0"] = "a"
        config = _root(confuse.EnvSource("TEST_", handle_lists=True))
        assert config["foo"].get() == ["a", "b", "c"]

    def test_handle_lists_nested_lists(self):
        os.environ["TEST_FOO__0__0"] = "a"
        os.environ["TEST_FOO__0__1"] = "b"
        os.environ["TEST_FOO__1__0"] = "c"
        config = _root(confuse.EnvSource("TEST_", handle_lists=True))
        assert config["foo"].get() == [["a", "b"], ["c"]]

    def test_handle_lists_bad_list_missing_index(self):
        os.environ["TEST_FOO__0"] = "a"
        os.environ["TEST_FOO__2"] = "b"
        os.environ["TEST_FOO__3"] = "c"
        config = _root(confuse.EnvSource("TEST_", handle_lists=True))
        assert config["foo"].get() == {"0": "a", "2": "b", "3": "c"}

    def test_handle_lists_bad_list_non_zero_start(self):
        os.environ["TEST_FOO__1"] = "a"
        os.environ["TEST_FOO__2"] = "b"
        os.environ["TEST_FOO__3"] = "c"
        config = _root(confuse.EnvSource("TEST_", handle_lists=True))
        assert config["foo"].get() == {"1": "a", "2": "b", "3": "c"}

    def test_handle_lists_bad_list_non_numeric(self):
        os.environ["TEST_FOO__0"] = "a"
        os.environ["TEST_FOO__ONE"] = "b"
        os.environ["TEST_FOO__2"] = "c"
        config = _root(confuse.EnvSource("TEST_", handle_lists=True))
        assert config["foo"].get() == {"0": "a", "one": "b", "2": "c"}

    def test_handle_lists_top_level_always_dict(self):
        os.environ["TEST_0"] = "a"
        os.environ["TEST_1"] = "b"
        os.environ["TEST_2"] = "c"
        config = _root(confuse.EnvSource("TEST_", handle_lists=True))
        assert config.get() == {"0": "a", "1": "b", "2": "c"}

    def test_handle_lists_not_a_list(self):
        os.environ["TEST_FOO__BAR"] = "a"
        os.environ["TEST_FOO__BAZ"] = "b"
        config = _root(confuse.EnvSource("TEST_", handle_lists=True))
        assert config["foo"].get() == {"bar": "a", "baz": "b"}

    def test_parse_yaml_docs_scalar(self):
        os.environ["TEST_FOO"] = "a"
        config = _root(confuse.EnvSource("TEST_", parse_yaml_docs=True))
        assert config["foo"].get() == "a"

    def test_parse_yaml_docs_list(self):
        os.environ["TEST_FOO"] = "[a, b]"
        config = _root(confuse.EnvSource("TEST_", parse_yaml_docs=True))
        assert config["foo"].get() == ["a", "b"]

    def test_parse_yaml_docs_dict(self):
        os.environ["TEST_FOO"] = "{bar: a, baz: b}"
        config = _root(confuse.EnvSource("TEST_", parse_yaml_docs=True))
        assert config["foo"].get() == {"bar": "a", "baz": "b"}

    def test_parse_yaml_docs_nested(self):
        os.environ["TEST_FOO"] = "{bar: [a, b], baz: {qux: c}}"
        config = _root(confuse.EnvSource("TEST_", parse_yaml_docs=True))
        assert config["foo"]["bar"].get() == ["a", "b"]
        assert config["foo"]["baz"].get() == {"qux": "c"}

    def test_parse_yaml_docs_number_conversion(self):
        os.environ["TEST_FOO"] = "{bar: 1, baz: 2.0}"
        config = _root(confuse.EnvSource("TEST_", parse_yaml_docs=True))
        bar = config["foo"]["bar"].get()
        baz = config["foo"]["baz"].get()
        assert isinstance(bar, int)
        assert bar == 1
        assert isinstance(baz, float)
        assert baz == 2.0

    def test_parse_yaml_docs_bool_conversion(self):
        os.environ["TEST_FOO"] = "{bar: true, baz: FALSE}"
        config = _root(confuse.EnvSource("TEST_", parse_yaml_docs=True))
        assert config["foo"]["bar"].get() is True
        assert config["foo"]["baz"].get() is False

    def test_parse_yaml_docs_null_conversion(self):
        os.environ["TEST_FOO"] = "{bar: null, baz: }"
        config = _root(confuse.EnvSource("TEST_", parse_yaml_docs=True))
        assert config["foo"]["bar"].get() is None
        assert config["foo"]["baz"].get() is None

    def test_parse_yaml_docs_syntax_error(self):
        os.environ["TEST_FOO"] = "{:}"
        with pytest.raises(confuse.ConfigError, match="TEST_FOO"):
            _root(confuse.EnvSource("TEST_", parse_yaml_docs=True))

    def test_parse_yaml_docs_false(self):
        os.environ["TEST_FOO"] = "{bar: a, baz: b}"
        config = _root(confuse.EnvSource("TEST_", parse_yaml_docs=False))
        assert config["foo"].get() == "{bar: a, baz: b}"
        with pytest.raises(confuse.ConfigError):
            config["foo"]["bar"].get()


class ConfigEnvTest(unittest.TestCase):
    def setUp(self):
        self.config = confuse.Configuration("TestApp", read=False)
        os.environ = {
            "TESTAPP_FOO": "a",
            "TESTAPP_BAR__NESTED": "b",
            "TESTAPP_BAZ_SEP_NESTED": "c",
            "MYAPP_QUX_SEP_NESTED": "d",
        }

    def tearDown(self):
        os.environ = ENVIRON

    def test_defaults(self):
        self.config.set_env()
        assert self.config.get() == {
            "foo": "a",
            "bar": {"nested": "b"},
            "baz_sep_nested": "c",
        }

    def test_with_prefix(self):
        self.config.set_env(prefix="MYAPP_")
        assert self.config.get() == {"qux_sep_nested": "d"}

    def test_with_sep(self):
        self.config.set_env(sep="_sep_")
        assert self.config.get() == {
            "foo": "a",
            "bar__nested": "b",
            "baz": {"nested": "c"},
        }

    def test_with_prefix_and_sep(self):
        self.config.set_env(prefix="MYAPP_", sep="_sep_")
        assert self.config.get() == {"qux": {"nested": "d"}}
