"""Terra main application."""

import logging
import random

import terra.ui
from terra.sim import Simulation


def run() -> None:
    """Start the Terra application."""
    print('Starting Terra...')
    logging.basicConfig(filename='debug.log', filemode='w',
                        level=logging.DEBUG)
    random.seed(0)
    s = Simulation()
    terra.ui.start(s)
    print('Terra exited')
