Overview
=========

This project contains tools to split brain atlas regions and refine annotations accordingly.

After installation, you can display the available command lines with the following ``bash`` command:
.. code-block:: bash

    atlas-splitter --help

Installation
============

.. code-block:: bash

    git clone git@bbpgitlab.epfl.ch:nse/atlas-splitter.git
    cd atlas-splitter
    pip install -e .


Instructions for developers
===========================

Run the following commands before submitting your code for review:

.. code-block:: bash

    cd atlas-splitter
    isort -l 100 --profile black atlas_splitter tests setup.py
    black -l 100 atlas_splitter tests setup.py

These formatting operations will help you pass the linting check `testenv:lint` defined in
`tox.ini`.
