import os
import arcpy

from ..tss import get_parent_directory

def get_default_parameters():
    try:
        import ConfigParser

        Config = ConfigParser.ConfigParser()
        init_cfg = os.path.join(get_parent_directory(__file__, 2), "config/params.ini")
        updated_cfg = os.path.join(get_parent_directory(__file__, 2), "config/params_updated.ini")

        if os.path.exists(updated_cfg):
            Config.read(updated_cfg)
        else:
            Config.read(init_cfg)

        return Config
    except ImportError:
        pass

def log_message(message):
    arcpy.AddMessage(message)