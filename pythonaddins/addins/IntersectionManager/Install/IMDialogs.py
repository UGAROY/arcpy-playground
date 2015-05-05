import os
import wx
import wx.wizard
import wx.lib.scrolledpanel as scrolled
import pythonaddins
import ConfigParser

Config = ConfigParser.ConfigParser()
init_cfg = os.path.join(os.path.dirname(__file__), "params.ini")
updated_cfg = os.path.join(os.path.dirname(__file__), "params_updated.ini")
SECTION = "Default"


def readConfigFile():
    if os.path.exists(updated_cfg):
        Config.read(updated_cfg)
    else:
        Config.read(init_cfg)


class FileInputGroup(wx.Panel):
    """An InputGroup to specify a gdb or path."""
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

    @property
    def value(self):
        return self.inputText.GetValue()

    @value.setter
    def value(self, value):
        self.inputText.SetValue(str(value))


class TextInputGroup(wx.Panel):

    def __init__(self, parent, ID=-1, inputLabel="", key=""):
        self.key = key
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.TextCtrl(self, wx.ID_ANY)
        inputGroupSizer.Add(inputLabel, pos=(0,0))
        inputGroupSizer.Add(self.inputText, pos=(1,0), flag=wx.EXPAND)
        inputGroupSizer.AddGrowableCol(0)

        self.SetSizer(inputGroupSizer)

    @property
    def value(self):
        return self.inputText.GetValue()

    @value.setter
    def value(self, value):
        self.inputText.SetValue(str(value))

class ComboBoxInputGroup(wx.Panel):

    def __init__(self, parent, ID=-1, inputLabel="", options=None, key=""):
        self.key = key
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.ComboBox(self, wx.ID_ANY, choices=options)
        inputGroupSizer.Add(inputLabel, pos=(0,0))
        inputGroupSizer.Add(self.inputText, pos=(1,0), flag=wx.EXPAND)
        inputGroupSizer.AddGrowableCol(0)

        self.SetSizer(inputGroupSizer)

    @property
    def value(self):
        return self.inputText.GetStringSelection()

    @value.setter
    def value(self, value):
        self.inputText.SetValue(str(value))

class ConfigurationDialog(wx.Frame):

    def __init__(self):
        """Initialize the Frame and add wx widgets."""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Paramters Configuration", style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), 'Tlogo.ico'), wx.BITMAP_TYPE_ICO))
        self.MinSize = 500, 400
        self.MaxSize = 600, 600
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # Content Section
        contentPanel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        contentSizer = wx.BoxSizer(wx.VERTICAL)

        self.network_input = FileInputGroup(contentPanel, -1, "Network Feature Class", topFrame=self, key="network")
        self.network_rid_input = TextInputGroup(contentPanel,  -1, "Network Route Id Field Name", key="network_route_id_field")
        self.network_rname_input = TextInputGroup(contentPanel,  -1, "Network Route Name Field Name", key="network_route_name_field")
        self.network_fd_input = TextInputGroup(contentPanel,  -1, "Network From Date Field Name", key="network_from_date_field")
        self.network_td_input = TextInputGroup(contentPanel, -1, "Network To Date Field Name", key="network_to_date_field")

        self.intersection_fp_input = FileInputGroup(contentPanel, -1, "Intersection Filter Point", topFrame=self, key="intersection_filter_event")
        self.intersection_fp_fd_input = TextInputGroup(contentPanel,  -1, "Intersection Filter Point From Date Field Name", key="intersection_filter_from_date_field")
        self.intersection_fp_td_input = TextInputGroup(contentPanel,  -1, "Intersection Filter Point To Date Field Name", key="intersection_filter_to_date_field")

        self.functional_class_input = FileInputGroup(contentPanel, -1, "Functional Class Feature Event", topFrame=self, key="function_class_event")
        self.functional_class_value_input = TextInputGroup(contentPanel,  -1, "Functional Class Value Field", key="function_class_value_field")
        self.functional_class_rid_input = TextInputGroup(contentPanel, -1, "Functional Class Route Id Field", key="function_class_rid_field")
        self.functional_class_fm_input = TextInputGroup(contentPanel,  -1, "Functional Class From Measure Field", key="function_class_from_meas_field")
        self.functional_class_tm_input = TextInputGroup(contentPanel,  -1, "Functional Class To Measure Field", key="function_class_to_meas_field")
        self.functional_class_fd_input = TextInputGroup(contentPanel,  -1, "Functional Class From Date Field", key="function_class_from_date_field")
        self.functional_class_td_input = TextInputGroup(contentPanel,  -1, "Functional Class To Date Field", key="function_class_to_date_field")

        self.aadt_input = FileInputGroup(contentPanel, -1, "AADT Feature Event", topFrame=self, key="aadt_event")
        self.aadt_value_input = TextInputGroup(contentPanel,  -1, "AADT Value Field", key="aadt_value_field")
        self.aadt_rid_input = TextInputGroup(contentPanel,  -1, "AADT Route Id Field", key="aadt_rid_field")
        self.aadt_fm_input = TextInputGroup(contentPanel,  -1, "AADT From Measure Field", key="aadt_from_meas_field")
        self.aadt_tm_input = TextInputGroup(contentPanel,  -1, "AADT To Measure Field", key="aadt_to_meas_field")
        self.aadt_fd_input = TextInputGroup(contentPanel,  -1, "AADT From Date Field", key="aadt_from_date_field")
        self.aadt_td_input = TextInputGroup(contentPanel,  -1, "AADT To Date Field", key="aadt_to_date_field")

        self.search_radius_input = TextInputGroup(contentPanel,  -1, "XY Tolerance (Feet)", key="search_radius")
        self.leg_angle_cal_distance_input = TextInputGroup(contentPanel,  -1, "Leg Angle Calculation Distance (Feet)", key="angle_calculation_distance")
        self.intersection_influecne_distance_input = TextInputGroup(contentPanel,  -1, "Intersection Influence Distance (Feet)", key="area_of_influence")
        self.azumith_direction_input = ComboBoxInputGroup(contentPanel,  -1, "Azumith Direction Used As 0 Degree", options=["N", "S", "W", "E"], key="azumith_zero_direction")
        self.measure_scale = TextInputGroup(contentPanel,  -1, "Measure Scale", key="measure_scale")

        self.inputs = [
            self.network_input, self.network_rid_input, self.network_rname_input, self.network_fd_input, self.network_td_input,
            self.intersection_fp_input, self.intersection_fp_fd_input, self.intersection_fp_td_input,
            self.functional_class_input, self.functional_class_value_input, self.functional_class_rid_input, self.functional_class_fm_input, self.functional_class_tm_input, self.functional_class_fd_input, self.functional_class_td_input,
            self.aadt_input, self.aadt_value_input, self.aadt_rid_input, self.aadt_fm_input, self.aadt_tm_input, self.aadt_fd_input, self.aadt_td_input,
            self.search_radius_input, self.leg_angle_cal_distance_input, self.intersection_influecne_distance_input, self.azumith_direction_input, self.measure_scale
        ]

        for input in self.inputs:
            contentSizer.Add(input, 0, wx.ALL | wx.EXPAND, 5)

        contentPanel.SetSizer(contentSizer)
        contentPanel.SetupScrolling()
        contentPanel.Fit()
        # End of Content Section

        # Button Toolbar
        btnPanel = wx.Panel(self, -1, size = (400, 40))

        okBtn = wx.Button(btnPanel, wx.ID_OK, 'Save')
        closeBtn = wx.Button(btnPanel, wx.ID_CANCEL, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.OnOK, okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(okBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        btnSizer.Add(closeBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)

        btnPanel.SetSizer(btnSizer)
        # End of Button Toolbar

        mainSizer.Add(contentPanel, 1, flag=wx.EXPAND)
        mainSizer.Add(btnPanel, flag=wx.EXPAND)
        self.SetSizer(mainSizer)
        self.Fit()

        ## Uncomment line below when testing as a standalone application.
        # self.Show(True)


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
        self.SaveConfigValues()
        self.Show(False)
    # End OnOK event method


    def LoadDefaultValues(self):
        """Load Configurations To Dialog"""
        readConfigFile()

        for input in self.inputs:
            input.value = Config.get(SECTION, input.key)


    def SaveConfigValues(self):
        """Save Values In the Dialogs To ConfigParser"""
        for input in self.inputs:
            Config.set(SECTION, input.key, input.value)
        with open(updated_cfg, "wb") as cfg:
            Config.write(cfg)

# Uncomment code below to test as standalone application.
# app = wx.App(False)
# frame = ConfigurationDialog()
# app.MainLoop()