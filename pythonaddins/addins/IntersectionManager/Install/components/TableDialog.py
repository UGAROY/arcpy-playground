import os

import wx
import wx.lib.scrolledpanel as scrolled

from TableGroup import TableGroup


class TableDialog(wx.Dialog):
    def __init__(self, inputLabel, data, rowLabels=None, colLabels=None):
        """Initialize the Frame and add wx widgets."""
        wx.Dialog.__init__(self, None, wx.ID_ANY, title="Update Intersections Info",
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
        self.MinSize = 450, 300
        self.MaxSize = 600, 600
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Table Section
        self.table = TableGroup(self, data=data, colLabels=colLabels)

        # Button Toolbar
        btnPanel = wx.Panel(self, -1)
        saveBtn = wx.Button(btnPanel,wx.ID_OK, 'Save Edits')
        clearBtn = wx.Button(btnPanel,wx.ID_ANY, 'Clear Edits')
        closeBtn = wx.Button(btnPanel,wx.ID_CANCEL, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.SaveEdits, saveBtn)
        self.Bind(wx.EVT_BUTTON, self.ClearEdits, clearBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(saveBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        btnSizer.Add(clearBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        btnSizer.Add(closeBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        btnPanel.SetSizer(btnSizer)
        btnPanel.Fit()
        # End of Button Toolbar

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.table, 1, flag=wx.EXPAND)
        mainSizer.Add(btnPanel, flag=wx.EXPAND)
        self.SetSizer(mainSizer)
        self.Fit()
        self.CenterOnScreen()

        # initiate output data as None
        self.updated_data = None

        # # Uncomment line below when testing as a standalone application.
        # self.Show(True)

    # End __init__ built-in

    def ClearEdits(self, event):
        self.table.ClearEdits("Renamed Intersection ID")

    def SaveEdits(self, event):
        self.Show(False)
        self.updated_data = self.GetUpdatedData()
        self.SetReturnCode(wx.ID_OK)

    def ClearTable(self):
        self.table.ClearTable()

    def PopulateTable(self,data):
        self.table.PopulateTable(data)

    def GetUpdatedData(self):
        updated_data = self.table.GetUpdatedData()
        return updated_data

        # if len(updated_data):
        #     return updated_data
        # else:
        #     return None

    def OnClose(self, event):
        """Close the frame. Do not use destroy."""
        self.Show(False)
        self.SetReturnCode(wx.ID_CANCEL)
    # End OnClose event method



# Uncomment following code when testing in stand alone mode
# data = [["1","11",""],["1","11",""],["1","11",""],["1","11",""],["1","11",""],["1","11",""],["1","11",""],["1","11",""]\
#     ,["1","11",""],["1","11",""],["1","11",""],["1","11",""],["1","11",""],["1","11",""],["1","11",""],["1","11",""],\
#     ["1","11",""],["1","11",""],["1","11",""],["1","11",""]]
#
# data2 = [["1","11",""],["2","22",""],["3","33",""],["4","44",""],["5","55",""],["6","66",""],["7","77",""]]
#
# col_names = ["Object ID","Current Intersection ID","New Intersection ID"]
#
# app = wx.App(False)
# frame = TableDialog("Test",data=data,colLabels=col_names)
# app.MainLoop()