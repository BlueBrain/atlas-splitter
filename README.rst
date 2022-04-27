.. image:: atlas-splitter.jpg

Overview
=========

This project contains tools to split brain atlas regions and refine annotations accordingly.

After installation, you can display the available command lines with the following ``bash`` command:

.. code-block:: bash

    atlas-splitter --help

Installation
============

.. code-block:: bash

    git clone https://github.com/BlueBrain/atlas-splitter
    cd atlas-splitter
    pip install -e .


Instructions for developers
===========================

Run the following commands before submitting your code for review:

.. code-block:: bash

    cd atlas-splitter
    isort -l 100 --profile black atlas_splitter tests setup.py
    black -l 100 atlas_splitter tests setup.py

These formatting operations will help you pass the linting check ``testenv:lint`` defined in ``tox.ini``.

Acknowledgements
================

The development of this software was supported by funding to the Blue Brain Project, a research center of the École polytechnique fédérale de Lausanne (EPFL), from the Swiss government’s ETH Board of the Swiss Federal Institutes of Technology.

For license and authors, see LICENSE.txt and AUTHORS.txt respectively.

Copyright © 2022-2022 Blue Brain Project/EPFL
