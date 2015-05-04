import os
import sys
sys.path.append(os.path.dirname(__file__))
import arcpy
import pythonaddins


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
        except Exception:
            pythonaddins.MessageBox("Error starting the Intersection Manager Extension", "Extension Error", 0)

    @property
    def enabled(self):
        if self._enabled == False:
            configButton.enabled = False
        else:
            configButton.enabled = True
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        """Set the enabled property of this extension when the extension is turned on or off in the Extension Dlalog of ArcMap."""
        self._enabled = value

class Configuration(object):
    """Implementation for IntersectionManager_addin.button (Button)"""

    _dlg = None

    @property
    def dlg(self):
        """Return the configuration dialog."""
        if self._dlg is None:
            from IMDialogs import ConfigurationDialog
            self._dlg = ConfigurationDialog()
        return self._dlg

    def __init__(self):
        """Initialize button and set it to enabled and unchecked by default."""
        self.enabled = True
        self.checked = False

    def onClick(self):
        """Show the rename configuration dialog."""
        try:
            self.dlg.Show(True)
        except Exception as e:
            pythonaddins.MessageBox("Can't Show Parameter Configuration Dialog. %s" % e, "Error", "0")