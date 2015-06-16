import os
import sys

sys.path.append(os.path.dirname(__file__))
import pythonaddins

from PopulateIMTablesDialog import PopulateIMTablesDialog
from ConfigurationDialog import ConfigurationDialog
from SetViewDateDialog import SetViewDateDialog
from UpdateIMTablesDialog import UpdateIMTablesDialog

from src.util.helper import toolDialog

local_path = os.path.dirname(__file__)

im_toolbox =  os.path.join(local_path, "im.tbx")

class IntersectionManagerExt(object):
    """Implementation for IntersectionManager_addin.extension (Extension)"""
    def __init__(self):
        self._wxApp = None
        self._enabled = None

    def startup(self):
        """On startup of ArcGIS, create the wxPython Simple app and start the mainloop."""
        try:
            from wx import App
            self._wxApp = App(False)
            self._wxApp.MainLoop()

            # setup logger
            from src.tss import setup_logger
            setup_logger('IntersectionManager')

        except Exception:
            pythonaddins.MessageBox("Error starting the Intersection Manager Extension", "Extension Error", 0)

    @property
    def enabled(self):
        if self._enabled == False:
            configButton.enabled = False
            populateIMTablesButton.enabled = False
            updateIMTablesButton.enabled = False
            setViewDateButton.enabled = False
        else:
            configButton.enabled = True
            populateIMTablesButton.enabled = True
            updateIMTablesButton.enabled = True
            setViewDateButton.enabled = True
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        """Set the enabled property of this extension when the extension is turned on or off in the Extension Dlalog of ArcMap."""
        self._enabled = value

class Configuration(object):
    """Implementation for IntersectionManager_addin.button (Button)"""

    def __init__(self):
        """Initialize button and set it to enabled and unchecked by default."""
        self.enabled = True
        self.checked = False

    def onClick(self):
        """Show the rename configuration dialog."""
        try:
            toolDialog(im_toolbox,"configuration")
        except Exception as e:
            pythonaddins.MessageBox("Can't Show Parameter Configuration Dialog. %s" % e, "Error", "0")

class PopulateIMTables(object):
    """Implementation for IntersectionManager_addin.button (Button)"""

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        try:
            toolDialog(im_toolbox,"populate")
        except Exception as e:
            pythonaddins.MessageBox("Can't Show Populate Intersections Manager Table Dialog. %s" % e, "Error", "0")

class UpdateIMTables(object):
    """Implementation for IntersectionManager_addin.button (Button)"""

    _dlg = None

    @property
    def dlg(self):
        """Return the configuration dialog."""
        if self._dlg is None:
            self._dlg = UpdateIMTablesDialog()
        # self._dlg.LoadDefaultValues()
        return self._dlg

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        try:
            self.dlg.Show(True)
        except Exception as e:
            pythonaddins.MessageBox("Can't Show Update Intersections Manager Table Dialog. %s" % e, "Error", "0")

class SetViewDate(object):
    """Implementation for IntersectionManager_addin.button (Button)"""

    def __init__(self):
        self.enabled = True
        self.checked = False

    def onClick(self):
        try:
            toolDialog(im_toolbox,"setviewdate")
        except Exception as e:
            pythonaddins.MessageBox("Can't Show Set View Date Dialog. %s" % e, "Error", "0")