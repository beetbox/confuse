Development Guide
=================

This document provides guidelines for developers working on the `confuse` library.

Version Bumps
-------------

This section outlines how to create a new version of the `confuse` library and publish it on PyPi. The versioning follows semantic versioning principles, where the version number is structured as `MAJOR.MINOR.PATCH`.

To create a new version, follow these steps:

- make sure the changes are documented in the `changelog.rst` file
- update the version number in `confuse/__init__.py`
- create a new release in GitHub with the tag `vMAJOR.MINOR.PATCH`

This should trigger the GitHub Actions workflow that builds the package and publishes it to PyPi.

Check if the github actions succeeded by looking at the Actions tab in the repository. If it failed, you can check the logs to see what went wrong and try to fix it.
