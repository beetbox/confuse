import pytest

import confuse
from example import template

from . import _root


@pytest.mark.parametrize("value", [True, False, "ask", "skip"])
def test_import_write_accepts_supported_values(value):
    config = _root({"import_write": value})
    assert config.get({"import_write": template["import_write"]}).import_write == value


@pytest.mark.parametrize("value", ["unexpected", "", "ASK", 1, None])
def test_import_write_rejects_unsupported_values(value):
    config = _root({"import_write": value})
    with pytest.raises(confuse.ConfigValueError):
        config.get({"import_write": template["import_write"]})
