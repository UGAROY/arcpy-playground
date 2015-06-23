import logging
import arcpy  # our internal module for sending SMS


class AgsLogHandler(logging.Handler):  # Inherit from logging.Handler

    def __init__(self):
        # run the regular Handler __init__
        logging.Handler.__init__(self)

    def emit(self, record):
        # record.message is the log message
        if record.levelname == "INFO":
            arcpy.AddMessage(record.message)
        elif record.levelname == "ERROR":
            arcpy.AddError(record.message)
        elif record.levelname == "WARNING":
            arcpy.AddWarning(record.message)
        else:
            arcpy.AddMessage(record.message)