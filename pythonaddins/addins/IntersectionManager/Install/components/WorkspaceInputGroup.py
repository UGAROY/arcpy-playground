import wx
import os
import pythonaddins

class WorkspaceInputGroup(wx.Panel):
    """An InputGroup to specify a gdb workspace, etc."""

    def __init__(self, parent, ID=-1, inputLabel="", topFrame=None, key=""):
        # A top frame is added here to toggle the stay_on_top property
        # Current this is the only workaround I can think of to make the Frame
        # Stay on top of the ArcMap but do not block the File Dialog
        self.topFrame = topFrame
        self.key = key
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.TextCtrl(self, wx.ID_ANY)
        png = wx.Image(os.path.join(os.path.dirname(__file__), "img", "OpenFolder.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        inputButton = wx.BitmapButton(self, wx.ID_ANY, png)
        inputGroupSizer.Add(inputLabel, pos=(0, 0))
        inputGroupSizer.Add(self.inputText, pos=(1, 0), flag=wx.EXPAND)
        inputGroupSizer.Add(inputButton, pos=(1, 1))
        inputGroupSizer.AddGrowableCol(0)

        self.Bind(wx.EVT_BUTTON, self.openWorkspaceDialog, inputButton)

        self.SetSizer(inputGroupSizer)


    def openWorkspaceDialog(self, event):
        self.topFrame.ToggleWindowStyle(wx.STAY_ON_TOP)
        path = pythonaddins.OpenDialog('Select Workspace', False, r'', 'Add')[0]
        self.inputText.SetValue(path)
        self.topFrame.ToggleWindowStyle(wx.STAY_ON_TOP)

    @property
    def value(self):
        return self.inputText.GetValue()

    @value.setter
    def value(self, value):
        self.inputText.SetValue(str(value))