import errno
import ntpath
import os
import platform
import posixpath
import shutil
import tempfile
import unittest
from typing import ClassVar
from unittest.mock import Mock

import pytest

import confuse
import confuse.yaml_util

DEFAULT = (platform.system, os.environ, os.path)
SYSTEMS = {
    "Linux": ({"HOME": "/home/test", "XDG_CONFIG_HOME": "~/xdgconfig"}, posixpath),
    "Darwin": ({"HOME": "/Users/test"}, posixpath),
    "Windows": (
        {
            "APPDATA": "~\\winconfig",
            "HOME": "C:\\Users\\test",
            "USERPROFILE": "C:\\Users\\test",
        },
        ntpath,
    ),
}


def _touch(path):
    open(path, "a").close()


class FakeHome(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.home = tempfile.mkdtemp()
        os.environ["HOME"] = self.home
        os.environ["USERPROFILE"] = self.home

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.home)


class FakeSystem(unittest.TestCase):
    SYS_NAME: ClassVar[str]

    def setUp(self):
        super().setUp()
        self.os_path = os.path
        os.environ = {}  # type: ignore[assignment]

        environ, os.path = SYSTEMS[self.SYS_NAME]
        os.environ.update(environ)
        platform.system = lambda: self.SYS_NAME

    def tearDown(self):
        super().tearDown()
        platform.system, os.environ, os.path = DEFAULT


class LinuxTestCases(FakeSystem):
    SYS_NAME = "Linux"

    def test_both_xdg_and_fallback_dirs(self):
        assert confuse.config_dirs() == [
            "/home/test/.config",
            "/home/test/xdgconfig",
            "/etc/xdg",
            "/etc",
        ]

    def test_fallback_only(self):
        del os.environ["XDG_CONFIG_HOME"]
        assert confuse.config_dirs() == ["/home/test/.config", "/etc/xdg", "/etc"]

    def test_xdg_matching_fallback_not_duplicated(self):
        os.environ["XDG_CONFIG_HOME"] = "~/.config"
        assert confuse.config_dirs() == ["/home/test/.config", "/etc/xdg", "/etc"]

    def test_xdg_config_dirs(self):
        os.environ["XDG_CONFIG_DIRS"] = "/usr/local/etc/xdg:/etc/xdg"
        assert confuse.config_dirs() == [
            "/home/test/.config",
            "/home/test/xdgconfig",
            "/usr/local/etc/xdg",
            "/etc/xdg",
            "/etc",
        ]


class OSXTestCases(FakeSystem):
    SYS_NAME = "Darwin"

    def test_mac_dirs(self):
        assert confuse.config_dirs() == [
            "/Users/test/.config",
            "/Users/test/Library/Application Support",
            "/etc/xdg",
            "/etc",
        ]

    def test_xdg_config_dirs(self):
        os.environ["XDG_CONFIG_DIRS"] = "/usr/local/etc/xdg:/etc/xdg"
        assert confuse.config_dirs() == [
            "/Users/test/.config",
            "/Users/test/Library/Application Support",
            "/usr/local/etc/xdg",
            "/etc/xdg",
            "/etc",
        ]


class WindowsTestCases(FakeSystem):
    SYS_NAME = "Windows"

    def test_dir_from_environ(self):
        assert confuse.config_dirs() == [
            "C:\\Users\\test\\AppData\\Roaming",
            "C:\\Users\\test\\winconfig",
        ]

    def test_fallback_dir(self):
        del os.environ["APPDATA"]
        assert confuse.config_dirs() == ["C:\\Users\\test\\AppData\\Roaming"]


class ConfigFilenamesTest(unittest.TestCase):
    def setUp(self):
        self._old = os.path.isfile, confuse.yaml_util.load_yaml
        os.path.isfile = lambda x: True  # type: ignore[assignment]
        confuse.yaml_util.load_yaml = lambda *args, **kwargs: {}

    def tearDown(self):
        os.path.isfile, confuse.yaml_util.load_yaml = self._old

    def test_no_sources_when_files_missing(self):
        config = confuse.Configuration("myapp", read=False)
        filenames = [s.filename for s in config.sources]
        assert filenames == []

    def test_search_package(self):
        config = confuse.Configuration("myapp", __name__, read=False)
        config._add_default_source()

        for source in config.sources:
            if source.default:
                default_source = source
                break
        else:
            self.fail("no default source")

        assert default_source.filename == os.path.join(
            os.path.dirname(__file__), "config_default.yaml"
        )
        assert source.default


class EnvVarTest(FakeHome):
    def setUp(self):
        super().setUp()
        self.config = confuse.Configuration("myapp", read=False)
        os.environ["MYAPPDIR"] = self.home  # use the tmp home as a config dir

    def test_env_var_name(self):
        assert self.config._env_var == "MYAPPDIR"

    def test_env_var_dir_has_first_priority(self):
        assert self.config.config_dir() == self.home

    def test_env_var_missing(self):
        del os.environ["MYAPPDIR"]
        assert self.config.config_dir() != self.home


@unittest.skipUnless(platform.system() == "Linux", "Linux-specific tests")
class PrimaryConfigDirTest(FakeHome, FakeSystem):
    SYS_NAME = "Linux"  # conversion from posix to nt is easy

    def setUp(self):
        super().setUp()

        self.config = confuse.Configuration("test", read=False)

    def test_create_dir_if_none_exists(self):
        path = os.path.join(self.home, ".config", "test")
        assert not os.path.exists(path)

        assert self.config.config_dir() == path
        assert os.path.isdir(path)

    def test_return_existing_dir(self):
        path = os.path.join(self.home, "xdgconfig", "test")
        os.makedirs(path)
        _touch(os.path.join(path, confuse.CONFIG_FILENAME))
        assert self.config.config_dir() == path

    def test_do_not_create_dir_if_lower_priority_exists(self):
        path1 = os.path.join(self.home, "xdgconfig", "test")
        path2 = os.path.join(self.home, ".config", "test")
        os.makedirs(path2)
        _touch(os.path.join(path2, confuse.CONFIG_FILENAME))
        assert not os.path.exists(path1)
        assert os.path.exists(path2)

        assert self.config.config_dir() == path2
        assert not os.path.isdir(path1)
        assert os.path.isdir(path2)


@pytest.mark.parametrize("error", [errno.EACCES, errno.EROFS])
@pytest.mark.parametrize("read_mode", ["explicit", "automatic", "lazy"])
def test_missing_user_config_reads_defaults_without_creating_directory(
    tmp_path, monkeypatch, error, read_mode
):
    user_dir = tmp_path / "missing" / "myapp"
    package = tmp_path / "package"
    package.mkdir()
    (package / confuse.DEFAULT_FILENAME).write_text("answer: 42\n")
    monkeypatch.delenv("MYAPPDIR", raising=False)
    monkeypatch.setattr(confuse.util, "config_dirs", lambda: [str(user_dir.parent)])
    monkeypatch.setattr(confuse.util, "find_package_path", lambda _: str(package))
    makedirs = Mock(side_effect=OSError(error, os.strerror(error)))
    monkeypatch.setattr(os, "makedirs", makedirs)

    config: confuse.Configuration
    if read_mode == "lazy":
        config = confuse.LazyConfig("myapp", "package")
    else:
        config = confuse.Configuration(
            "myapp", "package", read=read_mode == "automatic"
        )
        if read_mode == "explicit":
            config.read()

    assert config["answer"].get(int) == 42
    assert config.user_config_path() == str(user_dir / confuse.CONFIG_FILENAME)
    assert not user_dir.exists()
    makedirs.assert_not_called()


@pytest.mark.parametrize("error", [errno.EACCES, errno.EROFS])
def test_explicit_config_dir_still_raises(tmp_path, monkeypatch, error):
    user_dir = tmp_path / "myapp"
    monkeypatch.setenv("MYAPPDIR", str(user_dir))
    config = confuse.Configuration("myapp", read=False)
    makedirs = Mock(side_effect=OSError(error, os.strerror(error)))
    monkeypatch.setattr(os, "makedirs", makedirs)

    with pytest.raises(OSError, match=os.strerror(error)) as exc_info:
        config.config_dir()

    assert exc_info.value.errno == error
    makedirs.assert_called_once_with(str(user_dir))


@pytest.mark.parametrize("selection", ["environment", "first", "second", "fallback"])
def test_user_config_path_preserves_discovery_order(tmp_path, monkeypatch, selection):
    dirs = [tmp_path / "first", tmp_path / "second"]
    monkeypatch.delenv("MYAPPDIR", raising=False)
    monkeypatch.setattr(confuse.util, "config_dirs", lambda: list(map(str, dirs)))
    for index, directory in enumerate(dirs):
        if selection != "fallback" and (index == 1 or selection != "second"):
            appdir = directory / "myapp"
            appdir.mkdir(parents=True)
            (appdir / confuse.CONFIG_FILENAME).write_text("value: user\n")
    expected = dirs[1 if selection == "second" else 0] / "myapp"
    if selection == "environment":
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("USERPROFILE", str(tmp_path))
        monkeypatch.setenv("MYAPPDIR", "~/override")
        expected = tmp_path / "override"
    config = confuse.Configuration("myapp", read=False)
    makedirs = Mock()
    monkeypatch.setattr(os, "makedirs", makedirs)

    assert config.user_config_path() == str(expected / confuse.CONFIG_FILENAME)
    makedirs.assert_not_called()
    assert config.config_dir() == str(expected)
    makedirs.assert_called_once_with(str(expected))


def test_user_config_path_rejects_environment_file(tmp_path, monkeypatch):
    filename = tmp_path / "file"
    filename.touch()
    monkeypatch.setenv("MYAPPDIR", str(filename))
    config = confuse.Configuration("myapp", read=False)

    with pytest.raises(confuse.ConfigError, match="MYAPPDIR must be a directory"):
        config.user_config_path()


@pytest.mark.parametrize("error", [errno.EACCES, errno.EIO])
def test_existing_user_config_read_errors_propagate(tmp_path, monkeypatch, error):
    filename = tmp_path / confuse.CONFIG_FILENAME
    filename.write_text("answer: 42\n")
    monkeypatch.setenv("MYAPPDIR", str(tmp_path))
    config = confuse.Configuration("myapp", read=False)
    monkeypatch.setattr(
        "builtins.open", Mock(side_effect=OSError(error, os.strerror(error)))
    )

    with pytest.raises(confuse.ConfigReadError, match=r"config\.yaml") as exc_info:
        config.read()

    assert exc_info.value.name == str(filename)
    assert isinstance(exc_info.value.reason, OSError)
    assert exc_info.value.reason.errno == error
