__author__ = 'yluo'

import os
import wx
import pythonaddins
#import arcpy


class FileInputGroup(wx.Panel):

    def __init__(self, parent, ID=-1):
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, 'Test')
        self.inputText = wx.TextCtrl(self, wx.ID_ANY)
        png = wx.Image(os.path.join(os.path.dirname(__file__), 'DataFrame16.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        inputButton = wx.BitmapButton(self, wx.ID_ANY, png)
        inputGroupSizer.Add(inputLabel, pos=(0,0), span=(1, 2), flag=wx.EXPAND)
        inputGroupSizer.Add(self.inputText, pos=(1,0), flag=wx.EXPAND)
        inputGroupSizer.Add(inputButton, pos=(1,1))
        inputGroupSizer.AddGrowableCol(0)

        self.Bind(wx.EVT_BUTTON, self.openFileDialog, inputButton)

        self.SetSizer(inputGroupSizer)


    def openFileDialog(self, event):
        path = pythonaddins.OpenDialog('Select Layers', True, r'C:\GISData', 'Add')[0]
        self.inputText.SetValue(path)

    def value(self):
        return self.inputText.GetValue()


class ConfigDialog(wx.Frame):

    def __init__(self):
        """Initialize the Frame and add wx widgets."""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Configuration", style=wx.DEFAULT_FRAME_STYLE )
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), 'wxpdemo.ico'), wx.BITMAP_TYPE_ICO))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.panel = wx.Panel(self, wx.ID_ANY)

        okBtn = wx.Button(self.panel, wx.ID_OK, 'OK')
        closeBtn = wx.Button(self.panel, wx.ID_CANCEL, 'Close')
        self.Bind(wx.EVT_BUTTON, self.OnOK, okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)

        topSizer = wx.BoxSizer(wx.VERTICAL)
        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputOneSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        inputLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Test')
        inputText = wx.TextCtrl(self.panel, wx.ID_ANY)
        png = wx.Image(os.path.join(os.path.dirname(__file__), 'open.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        inputButton = wx.BitmapButton(self.panel, wx.ID_ANY, png)
        inputGroupSizer.Add(inputLabel, pos=(0,0), span=(1, 2), flag=wx.EXPAND)
        inputGroupSizer.Add(inputText, pos=(1,0), flag=wx.EXPAND)
        inputGroupSizer.Add(inputButton, pos=(1,1))
        inputGroupSizer.AddGrowableCol(0)


        topSizer.Add(inputGroupSizer, 0, wx.ALL | wx.EXPAND, 10)

        btnSizer.Add(okBtn, 0, wx.ALL , 5)
        btnSizer.Add(closeBtn, 0, wx.ALL, 5)

        test = FileInputGroup(self.panel)
        topSizer.Add(test, 0, wx.ALL | wx.EXPAND, 10)

        topSizer.Add(inputOneSizer, 0, wx.ALL | wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 10)
        topSizer.Add(btnSizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)

        ## Uncomment line below when testing as a standalone application.
        self.Show(True)

    # End __init__ built-in

    def OnClose(self, event):
        """Close the frame. Do not use destroy."""
        self.Show(False)
    # End OnClose event method

    def OnOK(self, event):
        """Renames the active data frame of map document."""
        # sTitle = str(self.dfName.GetValue())
        # mxd = arcpy.mapping.MapDocument("CURRENT")
        # df = mxd.activeDataFrame
        # df.name = sTitle
        # arcpy.RefreshTOC()
        pass
    # End OnOK event method


class RenameDialog(wx.Frame):

    def __init__(self):
        """Initialize the Frame and add wx widgets."""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Set Data Frame Name", style=wx.DEFAULT_FRAME_STYLE)
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), 'wxpdemo.ico'), wx.BITMAP_TYPE_ICO))
        self.MinSize = 300, 125
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.panel = wx.Panel(self, wx.ID_ANY)

        png = wx.Image(os.path.join(os.path.dirname(__file__), 'DataFrame16.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        inputIcon = wx.StaticBitmap(self.panel, wx.ID_ANY, png)
        labelOne = wx.StaticText(self.panel, wx.ID_ANY, 'New Name:')
        self.dfName = wx.TextCtrl(self.panel, wx.ID_ANY)

        okBtn = wx.Button(self.panel, wx.ID_OK, 'OK')
        closeBtn = wx.Button(self.panel, wx.ID_CANCEL, 'Close')
        self.Bind(wx.EVT_BUTTON, self.OnOK, okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)

        topSizer = wx.BoxSizer(wx.VERTICAL)
        inputOneSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        inputOneSizer.Add(inputIcon, 0, wx.ALL, 5)
        inputOneSizer.Add(labelOne, 0, wx.ALL, 5)
        inputOneSizer.Add(self.dfName, 1, wx.ALL | wx.EXPAND, 5)

        btnSizer.Add(okBtn, 0, wx.ALL, 5)
        btnSizer.Add(closeBtn, 0, wx.ALL, 5)

        test = FileInputGroup(self.panel)
        topSizer.Add(test, 0, wx.ALL | wx.EXPAND, 10)

        topSizer.Add(inputOneSizer, 0, wx.ALL | wx.EXPAND, 5)
        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL | wx.CENTER, 5)

        self.panel.SetSizer(topSizer)
        topSizer.Fit(self)

        ## Uncomment line below when testing as a standalone application.
        #self.Show(True)

    # End __init__ built-in

    def OnClose(self, event):
        """Close the frame. Do not use destroy."""
        self.Show(False)
    # End OnClose event method

    def OnOK(self, event):
        """Renames the active data frame of map document."""
        # sTitle = str(self.dfName.GetValue())
        # mxd = arcpy.mapping.MapDocument("CURRENT")
        # df = mxd.activeDataFrame
        # df.name = sTitle
        # arcpy.RefreshTOC()
    # End OnOK event method


## Uncomment code below to test as standalone application.
# app = wx.App(False)
# frame = ConfigDialog()
# app.MainLoop()