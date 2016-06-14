from __future__ import division, absolute_import, print_function

import confuse
import tempfile
import shutil
import os


def _root(*sources):
    return confuse.RootView([confuse.ConfigSource.of(s) for s in sources])


class TempDir(object):
    """Context manager that creates and destroys a temporary directory.
    """
    def __init__(self):
        self.path = tempfile.mkdtemp()

    def __enter__(self):
        return self

    def __exit__(self, *errstuff):
        shutil.rmtree(self.path)

    def sub(self, name, contents=None):
        """Get a path to a file named `name` inside this temporary
        directory. If `contents` is provided, then the bytestring is
        written to the file.
        """
        path = os.path.join(self.path, name)
        if contents:
            with open(path, 'wb') as f:
                f.write(contents)
        return path
