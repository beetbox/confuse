import unittest

import pytest

import confuse

from . import _root


class SingleSourceTest(unittest.TestCase):
    def test_dict_access(self):
        config = _root({"foo": "bar"})
        value = config["foo"].get()
        assert value == "bar"

    def test_list_access(self):
        config = _root({"foo": ["bar", "baz"]})
        value = config["foo"][1].get()
        assert value == "baz"

    def test_missing_key(self):
        config = _root({"foo": "bar"})
        with pytest.raises(confuse.NotFoundError):
            config["baz"].get()

    def test_missing_index(self):
        config = _root({"l": ["foo", "bar"]})
        with pytest.raises(confuse.NotFoundError):
            config["l"][5].get()

    def test_dict_iter(self):
        config = _root({"foo": "bar", "baz": "qux"})
        keys = [key for key in config]
        assert set(keys) == {"foo", "baz"}

    def test_list_iter(self):
        config = _root({"l": ["foo", "bar"]})
        items = [subview.get() for subview in config["l"]]
        assert items == ["foo", "bar"]

    def test_int_iter(self):
        config = _root({"n": 2})
        with pytest.raises(confuse.ConfigTypeError):
            [item for item in config["n"]]

    def test_dict_keys(self):
        config = _root({"foo": "bar", "baz": "qux"})
        keys = config.keys()
        assert set(keys) == {"foo", "baz"}

    def test_dict_values(self):
        config = _root({"foo": "bar", "baz": "qux"})
        values = [value.get() for value in config.values()]
        assert set(values) == {"bar", "qux"}

    def test_dict_items(self):
        config = _root({"foo": "bar", "baz": "qux"})
        items = [(key, value.get()) for (key, value) in config.items()]
        assert set(items) == {("foo", "bar"), ("baz", "qux")}

    def test_list_keys_error(self):
        config = _root({"l": ["foo", "bar"]})
        with pytest.raises(confuse.ConfigTypeError):
            config["l"].keys()

    def test_list_sequence(self):
        config = _root({"l": ["foo", "bar"]})
        items = [item.get() for item in config["l"].sequence()]
        assert items == ["foo", "bar"]

    def test_dict_sequence_error(self):
        config = _root({"foo": "bar", "baz": "qux"})
        with pytest.raises(confuse.ConfigTypeError):
            list(config.sequence())

    def test_dict_contents(self):
        config = _root({"foo": "bar", "baz": "qux"})
        contents = config.all_contents()
        assert set(contents) == {"foo", "baz"}

    def test_list_contents(self):
        config = _root({"l": ["foo", "bar"]})
        contents = config["l"].all_contents()
        assert list(contents) == ["foo", "bar"]

    def test_int_contents(self):
        config = _root({"n": 2})
        with pytest.raises(confuse.ConfigTypeError):
            list(config["n"].all_contents())


class ConverstionTest(unittest.TestCase):
    def test_str_conversion_from_str(self):
        config = _root({"foo": "bar"})
        value = str(config["foo"])
        assert value == "bar"

    def test_str_conversion_from_int(self):
        config = _root({"foo": 2})
        value = str(config["foo"])
        assert value == "2"

    def test_bool_conversion_from_bool(self):
        config = _root({"foo": True})
        value = bool(config["foo"])
        assert value

    def test_bool_conversion_from_int(self):
        config = _root({"foo": 0})
        value = bool(config["foo"])
        assert not value


class NameTest(unittest.TestCase):
    def test_root_name(self):
        config = _root()
        assert config.name == "root"

    def test_string_access_name(self):
        config = _root()
        name = config["foo"].name
        assert name == "foo"

    def test_int_access_name(self):
        config = _root()
        name = config[5].name
        assert name == "#5"

    def test_nested_access_name(self):
        config = _root()
        name = config[5]["foo"]["bar"][20].name
        assert name == "#5.foo.bar#20"


class MultipleSourceTest(unittest.TestCase):
    def test_dict_access_shadowed(self):
        config = _root({"foo": "bar"}, {"foo": "baz"})
        value = config["foo"].get()
        assert value == "bar"

    def test_dict_access_fall_through(self):
        config = _root({"qux": "bar"}, {"foo": "baz"})
        value = config["foo"].get()
        assert value == "baz"

    def test_dict_access_missing(self):
        config = _root({"qux": "bar"}, {"foo": "baz"})
        with pytest.raises(confuse.NotFoundError):
            config["fred"].get()

    def test_list_access_shadowed(self):
        config = _root({"l": ["a", "b"]}, {"l": ["c", "d", "e"]})
        value = config["l"][1].get()
        assert value == "b"

    def test_list_access_fall_through(self):
        config = _root({"l": ["a", "b"]}, {"l": ["c", "d", "e"]})
        value = config["l"][2].get()
        assert value == "e"

    def test_list_access_missing(self):
        config = _root({"l": ["a", "b"]}, {"l": ["c", "d", "e"]})
        with pytest.raises(confuse.NotFoundError):
            config["l"][3].get()

    def test_access_dict_replaced(self):
        config = _root({"foo": {"bar": "baz"}}, {"foo": {"qux": "fred"}})
        value = config["foo"].get()
        assert value == {"bar": "baz"}

    def test_dict_keys_merged(self):
        config = _root({"foo": {"bar": "baz"}}, {"foo": {"qux": "fred"}})
        keys = config["foo"].keys()
        assert set(keys) == {"bar", "qux"}

    def test_dict_keys_replaced(self):
        config = _root({"foo": {"bar": "baz"}}, {"foo": {"bar": "fred"}})
        keys = config["foo"].keys()
        assert list(keys) == ["bar"]

    def test_dict_values_merged(self):
        config = _root({"foo": {"bar": "baz"}}, {"foo": {"qux": "fred"}})
        values = [value.get() for value in config["foo"].values()]
        assert set(values) == {"baz", "fred"}

    def test_dict_values_replaced(self):
        config = _root({"foo": {"bar": "baz"}}, {"foo": {"bar": "fred"}})
        values = [value.get() for value in config["foo"].values()]
        assert list(values) == ["baz"]

    def test_dict_items_merged(self):
        config = _root({"foo": {"bar": "baz"}}, {"foo": {"qux": "fred"}})
        items = [(key, value.get()) for (key, value) in config["foo"].items()]
        assert set(items) == {("bar", "baz"), ("qux", "fred")}

    def test_dict_items_replaced(self):
        config = _root({"foo": {"bar": "baz"}}, {"foo": {"bar": "fred"}})
        items = [(key, value.get()) for (key, value) in config["foo"].items()]
        assert list(items) == [("bar", "baz")]

    def test_list_sequence_shadowed(self):
        config = _root({"l": ["a", "b"]}, {"l": ["c", "d", "e"]})
        items = [item.get() for item in config["l"].sequence()]
        assert items == ["a", "b"]

    def test_list_sequence_shadowed_by_dict(self):
        config = _root({"foo": {"bar": "baz"}}, {"foo": ["qux", "fred"]})
        with pytest.raises(confuse.ConfigTypeError):
            list(config["foo"].sequence())

    def test_dict_contents_concatenated(self):
        config = _root({"foo": {"bar": "baz"}}, {"foo": {"qux": "fred"}})
        contents = config["foo"].all_contents()
        assert set(contents) == {"bar", "qux"}

    def test_dict_contents_concatenated_not_replaced(self):
        config = _root({"foo": {"bar": "baz"}}, {"foo": {"bar": "fred"}})
        contents = config["foo"].all_contents()
        assert list(contents) == ["bar", "bar"]

    def test_list_contents_concatenated(self):
        config = _root({"foo": ["bar", "baz"]}, {"foo": ["qux", "fred"]})
        contents = config["foo"].all_contents()
        assert list(contents) == ["bar", "baz", "qux", "fred"]

    def test_int_contents_error(self):
        config = _root({"foo": ["bar", "baz"]}, {"foo": 5})
        with pytest.raises(confuse.ConfigTypeError):
            list(config["foo"].all_contents())

    def test_list_and_dict_contents_concatenated(self):
        config = _root({"foo": ["bar", "baz"]}, {"foo": {"qux": "fred"}})
        contents = config["foo"].all_contents()
        assert list(contents) == ["bar", "baz", "qux"]

    def test_add_source(self):
        config = _root({"foo": "bar"})
        config.add({"baz": "qux"})
        assert config["foo"].get() == "bar"
        assert config["baz"].get() == "qux"


class SetTest(unittest.TestCase):
    def test_set_missing_top_level_key(self):
        config = _root({})
        config["foo"] = "bar"
        assert config["foo"].get() == "bar"

    def test_override_top_level_key(self):
        config = _root({"foo": "bar"})
        config["foo"] = "baz"
        assert config["foo"].get() == "baz"

    def test_set_second_level_key(self):
        config = _root({})
        config["foo"]["bar"] = "baz"
        assert config["foo"]["bar"].get() == "baz"

    def test_override_second_level_key(self):
        config = _root({"foo": {"bar": "qux"}})
        config["foo"]["bar"] = "baz"
        assert config["foo"]["bar"].get() == "baz"

    def test_override_list_index(self):
        config = _root({"foo": ["a", "b", "c"]})
        config["foo"][1] = "bar"
        assert config["foo"][1].get() == "bar"
