import enum
import os
import pathlib
import unittest

import pytest

import confuse

from . import _root


class TypeCheckTest(unittest.TestCase):
    def test_str_type_correct(self):
        config = _root({"foo": "bar"})
        value = config["foo"].get(str)
        assert value == "bar"

    def test_str_type_incorrect(self):
        config = _root({"foo": 2})
        with pytest.raises(confuse.ConfigTypeError):
            config["foo"].get(str)

    def test_int_type_correct(self):
        config = _root({"foo": 2})
        value = config["foo"].get(int)
        assert value == 2

    def test_int_type_incorrect(self):
        config = _root({"foo": "bar"})
        with pytest.raises(confuse.ConfigTypeError):
            config["foo"].get(int)


class TestBuiltInValidator:
    def test_as_filename_with_non_file_source(self):
        config = _root({"foo": "foo/bar"})
        value = config["foo"].as_filename()
        assert value == os.path.join(os.getcwd(), "foo", "bar")

    def test_as_filename_with_file_source(self):
        source = confuse.ConfigSource({"foo": "foo/bar"}, filename="/baz/config.yaml")
        config = _root(source)
        config.config_dir = lambda: "/config/path"  # type: ignore[attr-defined]
        value = config["foo"].as_filename()
        assert value == os.path.realpath("/config/path/foo/bar")

    def test_as_filename_with_default_source(self):
        source = confuse.ConfigSource(
            {"foo": "foo/bar"}, filename="/baz/config.yaml", default=True
        )
        config = _root(source)
        config.config_dir = lambda: "/config/path"  # type: ignore[attr-defined]
        value = config["foo"].as_filename()
        assert value == os.path.realpath("/config/path/foo/bar")

    def test_as_filename_wrong_type(self):
        config = _root({"foo": None})
        with pytest.raises(confuse.ConfigTypeError):
            config["foo"].as_filename()

    def test_as_path(self):
        config = _root({"foo": "foo/bar"})
        path_str = os.path.join(os.getcwd(), "foo", "bar")
        value = config["foo"].as_path()
        path = pathlib.Path(path_str)
        assert value == path

    @pytest.mark.parametrize(
        "config, expected_value",
        [
            ({"foo": "foo/bar"}, pathlib.Path(os.getcwd(), "foo", "bar")),
            ({"foo": None}, None),
            ({}, None),
        ],
    )
    def test_as_optional_path(self, config, expected_value):
        config = _root(config)
        value = config["foo"].as_optional_path()
        assert value == expected_value

    def test_as_choice_correct(self):
        config = _root({"foo": "bar"})
        value = config["foo"].as_choice(["foo", "bar", "baz"])
        assert value == "bar"

    def test_as_choice_error(self):
        config = _root({"foo": "bar"})
        with pytest.raises(confuse.ConfigValueError):
            config["foo"].as_choice(["foo", "baz"])

    def test_as_choice_with_dict(self):
        config = _root({"foo": "bar"})
        res = config["foo"].as_choice(
            {
                "bar": "baz",
                "x": "y",
            }
        )
        assert res == "baz"

    def test_as_choice_with_enum(self):
        class Foobar(enum.Enum):
            Foo = "bar"

        config = _root({"foo": Foobar.Foo.value})
        res = config["foo"].as_choice(Foobar)
        assert res == Foobar.Foo

    def test_as_choice_with_enum_error(self):
        class Foobar(enum.Enum):
            Foo = "bar"

        config = _root({"foo": "foo"})
        with pytest.raises(confuse.ConfigValueError):
            config["foo"].as_choice(Foobar)

    def test_as_number_float(self):
        config = _root({"f": 1.0})
        config["f"].as_number()

    def test_as_number_int(self):
        config = _root({"i": 2})
        config["i"].as_number()

    def test_as_number_string(self):
        config = _root({"s": "a"})
        with pytest.raises(confuse.ConfigTypeError):
            config["s"].as_number()

    def test_as_str_seq_str(self):
        config = _root({"k": "a b c"})
        assert config["k"].as_str_seq() == ["a", "b", "c"]

    def test_as_str_seq_list(self):
        config = _root({"k": ["a b", "c"]})
        assert config["k"].as_str_seq() == ["a b", "c"]

    def test_as_str(self):
        config = _root({"s": "foo"})
        config["s"].as_str()

    def test_as_str_non_string(self):
        config = _root({"f": 1.0})
        with pytest.raises(confuse.ConfigTypeError):
            config["f"].as_str()

    def test_as_str_expanded(self):
        config = _root({"s": "${CONFUSE_TEST_VAR}/bar"})
        os.environ["CONFUSE_TEST_VAR"] = "foo"
        assert config["s"].as_str_expanded() == "foo/bar"

    def test_as_pairs(self):
        config = _root({"k": [{"a": "A"}, "b", ["c", "C"]]})
        assert [("a", "A"), ("b", None), ("c", "C")] == config["k"].as_pairs()


@pytest.mark.parametrize("accessor", ["as_filename", "as_path", "as_optional_path"])
@pytest.mark.parametrize("option", ["cwd", "in_app_dir", "in_source_dir"])
def test_path_accessor_resolution_options(tmp_path, monkeypatch, accessor, option):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    monkeypatch.setenv("ACCESSORTESTDIR", str(app_dir))
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source = source_dir / "config.yaml"
    source.write_text("path: nested/file.txt\n", encoding="utf-8")
    config = confuse.Configuration("AccessorTest", read=False)
    config.set_file(str(source))
    options = {option: str(tmp_path / "working") if option == "cwd" else True}
    expected_base = {
        "cwd": tmp_path / "working",
        "in_app_dir": app_dir,
        "in_source_dir": source_dir,
    }[option]
    expected = expected_base / "nested" / "file.txt"
    result = getattr(config["path"], accessor)(**options)
    assert result == (str(expected) if accessor == "as_filename" else expected)


@pytest.mark.parametrize("value", [None, {}])
def test_optional_path_options_preserve_missing_and_null(value, tmp_path):
    config = _root({"path": value} if value is None else {})
    assert config["path"].as_optional_path(cwd=str(tmp_path)) is None


@pytest.mark.parametrize("accessor", ["as_filename", "as_path", "as_optional_path"])
def test_path_accessor_precedence_and_updates(tmp_path, monkeypatch, accessor):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    monkeypatch.setenv("ACCESSORTESTDIR", str(app_dir))
    source = tmp_path / "config.yaml"
    source.write_text("path: file.txt\n", encoding="utf-8")
    config = confuse.Configuration("AccessorTest", read=False)
    config.set_file(str(source))
    get_path = getattr(config["path"], accessor)
    working = tmp_path / "working"
    assert (
        pathlib.Path(get_path(cwd=str(working), in_app_dir=True, in_source_dir=True))
        == working / "file.txt"
    )
    assert (
        pathlib.Path(get_path(in_app_dir=True, in_source_dir=True))
        == tmp_path / "file.txt"
    )
    absolute = tmp_path / "absolute.txt"
    config["path"].set(str(absolute))
    assert pathlib.Path(get_path(cwd=str(working))) == absolute
    config["path"].set(123)
    with pytest.raises(confuse.ConfigTypeError):
        get_path(cwd=str(working))
