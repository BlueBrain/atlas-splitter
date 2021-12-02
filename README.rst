Overview
=========

This project contains to split brain atlas regions and refine annotations accordingly.

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
