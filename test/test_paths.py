import unittest
import confit
import os
import platform

def _mock_system(plat):
    def system():
        return plat
    old = platform.system
    platform.system = system
    return old

def _mock_environ(home='/home'):
    old = os.environ
    os.environ = {
        'XDG_DATA_HOME': '~/xdgconfig',
        'APPDATA': '~\\winconfig',
        'HOME': home,
    }
    return old

def _mock_path(modname):
    old = os.path
    os.path = __import__(modname)
    return old

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
        self.assertEqual(dirs, ['/home/xdgconfig', '/home/.config'])

    def test_fallback_only(self):
        del os.environ['XDG_DATA_HOME']
        dirs = confit.config_dirs()
        self.assertEqual(dirs, ['/home/.config'])

    def test_xdg_matching_fallback_not_duplicated(self):
        os.environ['XDG_DATA_HOME'] = '~/.config'
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
        self.assertEqual(dirs, ['/home/Library/Application Support',
                                '/home/.config'])

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
        self.assertEqual(dirs, ['c:\\home\\winconfig'])

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
    def tearDown(self):
        platform.system = self.old_system
        os.envrion = self.old_environ
        os.path = self.old_path
        os.path.isfile = self.old_isfile
    
    def test_search_all_conf_dirs(self):
        fns = confit.config_filenames('myapp')
        self.assertEqual(fns, [
            '/home/xdgconfig/myapp/config.yaml',
            '/home/.config/myapp/config.yaml',
        ])
    
    def test_search_package(self):
        fns = confit.config_filenames('myapp', __name__)
        self.assertEqual(fns, [
            '/home/xdgconfig/myapp/config.yaml',
            '/home/.config/myapp/config.yaml',
            os.path.join(os.path.dirname(__file__), 'config_default.yaml'),
        ])
