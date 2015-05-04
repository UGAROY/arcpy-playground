__author__ = 'yluo'

import os
import wx
import wx.wizard
import wx.lib.scrolledpanel as scrolled
import pythonaddins
#import arcpy


class FileInputGroup(wx.Panel):
    """An InputGroup to specify a gdb or path."""
    def __init__(self, parent, ID=-1, inputLabel="", topFrame=None):
        # A top frame is added here to toggle the stay_on_top property
        # Current this is the only workaround I can think of to make the Frame
        # Stay on top of the ArcMap but do not block the File Dialog
        self.topFrame = topFrame
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.TextCtrl(self, wx.ID_ANY)
        png = wx.Image(os.path.join(os.path.dirname(__file__), 'DataFrame16.png'), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        inputButton = wx.BitmapButton(self, wx.ID_ANY, png)
        inputGroupSizer.Add(inputLabel, pos=(0,0))
        inputGroupSizer.Add(self.inputText, pos=(1,0), flag=wx.EXPAND)
        inputGroupSizer.Add(inputButton, pos=(1,1))
        inputGroupSizer.AddGrowableCol(0)

        self.Bind(wx.EVT_BUTTON, self.openFileDialog, inputButton)

        self.SetSizer(inputGroupSizer)


    def openFileDialog(self, event):
        self.topFrame.ToggleWindowStyle(wx.STAY_ON_TOP)
        path = pythonaddins.OpenDialog('Select Layers', True, r'C:\GISData', 'Add')[0]
        self.inputText.SetValue(path)
        self.topFrame.ToggleWindowStyle(wx.STAY_ON_TOP)

    def value(self):
        return self.inputText.GetValue()


class TextInputGroup(wx.Panel):

    def __init__(self, parent, ID=-1, inputLabel=""):
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.TextCtrl(self, wx.ID_ANY)
        inputGroupSizer.Add(inputLabel, pos=(0,0))
        inputGroupSizer.Add(self.inputText, pos=(1,0), flag=wx.EXPAND)
        inputGroupSizer.AddGrowableCol(0)

        self.SetSizer(inputGroupSizer)

    def value(self):
        return self.inputText.GetValue()


class ComboBoxInputGroup(wx.Panel):

    def __init__(self, parent, ID=-1, inputLabel="", options=None):
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.ComboBox(self, wx.ID_ANY, choices=options)
        inputGroupSizer.Add(inputLabel, pos=(0,0))
        inputGroupSizer.Add(self.inputText, pos=(1,0), flag=wx.EXPAND)
        inputGroupSizer.AddGrowableCol(0)

        self.SetSizer(inputGroupSizer)

    def value(self):
        return self.inputText.GetStringSelection()


class ConfigurationDialog(wx.Frame):

    def __init__(self):
        """Initialize the Frame and add wx widgets."""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Paramters Configuration", style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), 'wxpdemo.ico'), wx.BITMAP_TYPE_ICO))
        self.MinSize = 450, 100
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.panel = scrolled.ScrolledPanel(self, wx.ID_ANY)

        okBtn = wx.Button(self.panel, wx.ID_OK, 'OK')
        closeBtn = wx.Button(self.panel, wx.ID_CANCEL, 'Close')
        self.Bind(wx.EVT_BUTTON, self.OnOK, okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)

        topSizer = wx.BoxSizer(wx.VERTICAL)

        network_input = FileInputGroup(self.panel, -1, "Network Feature Class", topFrame=self)
        network_rid_input = TextInputGroup(self.panel,  -1, "Network Route Name Field Name")
        network_rname_input = TextInputGroup(self.panel,  -1, "Network Route Id Field Name")
        network_fd_input = TextInputGroup(self.panel,  -1, "Network From Date Field Name")
        network_td_input = TextInputGroup(self.panel, -1, "Network To Date Field Name")

        intersection_fp_input = FileInputGroup(self.panel, -1, "Intersection Filter Point", topFrame=self)
        intersection_fp_fd_input = TextInputGroup(self.panel,  -1, "Intersection Filter Point From Date Field Name")
        intersection_fp_td_input = TextInputGroup(self.panel,  -1, "Intersection Filter Point To Date Field Name")

        functional_class_input = FileInputGroup(self.panel, -1, "Functional Class Feature Event", topFrame=self)
        functional_class_value_input = TextInputGroup(self.panel,  -1, "Functional Class Value Field")
        functional_class_fm_input = TextInputGroup(self.panel,  -1, "Functional Class From Measure Field")
        functional_class_tm_input = TextInputGroup(self.panel,  -1, "Functional Class To Measure Field")
        functional_class_fd_input = TextInputGroup(self.panel,  -1, "Functional Class From Date Field")
        functional_class_td_input = TextInputGroup(self.panel,  -1, "Functional Class To Date Field")

        aadt_input = FileInputGroup(self.panel, -1, "AADT Feature Event", topFrame=self)
        aadt_value_input = TextInputGroup(self.panel,  -1, "AADT Value Field")
        aadt_fm_input = TextInputGroup(self.panel,  -1, "AADT From Measure Field")
        aadt_tm_input = TextInputGroup(self.panel,  -1, "AADT To Measure Field")
        aadt_fd_input = TextInputGroup(self.panel,  -1, "AADT From Date Field")
        aadt_td_input = TextInputGroup(self.panel,  -1, "AADT To Date Field")

        search_radius_input = TextInputGroup(self.panel,  -1, "XY Tolerance (Feet)")
        leg_angle_cal_distance_input = TextInputGroup(self.panel,  -1, "Leg Angle Calculation Distance (Feet)")
        intersection_influecne_distance_input = TextInputGroup(self.panel,  -1, "Intersection Influence Distance (Feet)")
        azumith_direction_input = ComboBoxInputGroup(self.panel,  -1, "Azumith Direction Used As 0 Degree", options=["N", "S", "W", "E"])
        measure_scale = TextInputGroup(self.panel,  -1, "Measure Scale")

        inputs = [
            network_input, network_rid_input, network_rname_input, network_fd_input, network_td_input,
            intersection_fp_input, intersection_fp_fd_input, intersection_fp_td_input,
            functional_class_input, functional_class_value_input, functional_class_fm_input, functional_class_tm_input, functional_class_fd_input, functional_class_td_input,
            aadt_input, aadt_value_input, aadt_fm_input, aadt_tm_input, aadt_fd_input, aadt_td_input,
            search_radius_input, leg_angle_cal_distance_input, intersection_influecne_distance_input, azumith_direction_input, measure_scale
        ]

        for input in inputs:
            topSizer.Add(input, 0, wx.ALL | wx.EXPAND, 5)

        # topSizer.Add(network_input, 0, wx.ALL | wx.EXPAND, 5)
        # topSizer.Add(network_rid_input, 0, wx.ALL | wx.EXPAND, 5)
        # topSizer.Add(network_fd_input, 0, wx.ALL | wx.EXPAND, 5)
        # topSizer.Add(network_td_input, 0, wx.ALL | wx.EXPAND, 5)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(okBtn, 0, wx.ALL, 5)
        btnSizer.Add(closeBtn, 0, wx.ALL, 5)

        topSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, 5)
        topSizer.Add(btnSizer, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.panel.SetSizer(topSizer)
        self.panel.SetupScrolling()
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


# Uncomment code below to test as standalone application.
app = wx.App(False)
frame = ConfigurationDialog()
app.MainLoop()