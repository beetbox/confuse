import ntpath
import os
import platform
import posixpath
import shutil
import tempfile
import unittest
from typing import ClassVar

import confuse
import confuse.yaml_util

DEFAULT = [platform.system, os.environ, os.path]

SYSTEMS = {
    "Linux": [{"HOME": "/home/test", "XDG_CONFIG_HOME": "~/xdgconfig"}, posixpath],
    "Darwin": [{"HOME": "/Users/test"}, posixpath],
    "Windows": [
        {
            "APPDATA": "~\\winconfig",
            "HOME": "C:\\Users\\test",
            "USERPROFILE": "C:\\Users\\test",
        },
        ntpath,
    ],
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
        os.environ = {}

        environ, os.path = SYSTEMS[self.SYS_NAME]
        os.environ.update(environ)  # copy
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
        os.path.isfile = lambda x: True
        confuse.yaml_util.load_yaml = lambda *args, **kwargs: {}

    def tearDown(self):
        confuse.yaml_util.load_yaml, os.path.isfile = self._old

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


@unittest.skipUnless(os.system == "Linux", "Linux-specific tests")
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
