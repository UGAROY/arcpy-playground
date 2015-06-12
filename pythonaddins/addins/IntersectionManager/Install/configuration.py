import logging

import arcpy

from src.tss import setup_logger

setup_logger("Test")

logger = logging.getLogger(__name__)

logger.info("ABC1234")