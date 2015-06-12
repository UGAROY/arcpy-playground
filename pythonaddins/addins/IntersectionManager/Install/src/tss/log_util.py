import logging
import logging.config
import logging.handlers
import os
from ags.AgsLogHandler import AgsLogHandler
from datetime_util import get_datetime_stamp
from path_util import get_user_directory
from helper import first_or_default


def setup_logger(folder_name):
    """
    Setup the logger.
    The function will try to find the best location to put the folder/log
    1) Home Directory 2) Current Directory
    @param folder_name: The folder name that will hold all the log files
    @return:
    """
    time_stamp = get_datetime_stamp()

    path_candiates = [os.path.join(get_user_directory(), ".%s" % folder_name),
                     os.path.join(os.path.dirname(__file__), ".%s" % folder_name)]
    output_path = first_or_default(path_candiates, create_output_folder, "")
    log_path = os.path.join(output_path, ".%s.log" % time_stamp)

    logging.handlers.AgsHandler = AgsLogHandler

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,  # this fixes the problem

        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
        },
        "handlers": {
            "default": {
                "level":"INFO",
                "class":"logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            },
            "info_file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "filename": log_path,
                "encoding": "utf8",
                "maxBytes": 1024,
                "backupCount": 3
            },
            "ags": {
                "level":"INFO",
                "class":"logging.handlers.AgsHandler",
                "formatter": "standard"
            },
        },
        "loggers": {
            "": {
                "handlers": ["default", "info_file", "ags"],
                "level": "INFO"
            }
        }
    })

    #
    # logging.basicConfig(level=logging.DEBUG,
    #                     format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    #                     datefmt="%m-%d %H:%M",
    #                     filename="log-%s.log" % time_stamp,
    #                     filemode="w")


def create_output_folder(path):
    if os.path.exists(path):
        return path
    try:
        os.mkdir(path)
    except Exception:
        return
