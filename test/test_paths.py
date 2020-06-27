from __future__ import division, absolute_import, print_function

import confuse
import confuse.yaml_util
import ntpath
import os
import platform
import posixpath
import shutil
import tempfile
import unittest


DEFAULT = [platform.system, os.environ, os.path]

SYSTEMS = {
    'Linux': [{'HOME': '/home/test', 'XDG_CONFIG_HOME': '~/xdgconfig'},
              posixpath],
    'Darwin': [{'HOME': '/Users/test'}, posixpath],
    'Windows': [{
        'APPDATA': '~\\winconfig',
        'HOME': 'C:\\Users\\test',
        'USERPROFILE': 'C:\\Users\\test',
    }, ntpath]
}


def _touch(path):
    open(path, 'a').close()


class FakeSystem(unittest.TestCase):
    SYS_NAME = None
    TMP_HOME = False

    def setUp(self):
        if self.SYS_NAME in SYSTEMS:
            self.os_path = os.path
            os.environ = {}

            environ, os.path = SYSTEMS[self.SYS_NAME]
            os.environ.update(environ)  # copy
            platform.system = lambda: self.SYS_NAME

        if self.TMP_HOME:
            self.home = tempfile.mkdtemp()
            os.environ['HOME'] = self.home
            os.environ['USERPROFILE'] = self.home

    def tearDown(self):
        platform.system, os.environ, os.path = DEFAULT
        if hasattr(self, 'home'):
            shutil.rmtree(self.home)


class LinuxTestCases(FakeSystem):
    SYS_NAME = 'Linux'

    def test_both_xdg_and_fallback_dirs(self):
        self.assertEqual(confuse.config_dirs(),
                         ['/home/test/.config', '/home/test/xdgconfig',
                          '/etc/xdg', '/etc'])

    def test_fallback_only(self):
        del os.environ['XDG_CONFIG_HOME']
        self.assertEqual(confuse.config_dirs(), ['/home/test/.config',
                                                 '/etc/xdg', '/etc'])

    def test_xdg_matching_fallback_not_duplicated(self):
        os.environ['XDG_CONFIG_HOME'] = '~/.config'
        self.assertEqual(confuse.config_dirs(), ['/home/test/.config',
                                                 '/etc/xdg', '/etc'])

    def test_xdg_config_dirs(self):
        os.environ['XDG_CONFIG_DIRS'] = '/usr/local/etc/xdg:/etc/xdg'
        self.assertEqual(confuse.config_dirs(), ['/home/test/.config',
                                                 '/home/test/xdgconfig',
                                                 '/usr/local/etc/xdg',
                                                 '/etc/xdg', '/etc'])


class OSXTestCases(FakeSystem):
    SYS_NAME = 'Darwin'

    def test_mac_dirs(self):
        self.assertEqual(confuse.config_dirs(),
                         ['/Users/test/.config',
                          '/Users/test/Library/Application Support',
                          '/etc/xdg', '/etc'])

    def test_xdg_config_dirs(self):
        os.environ['XDG_CONFIG_DIRS'] = '/usr/local/etc/xdg:/etc/xdg'
        self.assertEqual(confuse.config_dirs(),
                         ['/Users/test/.config',
                          '/Users/test/Library/Application Support',
                          '/usr/local/etc/xdg',
                          '/etc/xdg', '/etc'])


class WindowsTestCases(FakeSystem):
    SYS_NAME = 'Windows'

    def test_dir_from_environ(self):
        self.assertEqual(confuse.config_dirs(),
                         ['C:\\Users\\test\\AppData\\Roaming',
                          'C:\\Users\\test\\winconfig'])

    def test_fallback_dir(self):
        del os.environ['APPDATA']
        self.assertEqual(confuse.config_dirs(),
                         ['C:\\Users\\test\\AppData\\Roaming'])


class ConfigFilenamesTest(unittest.TestCase):
    def setUp(self):
        self._old = os.path.isfile, confuse.yaml_util.load_yaml
        os.path.isfile = lambda x: True
        confuse.yaml_util.load_yaml = lambda *args, **kwargs: {}

    def tearDown(self):
        confuse.yaml_util.load_yaml, os.path.isfile = self._old

    def test_no_sources_when_files_missing(self):
        config = confuse.Configuration('myapp', read=False)
        filenames = [s.filename for s in config.sources]
        self.assertEqual(filenames, [])

    def test_search_package(self):
        config = confuse.Configuration('myapp', __name__, read=False)
        config._add_default_source()

        for source in config.sources:
            if source.default:
                default_source = source
                break
        else:
            self.fail("no default source")

        self.assertEqual(
            default_source.filename,
            os.path.join(os.path.dirname(__file__), 'config_default.yaml')
        )
        self.assertTrue(source.default)


class EnvVarTest(FakeSystem):
    TMP_HOME = True

    def setUp(self):
        super(EnvVarTest, self).setUp()
        self.config = confuse.Configuration('myapp', read=False)
        os.environ['MYAPPDIR'] = self.home  # use the tmp home as a config dir

    def test_env_var_name(self):
        self.assertEqual(self.config._env_var, 'MYAPPDIR')

    def test_env_var_dir_has_first_priority(self):
        self.assertEqual(self.config.config_dir(), self.home)

    def test_env_var_missing(self):
        del os.environ['MYAPPDIR']
        self.assertNotEqual(self.config.config_dir(), self.home)


class PrimaryConfigDirTest(FakeSystem):
    SYS_NAME = 'Linux'  # conversion from posix to nt is easy
    TMP_HOME = True

    if platform.system() == 'Windows':
        # wrap these functions as they need to work on the host system which is
        # only needed on Windows as we are using `posixpath`
        def join(self, *args):
            return self.os_path.normpath(self.os_path.join(*args))

        def makedirs(self, path, *args):
            os.path, os_path = self.os_path, os.path
            self._makedirs(path, *args)
            os.path = os_path

    def setUp(self):
        super(PrimaryConfigDirTest, self).setUp()
        if hasattr(self, 'join'):
            os.path.join = self.join
            os.makedirs, self._makedirs = self.makedirs, os.makedirs

        self.config = confuse.Configuration('test', read=False)

    def tearDown(self):
        super(PrimaryConfigDirTest, self).tearDown()
        if hasattr(self, '_makedirs'):
            os.makedirs = self._makedirs

    def test_create_dir_if_none_exists(self):
        path = os.path.join(self.home, '.config', 'test')
        assert not os.path.exists(path)

        self.assertEqual(self.config.config_dir(), path)
        self.assertTrue(os.path.isdir(path))

    def test_return_existing_dir(self):
        path = os.path.join(self.home, 'xdgconfig', 'test')
        os.makedirs(path)
        _touch(os.path.join(path, confuse.CONFIG_FILENAME))
        self.assertEqual(self.config.config_dir(), path)

    def test_do_not_create_dir_if_lower_priority_exists(self):
        path1 = os.path.join(self.home, 'xdgconfig', 'test')
        path2 = os.path.join(self.home, '.config', 'test')
        os.makedirs(path2)
        _touch(os.path.join(path2, confuse.CONFIG_FILENAME))
        assert not os.path.exists(path1)
        assert os.path.exists(path2)

        self.assertEqual(self.config.config_dir(), path2)
        self.assertFalse(os.path.isdir(path1))
        self.assertTrue(os.path.isdir(path2))
