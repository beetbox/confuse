"""Tests for the release utils."""

import os
import shutil
import sys
from datetime import datetime, timezone

import pytest
from packaging.version import Version

release = pytest.importorskip("extra.release")

RUNNING_IN_CI = os.environ.get("GITHUB_ACTIONS") == "true"

pytestmark = pytest.mark.skipif(
    not ((RUNNING_IN_CI and sys.platform != "win32") or bool(shutil.which("pandoc"))),
    reason="pandoc isn't available",
)


@pytest.fixture
def rst_changelog():
    return """
Unreleased
----------

New features
~~~~~~~~~~~~

- Some substitute
  multi-line change.
  :bug:`5467`
- See :class:`~nonexisting_ref` for non-existing reference.
- See :ref:`Nice title <nonexisting_ref>` for non-existing named reference.

You can do something with this command:

::

    $ do-something

Bug fixes
~~~~~~~~~

- Some fix that refers to an issue.
  :bug:`5467`
- Some fix that mentions user :user:`username`.
- Some fix thanks to
  :user:`username`. :bug:`5467`
- Some fix with its own bullet points using incorrect indentation:

  - First nested bullet point
    with some text that wraps to the next line
  - Second nested bullet point

- Another fix with an enumerated list

  1. First
     and some details
  2. Second
     and some details

Long parapgraph naaaaaaaaaaaaaaaaaaaaaaaammmmmmmmmmmmmmmmeeeeeeeeeeeeeee ending
with a colon:

.. For plugin developers
.. ~~~~~~~~~~~~~~~~~~~~~

Other changes
~~~~~~~~~~~~~

- Changed ``bitesize`` label to ``good first issue``. Our `contribute`_ page is now
  automatically populated with these issues. :bug:`4855`

.. _contribute: https://github.com/beetbox/beets/contribute

2.1.0 (November 22, 2024)
-------------------------

Bug fixes
~~~~~~~~~

- Fixed something."""


@pytest.fixture
def md_changelog():
    return r"""# Unreleased

## New features

- See `Nice title` for non-existing named reference.
- See `nonexisting_ref` for non-existing reference.
- Some substitute multi-line change. :bug: (#5467)

You can do something with this command:

    $ do-something

## Bug fixes

- Another fix with an enumerated list
  1.  First and some details
  2.  Second and some details
- Some fix thanks to @username. :bug: (#5467)
- Some fix that mentions user @username.
- Some fix that refers to an issue. :bug: (#5467)
- Some fix with its own bullet points using incorrect indentation:
  - First nested bullet point with some text that wraps to the next line
  - Second nested bullet point

Long parapgraph naaaaaaaaaaaaaaaaaaaaaaaammmmmmmmmmmmmmmmeeeeeeeeeeeeeee ending with a colon:

## Other changes

- Changed `bitesize` label to `good first issue`. Our [contribute](https://github.com/beetbox/beets/contribute) page is now automatically populated with these issues. :bug: (#4855)

# 2.1.0 (November 22, 2024)

## Bug fixes

- Fixed something."""  # noqa: E501


def test_convert_rst_to_md(rst_changelog, md_changelog):
    actual = release.changelog_as_markdown(rst_changelog)

    assert actual == md_changelog


def test_bump_version_applies_sequential_changelog_updates(tmp_path, monkeypatch):
    changelog = tmp_path / "changelog.rst"
    changelog.write_text(
        """
Unreleased
----------

..
    New features
    ~~~~~~~~~~~~

Bug fixes
~~~~~~~~~

- Fixed a bug.

..
    Other changes
    ~~~~~~~~~~~~~

2.2.1 (January 01, 2025)
------------------------
"""
    )
    monkeypatch.setattr(
        release,
        "FILENAME_AND_UPDATE_TEXT",
        [
            (changelog, release.remove_unused_headers),
            (changelog, release.update_changelog),
        ],
    )

    release.bump_version(Version("2.3.0"))

    today = datetime.now(timezone.utc).date()
    assert (
        changelog.read_text()
        == f"""
Unreleased
----------

..
    New features
    ~~~~~~~~~~~~

..
    Bug fixes
    ~~~~~~~~~

..
    For plugin developers
    ~~~~~~~~~~~~~~~~~~~~~

..
    Other changes
    ~~~~~~~~~~~~~

2.3.0 ({today:%B %d, %Y})
--------------------------

Bug fixes
~~~~~~~~~

- Fixed a bug.

2.2.1 (January 01, 2025)
------------------------
"""
    )
