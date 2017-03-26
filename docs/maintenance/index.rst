.. role:: raw-html(raw)
   :format: html

Maintainer Notes
================

These notes are directed towards helping with the maintenance of the
Specter project.

Releasing a new version of Specter
----------------------------------

#. Start with a fresh local branch.

   .. code-block:: shell

        git checkout -b prep_for_release

#. Update and commit release notes in ``docs/release_notes/index.rst``.
#. Execute bumpversion.

   .. code-block:: shell

        # Available parts: major, minor, patch
        bumpversion <part>

#. Push up branch and tag

   .. code-block:: shell

        git push origin prep_for_release --tags

#. Create PR.
#. Wait for CI to pass and PR to merge.
#. Remove old packages

   .. code-block:: shell

        rm -r dist

#. Build sdist and wheel

   .. code-block:: shell

        python setup.py sdist
        python setup.py bdist_wheel
#. Upload to PyPI

   .. code-block:: shell

        twine upload dist/*
