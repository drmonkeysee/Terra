"""Terra main application."""

import logging
import random

import terra.ui


def run() -> None:
    """Start the Terra application."""
    print('Starting Terra...')
    logging.basicConfig(filename='debug.log', filemode='w',
                        level=logging.DEBUG)
    random.seed(0)
    terra.ui.start()
    print('Terra exited')
