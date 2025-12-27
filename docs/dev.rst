Development Guide
=================

This document provides guidelines for developers working on the ``confuse``
library.

Version Bumps
-------------

This section outlines how to create a new version of the ``confuse`` library and
publish it on PyPi. The versioning follows semantic versioning principles, where
the version number is structured as ``MAJOR.MINOR.PATCH``.

To create a new version, follow these steps:

1. Navigate to `Make release
   <https://github.com/beetbox/confuse/actions/workflows/make_release.yaml>`_
   action in the GitHub repository.
2. Press **Run workflow**, enter the new version number in the format
   ``MAJOR.MINOR.PATCH``, e.g., ``1.8.0`` and submit it.
3. Refresh the page to see the status of the workflow.
4. Once it succeeds, create a GitHub release with notes from the
   ``docs/changelog.rst`` file.

Note: This workflow does not update the changelog version numbers; this must be
done manually before running the release workflow.
