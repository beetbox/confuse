import unittest
from argparse import Namespace
from collections import OrderedDict
from copy import deepcopy
from typing import Any

import pytest

import confuse


class BuildDictTests(unittest.TestCase):
    def test_pure_dicts(self):
        config = {"foo": {"bar": 1}}
        result = confuse.util.build_dict(config)
        assert 1 == result["foo"]["bar"]

    def test_namespaces(self):
        config = Namespace(foo=Namespace(bar=2), another=1)
        result = confuse.util.build_dict(config)
        assert 2 == result["foo"]["bar"]
        assert 1 == result["another"]

    def test_dot_sep_keys(self):
        config: dict[str, Any] = {"foo.bar": 1}
        result = confuse.util.build_dict(config.copy())
        assert 1 == result["foo.bar"]

        result = confuse.util.build_dict(config.copy(), sep=".")
        assert 1 == result["foo"]["bar"]

    def test_dot_sep_keys_clobber(self):
        args: list[tuple[str, Any]] = [("foo.bar", 1), ("foo.bar.zar", 2)]
        config = OrderedDict(args)
        result = confuse.util.build_dict(config.copy(), sep=".")
        assert {"zar": 2} == result["foo"]["bar"]
        assert 2 == result["foo"]["bar"]["zar"]

        # Reverse and do it again! (should be stable)
        args.reverse()
        config = OrderedDict(args)
        result = confuse.util.build_dict(config.copy(), sep=".")
        assert {"zar": 2} == result["foo"]["bar"]
        assert 2 == result["foo"]["bar"]["zar"]

    def test_dot_sep_keys_no_clobber(self):
        args: list[tuple[str, Any]] = [
            ("foo.bar", 1),
            ("foo.far", 2),
            ("foo.zar.dar", 4),
        ]
        config = OrderedDict(args)
        result = confuse.util.build_dict(config.copy(), sep=".")
        assert 1 == result["foo"]["bar"]
        assert 2 == result["foo"]["far"]
        assert 4 == result["foo"]["zar"]["dar"]

    def test_adjacent_underscores_sep_keys(self):
        config: dict[str, Any] = {"foo__bar_baz": 1}
        result = confuse.util.build_dict(config.copy())
        assert 1 == result["foo__bar_baz"]

        result = confuse.util.build_dict(config.copy(), sep="_")
        assert 1 == result["foo"][""]["bar"]["baz"]

        result = confuse.util.build_dict(config.copy(), sep="__")
        assert 1 == result["foo"]["bar_baz"]

    def test_keep_none(self):
        config = {"foo": None}
        result = confuse.util.build_dict(config.copy())
        with pytest.raises(KeyError):
            result["foo"]

        result = confuse.util.build_dict(config.copy(), keep_none=True)
        assert None is result["foo"]

    def test_keep_none_with_nested(self):
        config = {"foo": {"bar": None}}
        result = confuse.util.build_dict(config.copy())
        assert {} == result["foo"]

        result = confuse.util.build_dict(config.copy(), keep_none=True)
        assert None is result["foo"]["bar"]


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("namespace", [False, True])
@pytest.mark.parametrize("original", [5432, "local", [5432], None, {"fallback": 5432}])
@pytest.mark.parametrize("override", [5433, "remote", [5433], {"primary": 5433}])
def test_set_args_nested_leaf_override(original, override, namespace, reverse):
    entries = [
        ("database", {"host": "localhost", "port": original}),
        ("database.port", override),
    ]
    if reverse:
        entries.reverse()
    args: dict[str, Any] | Namespace = dict(entries)
    if namespace:
        args = Namespace(**args)
    before = deepcopy(args)
    config = confuse.Configuration("test", read=False)
    config.set_args(args, dots=True)
    expected = override
    if isinstance(original, dict) and isinstance(override, dict):
        expected = {**original, **override}
    assert config["database"].get() == {"host": "localhost", "port": expected}
    assert args == before


@pytest.mark.parametrize("reverse", [False, True])
def test_set_args_none_override_remains_ignored(reverse):
    entries = [("database", {"port": 5432}), ("database.port", None)]
    if reverse:
        entries.reverse()
    config = confuse.Configuration("test", read=False)
    config.set_args(dict(entries), dots=True)
    assert config["database"]["port"].get() == 5432


def test_build_dict_mapping_merge_retains_order_and_is_shallow():
    args: dict[str, Any] = {
        "database": {"options": {"first": 1, "nested": {"old": 2}}},
        "database.options": {"nested": {"new": 3}, "last": 4},
    }
    result = confuse.util.build_dict(args, sep=".")
    assert result == {
        "database": {"options": {"first": 1, "nested": {"new": 3}, "last": 4}}
    }
    assert list(result["database"]["options"]) == ["first", "nested", "last"]
    assert args["database"]["options"]["nested"] == {"old": 2}
