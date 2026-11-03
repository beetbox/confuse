"""Test config discovery in subprocesses with temporary homes and synthetic envs."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.name == "nt", reason="Subprocess fixtures use POSIX temporary paths"
)

SCRIPT = """
import json
import ntpath
import os
import sys
from unittest.mock import patch

import confuse

system, action = sys.argv[1:]
real_isfile = os.path.isfile
root = os.getcwd() + os.sep

def local_isfile(path):
    return str(path).startswith(root) and real_isfile(path)

with patch('platform.system', return_value=system):
    if system == 'Windows':
        os.path = ntpath
    with patch('os.path.isfile', side_effect=local_isfile):
        if action == 'dirs':
            result = confuse.config_dirs()
        else:
            config = confuse.Configuration('xdg_priority_test', read=False)
            if action == 'read':
                config.read(user=True, defaults=False)
                result = config['origin'].get()
            else:
                result = config.config_dir()
        print(json.dumps(result))
"""


@pytest.fixture
def run_config(tmp_path):
    def run(system="Linux", *, env=None, action="dirs"):
        environment = {
            "HOME": str(tmp_path / "home"),
            "USERPROFILE": str(tmp_path / "home"),
            "PYTHONPATH": str(Path(__file__).resolve().parents[1]),
            "PYTHONDONTWRITEBYTECODE": "1",
            "XDG_CONFIG_DIRS": str(tmp_path / "system"),
        }
        environment.update(env or {})
        process = subprocess.run(
            [sys.executable, "-c", SCRIPT, system, action],
            cwd=tmp_path,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(process.stdout)

    return run


def write_config(directory, value):
    path = directory / "xdg_priority_test"
    path.mkdir(parents=True)
    (path / "config.yaml").write_text(f"origin: {value}\n")
    return path


@pytest.mark.parametrize("system", ["Linux", "FreeBSD", "Darwin"])
def test_explicit_xdg_home_first_preserves_other_locations(
    tmp_path, run_config, system
):
    xdg = tmp_path / "xdg"
    first_system = tmp_path / "system-one"
    second_system = tmp_path / "system-two"
    expected = [str(xdg), str(tmp_path / "home" / ".config")]
    if system == "Darwin":
        expected.append(str(tmp_path / "home" / "Library" / "Application Support"))
    expected.extend([str(first_system), str(second_system), "/etc"])
    assert (
        run_config(
            system,
            env={
                "XDG_CONFIG_HOME": str(xdg),
                "XDG_CONFIG_DIRS": f"{first_system}:{second_system}",
            },
        )
        == expected
    )


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
@pytest.mark.parametrize("env", [{}, {"XDG_CONFIG_HOME": ""}])
def test_unset_or_empty_keeps_legacy_first(tmp_path, run_config, system, env):
    paths = run_config(system, env=env)
    expected = [str(tmp_path / "home" / ".config")]
    if system == "Darwin":
        expected.append(str(tmp_path / "home" / "Library" / "Application Support"))
    assert paths[: len(expected)] == expected
    assert paths[-2:] == [str(tmp_path / "system"), "/etc"]


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
@pytest.mark.parametrize("xdg", ["~/.config", "~/xdg/../.config"])
def test_expanded_duplicate_paths_still_deduplicated(tmp_path, run_config, system, xdg):
    paths = run_config(system, env={"XDG_CONFIG_HOME": xdg})
    assert paths[0] == str(tmp_path / "home" / ".config")
    assert len(paths) == len(set(paths))


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_config_from_xdg_wins_when_legacy_also_exists(tmp_path, run_config, system):
    write_config(tmp_path / "home" / ".config", "legacy")
    write_config(tmp_path / "home" / "Library" / "Application Support", "mac")
    write_config(tmp_path / "xdg", "xdg")
    assert (
        run_config(
            system, env={"XDG_CONFIG_HOME": str(tmp_path / "xdg")}, action="read"
        )
        == "xdg"
    )


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_create_new_config_directory_under_xdg(tmp_path, run_config, system):
    xdg = tmp_path / "xdg"
    expected = xdg / "xdg_priority_test"
    assert run_config(
        system, env={"XDG_CONFIG_HOME": str(xdg)}, action="directory"
    ) == str(expected)
    assert expected.is_dir()
    assert not (tmp_path / "home" / ".config").exists()


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
@pytest.mark.parametrize("env", [{}, {"XDG_CONFIG_HOME": ""}])
def test_unset_or_empty_creation_keeps_legacy_fallback(
    tmp_path, run_config, system, env
):
    expected = tmp_path / "home" / ".config" / "xdg_priority_test"
    assert run_config(system, env=env, action="directory") == str(expected)
    assert expected.is_dir()


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_existing_legacy_config_remains_available(tmp_path, run_config, system):
    write_config(tmp_path / "home" / ".config", "legacy")
    assert (
        run_config(
            system, env={"XDG_CONFIG_HOME": str(tmp_path / "xdg")}, action="read"
        )
        == "legacy"
    )
    assert not (tmp_path / "xdg").exists()


def test_existing_macos_location_remains_available(tmp_path, run_config):
    write_config(tmp_path / "home" / "Library" / "Application Support", "mac")
    assert (
        run_config(
            "Darwin", env={"XDG_CONFIG_HOME": str(tmp_path / "xdg")}, action="read"
        )
        == "mac"
    )


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_existing_system_config_remains_available(tmp_path, run_config, system):
    write_config(tmp_path / "system", "system")
    assert (
        run_config(
            system, env={"XDG_CONFIG_HOME": str(tmp_path / "xdg")}, action="read"
        )
        == "system"
    )
    assert not (tmp_path / "xdg").exists()


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_application_override_still_has_priority(tmp_path, run_config, system):
    expected = tmp_path / "override"
    assert run_config(
        system,
        env={
            "XDG_CONFIG_HOME": str(tmp_path / "xdg"),
            "XDG_PRIORITY_TESTDIR": str(expected),
        },
        action="directory",
    ) == str(expected)
    assert expected.is_dir()
    assert not (tmp_path / "xdg").exists()


@pytest.mark.parametrize("xdg", ["", "C:\\xdg"])
def test_windows_unchanged(run_config, xdg):
    assert run_config(
        "Windows",
        env={
            "HOME": "C:\\Users\\test",
            "USERPROFILE": "C:\\Users\\test",
            "APPDATA": "C:\\custom",
            "XDG_CONFIG_HOME": xdg,
        },
    ) == ["C:\\Users\\test\\AppData\\Roaming", "C:\\custom"]
