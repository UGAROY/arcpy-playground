import os

import wx
import wx.lib.scrolledpanel as scrolled

from TableGroup import TableGroup


class TableDialog(wx.Frame):
    def __init__(self, inputLabel, data, rowNum, colNum, colName):
        """Initialize the Frame and add wx widgets."""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Update Intersections Info",
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
        self.MinSize = 400, 300
        self.MaxSize = 600, 600
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Table Section
        contentPanel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        contentSizer = wx.BoxSizer(wx.VERTICAL)
        self.table = TableGroup(contentPanel, data, rowNum, colNum, colName)
        contentSizer.Add(self.table, 1, wx.EXPAND)
        contentPanel.SetSizer(contentSizer)
        contentPanel.SetupScrolling()
        contentPanel.Fit()
        # End of Table Section

        # Button Toolbar
        btnPanel = wx.Panel(self, -1)
        okBtn = wx.Button(btnPanel, wx.ID_OK, 'Save Edits')
        clearBtn = wx.Button(btnPanel, wx.ID_ANY, 'Clear Edits')
        closeBtn = wx.Button(btnPanel, wx.ID_CANCEL, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.OnOK, okBtn)
        self.Bind(wx.EVT_BUTTON, self.ClearEdits, clearBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(okBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        btnSizer.Add(clearBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        btnSizer.Add(closeBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        btnPanel.SetSizer(btnSizer)
        btnPanel.Fit()
        # End of Button Toolbar

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(contentPanel, 1, flag=wx.EXPAND)
        mainSizer.Add(btnPanel, flag=wx.EXPAND)
        self.SetSizer(mainSizer)
        self.Fit()
        self.CenterOnScreen()

        # # Uncomment line below when testing as a standalone application.
        self.Show(True)


    # End __init__ built-in

    def ClearEdits(self, event):
        self.table.ClearEdits("New Intersection ID")

    def OnClose(self, event):
        """Close the frame. Do not use destroy."""
        self.Show(False)

    # End OnClose event method

    def OnOK(self, event):
        """ """

        self.Show(False)