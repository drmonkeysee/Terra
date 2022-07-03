"""Terra main application."""

import logging
import random

import terra.ui
from terra.sim import Sim


def run() -> None:
    print('Starting Terra...')
    logging.basicConfig(filename='debug.log', filemode='w',
                        level=logging.DEBUG)
    random.seed(0)
    s = Sim()
    terra.ui.start(s)
    print('Terra exited')
