"""The atlas-splitter command line launcher"""

import logging

import click

from atlas_splitter.app import layer_splitter
from atlas_splitter.version import VERSION

L = logging.getLogger(__name__)


def cli():
    """The main CLI entry point"""
    logging.basicConfig(level=logging.INFO)
    app = layer_splitter.app
    app = click.version_option(VERSION)(app)
    app()
