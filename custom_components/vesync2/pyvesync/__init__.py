"""VeSync API Library."""

# pylint: skip-file
# flake8: noqa
import logging

from .vesync import VeSync
from .vesyncbulb import *
from .vesyncoutlet import *
from .vesyncswitch import *

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)5s - %(message)s"
)
