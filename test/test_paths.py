import confit
import os
import platform
import tempfile
import shutil
from . import unittest

def _mock_system(plat):
    def system():
        return plat
    old = platform.system
    platform.system = system
    return old

def _mock_environ(home='/home'):
    old = os.environ
    os.environ = {
        'XDG_CONFIG_HOME': '~/xdgconfig',
        'APPDATA': '~\\winconfig',
        'HOME': home,
    }
    return old

def _mock_path(modname):
    old = os.path
    os.path = __import__(modname)
    return old

def _touch(path):
    open(path, 'a').close()

class ConfigDirsUnixTest(unittest.TestCase):
    def setUp(self):
        self.old_system = _mock_system('Linux')
        self.old_environ = _mock_environ()
        self.old_path = _mock_path('posixpath')
    def tearDown(self):
        platform.system = self.old_system
        os.envrion = self.old_environ
        os.path = self.old_path

    def test_both_xdg_and_fallback_dirs(self):
        dirs = confit.config_dirs()
        self.assertEqual(dirs, [
            '/home/.config',
            '/home/xdgconfig',
        ])

    def test_fallback_only(self):
        del os.environ['XDG_CONFIG_HOME']
        dirs = confit.config_dirs()
        self.assertEqual(dirs, ['/home/.config'])

    def test_xdg_matching_fallback_not_duplicated(self):
        os.environ['XDG_CONFIG_HOME'] = '~/.config'
        dirs = confit.config_dirs()
        self.assertEqual(dirs, ['/home/.config'])

class ConfigDirsMacTest(unittest.TestCase):
    def setUp(self):
        self.old_system = _mock_system('Darwin')
        self.old_environ = _mock_environ()
        self.old_path = _mock_path('posixpath')
    def tearDown(self):
        platform.system = self.old_system
        os.envrion = self.old_environ
        os.path = self.old_path

    def test_mac_and_unixy_dirs(self):
        dirs = confit.config_dirs()
        self.assertEqual(dirs, [
            '/home/Library/Application Support',
            '/home/.config',
            '/home/xdgconfig',
        ])

class ConfigDirsWindowsTest(unittest.TestCase):
    def setUp(self):
        self.old_system = _mock_system('Windows')
        self.old_environ = _mock_environ('c:\\home')
        self.old_path = _mock_path('ntpath')
    def tearDown(self):
        platform.system = self.old_system
        os.envrion = self.old_environ
        os.path = self.old_path

    def test_dir_from_environ(self):
        dirs = confit.config_dirs()
        self.assertEqual(dirs, [
            'c:\\home\\AppData\\Roaming',
            'c:\\home\\winconfig',
        ])

    def test_fallback_dir(self):
        del os.environ['APPDATA']
        dirs = confit.config_dirs()
        self.assertEqual(dirs, ['c:\\home\\AppData\\Roaming'])

class ConfigFilenamesTest(unittest.TestCase):
    def setUp(self):
        self.old_system = _mock_system('Linux')
        self.old_environ = _mock_environ()
        self.old_path = _mock_path('posixpath')
        self.old_isfile = os.path.isfile
        os.path.isfile = lambda x: True
        self.old_load = confit.load_yaml
        confit.load_yaml = lambda x: {}
    def tearDown(self):
        platform.system = self.old_system
        os.envrion = self.old_environ
        os.path = self.old_path
        os.path.isfile = self.old_isfile
        confit.load_yaml = self.old_load

    def test_no_sources_when_files_missing(self):
        config = confit.Configuration('myapp', read=False)
        filenames = [s.filename for s in config.sources]
        self.assertEqual(filenames, [])

    def test_search_package(self):
        config = confit.Configuration('myapp', __name__, read=False)
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

class TempHomeMixin(object):
    """Test fixture that locates the home directory in a temporary
    directory.
    """
    def setUp(self):
        self.home = tempfile.mkdtemp()
        self.old_environ = _mock_environ(home=self.home)

    def tearDown(self):
        os.envrion = self.old_environ
        if os.path.exists(self.home):
            shutil.rmtree(self.home)

class EnvVarTest(unittest.TestCase, TempHomeMixin):
    def setUp(self):
        TempHomeMixin.setUp(self)
        self.old_system = _mock_system('Linux')
        self.old_path = _mock_path('posixpath')

        self.config = confit.Configuration('myapp', read=False)
        os.environ['MYAPPDIR'] = os.path.join(self.home, 'test')

    def tearDown(self):
        TempHomeMixin.tearDown(self)
        platform.system = self.old_system
        os.path = self.old_path

    def test_env_var_name(self):
        self.assertEqual(self.config._env_var, 'MYAPPDIR')

    def test_env_var_dir_has_first_priority(self):
        config_dir = self.config.config_dir()
        self.assertEqual(config_dir, os.path.join(self.home, 'test'))

    def test_env_var_missing(self):
        del os.environ['MYAPPDIR']
        config_dir = self.config.config_dir()
        self.assertNotEqual(config_dir, os.path.join(self.home, 'test'))

class PrimaryConfigDirTest(unittest.TestCase, TempHomeMixin):
    def setUp(self):
        TempHomeMixin.setUp(self)
        self.old_system = _mock_system('Linux')
        self.old_path = _mock_path('posixpath')

        self.config = confit.Configuration('test', read=False)

    def tearDown(self):
        TempHomeMixin.tearDown(self)
        platform.system = self.old_system
        os.path = self.old_path

    def test_create_dir_if_none_exists(self):
        path = os.path.join(self.home, 'xdgconfig', 'test')
        assert not os.path.exists(path)

        self.assertEqual(self.config.config_dir(), path)
        self.assertTrue(os.path.isdir(path))

    def test_return_existing_dir(self):
        path = os.path.join(self.home, 'xdgconfig', 'test')
        os.makedirs(path)
        _touch(os.path.join(path, confit.CONFIG_FILENAME))
        self.assertEqual(self.config.config_dir(), path)

    def test_do_not_create_dir_if_lower_priority_exists(self):
        path1 = os.path.join(self.home, 'xdgconfig', 'test')
        path2 = os.path.join(self.home, '.config', 'test')
        os.makedirs(path2)
        _touch(os.path.join(path2, confit.CONFIG_FILENAME))
        assert not os.path.exists(path1)
        assert os.path.exists(path2)

        self.assertEqual(self.config.config_dir(), path2)
        self.assertFalse(os.path.isdir(path1))
        self.assertTrue(os.path.isdir(path2))
