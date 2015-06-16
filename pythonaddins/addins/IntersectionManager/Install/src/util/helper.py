import os
import sys

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

def set_parameters(SECTION, key_value_dict):
    try:
        import ConfigParser

        Config = ConfigParser.ConfigParser()
        init_cfg = os.path.join(get_parent_directory(__file__, 2), "config/params.ini")
        updated_cfg = os.path.join(get_parent_directory(__file__, 2), "config/params_updated.ini")
        if os.path.exists(updated_cfg):
            Config.read(updated_cfg)
        else:
            Config.read(init_cfg)

        for key, value in key_value_dict.items():
            Config.set(SECTION, key, value)
        with open(updated_cfg, "wb") as cfg:
            Config.write(cfg)

        return Config
    except ImportError:
        pass

# enable local imports
local_path = os.path.dirname(__file__)
sys.path.insert(0, local_path)

try:
    import arcpy
    import pythonaddins
except:
    """
    The `import config` above thows a warning if ArcPy is unavailable,
    just swallow it here and let this script import, since most of
    these utils don't depend on ArcPy.
    """
    pass

def toolDialog(toolbox, tool):
    """Error-handling wrapper around pythonaddins.GPToolDialog."""
    result = None
    try:
        result = pythonaddins.GPToolDialog(toolbox, tool)
        # FIXME: this is a hack to prevent:
        # TypeError: GPToolDialog() takes at most 1 argument (2 given)
        # print ''
    except TypeError:
        pass
    # don't return anything. this prevents:
    #   TypeError: GPToolDialog() takes at most 1 argument (2 given)
    return result