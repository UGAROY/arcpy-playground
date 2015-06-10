import os
import sys
import arcpy
import wx
import wx.wizard
import wx.lib.scrolledpanel as scrolled
import wx.lib.masked as masked
import wx.calendar as calendar
import wx.grid as gridlib
import pythonaddins
import ConfigParser
import time
from wx.lib.newevent import NewEvent
from multiprocessing import *
from wx.lib.pubsub import pub
from datetime import datetime,timedelta
from threading import Thread
from tss_util import truncate_datetime, get_default_parameters, log_message

import tss

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
        log_message(os.path.join(tss.get_parent_directory(__file__), "img", "DataFrame16.png"))
        print(__file__)
        png = wx.Image(os.path.join(tss.get_parent_directory(__file__), "img", "DataFrame16.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        inputButton = wx.BitmapButton(self, wx.ID_ANY, png)
        inputGroupSizer.Add(inputLabel, pos=(0, 0))
        inputGroupSizer.Add(self.inputText, pos=(1, 0), flag=wx.EXPAND)
        inputGroupSizer.Add(inputButton, pos=(1, 1))
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
        png = wx.Image(os.path.join(tss.get_parent_directory(__file__), "img", "OpenFolder.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
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


class TextInputGroup(wx.Panel):
    def __init__(self, parent, ID=-1, inputLabel="", key=""):
        self.key = key
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.TextCtrl(self, wx.ID_ANY)
        inputGroupSizer.Add(inputLabel, pos=(0, 0))
        inputGroupSizer.Add(self.inputText, pos=(1, 0), flag=wx.EXPAND)
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
        inputGroupSizer.Add(inputLabel, pos=(0, 0))
        inputGroupSizer.Add(self.inputText, pos=(1, 0), flag=wx.EXPAND)
        inputGroupSizer.AddGrowableCol(0)

        self.SetSizer(inputGroupSizer)

    @property
    def value(self):
        return self.inputText.GetStringSelection()

    @value.setter
    def value(self, value):
        self.inputText.SetValue(str(value))


class DateTimeInputGroup(wx.Panel):
    def __init__(self, parent, ID=-1, inputLabel="", topFrame=None):
        self.topFrame = topFrame
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.TextCtrl(self, wx.ID_ANY)
        png = wx.Image(os.path.join(tss.get_parent_directory(__file__), "img", "Calendar.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        inputButton = wx.BitmapButton(self, wx.ID_ANY, png)
        inputGroupSizer.Add(inputLabel, pos=(0, 0))
        inputGroupSizer.Add(self.inputText, pos=(1, 0), flag=wx.EXPAND)
        inputGroupSizer.Add(inputButton, pos=(1, 1))
        inputGroupSizer.AddGrowableCol(0)

        self.Bind(wx.EVT_BUTTON, self.openCalendar, inputButton)

        self.SetSizer(inputGroupSizer)

        self.calendar = CalendarDialog()

    def openCalendar(self, event):
        self.topFrame.ToggleWindowStyle(wx.STAY_ON_TOP)

        if self.calendar.ShowModal() == wx.ID_OK:
            self.inputText.SetValue(self.calendar.dateTime.strftime("%Y-%m-%d %H:%M:%S"))

        self.topFrame.ToggleWindowStyle(wx.STAY_ON_TOP)

    @property
    def value(self):
        return self.calendar.dateTime


class TableGroup(wx.Panel):
    """
    @:parameters
    data: data array, example: [[value1,value2,value3...],[value_x,value_y,value_z...],[...]]
    rowNum, colNum: int
    colName: array, example: [name1,name2,name3...]
    """
    def __init__(self, parent, data, rowNum, colNum, colNames):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.data = data

        self.myGrid = gridlib.Grid(self, wx.ID_ANY)
        self.myGrid.CreateGrid(rowNum, colNum, selmode=wx.grid.Grid.SelectRows)
        self.myGrid.EnableDragGridSize()
        self.myGrid.SetRowLabelSize(0)
        self.myGrid.SetLabelFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        for i in range(0,colNum):
            self.myGrid.SetColLabelValue(i, colNames[i])
            self.myGrid.AutoSizeColLabelSize(i)

        for row in data:
            rid = data.index(row)
            for i in range(0,colNum):
                self.myGrid.SetCellValue(rid,i, str(row[i]))
                self.myGrid.SetCellFont(rid,i,wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.myGrid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()

        self.myGrid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.ShowPopupMenu)

    def ClearEdits(self,colName):
        pos = None
        for i in range(0,self.myGrid.GetNumberCols()):
            if self.myGrid.GetColLabelValue(i) == colName:
                pos = i
        if pos:
            for i in range(0,self.myGrid.GetNumberRows()):
                self.myGrid.SetCellValue(i,pos,"")

    def ShowPopupMenu(self, event):
        """
        Create and display a popup menu on right-click event
        """
        row = event.GetRow()
        self.myGrid.SelectRow(row,False)
        self.myGrid.Refresh()

        self.popupID1 = wx.NewId()
        self.menu = wx.Menu()

        # Show how to put an icon in the menu
        item = wx.MenuItem(self.menu, self.popupID1, "Zoom to Intersection")
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.menu.AppendItem(item)

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(self.menu)
        self.menu.Destroy()

    def OnPopupItemSelected(self, event):
        from tss_util import zoom_to_selected_features

        row = self.myGrid.GetSelectedRows()
        value = self.myGrid.GetCellValue(row[0],0)

        # layer_name = ""
        # where_clause = ""
        # zoom_to_selected_features(layer_name,where_clause)

        wx.MessageBox("You selected Row '%s'" % value)

    def ZoomToSelectedFeature(self,event):
        from tss_util import zoom_to_selected_features

    @property
    def value(self):
        return self.data

    # @value.setter
    # def value(self, value):
    #     pass


class TableDialog(wx.Frame):
    def __init__(self, inputLabel, data, rowNum, colNum, colName):
        """Initialize the Frame and add wx widgets."""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Update Intersections Info",
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(tss.get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
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


class CalendarDialog(wx.Dialog):
    def __init__(self, inputLabel="Date"):
        """Initialize the Frame and add wx widgets."""
        wx.Dialog.__init__(self, None, wx.ID_ANY, title=inputLabel, style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(tss.get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))

        # Calendar Section
        self.calendarCtrl = calendar.CalendarCtrl(self, wx.ID_ANY, pos=(5, 5))
        w_calendar = self.calendarCtrl.GetSize().width
        h_calendar = self.calendarCtrl.GetSize().height

        # Time Section
        self.timeCtrl = masked.TimeCtrl(self, wx.ID_ANY, pos=(15 + w_calendar, 10))
        w_time = self.timeCtrl.GetSize().width
        h_time = self.timeCtrl.GetSize().height
        spinButton = wx.SpinButton(self, -1, size=(-1, h_time), pos=(15 + w_calendar + w_time, 10),
                                   style=wx.SP_VERTICAL)
        w_spinButton = spinButton.GetSize().width
        self.timeCtrl.BindSpinButton(spinButton)

        # Button Section
        okBtn = wx.Button(self, wx.ID_OK, 'Ok', pos=(5, 15 + h_calendar))
        w_button = okBtn.GetSize().width
        h_button = okBtn.GetSize().height
        closeBtn = wx.Button(self, wx.ID_CANCEL, 'Cancel', pos=(10 + w_button, 15 + h_calendar))

        # set current time
        currentTime = datetime.now().strftime("%H:%M:%S")
        self.timeCtrl.SetValue(currentTime)

        # TODO: fit dialog size to its contents automatically
        self.SetSize((35 + w_calendar + w_time + w_spinButton, 60 + h_calendar + h_button))
        # self.Fit()
        self.CenterOnParent()

        # # Uncomment line below when testing as a standalone application.
        # self.Show(True)

    # End __init__ built-in

    # @property
    # def date(self):
    #     return self.calendarCtrl.GetDate().FormatDate()
    #
    # @property
    # def time(self):
    #     return self.timeCtrl.GetValue()

    @property
    def dateTime(self):
        date = self.calendarCtrl.GetDate().FormatISODate()
        time = self.timeCtrl.GetValue(as_wxDateTime=True).FormatISOTime()

        return datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M:%S')


class ProgressBarDialog(wx.Frame):

    def __init__(self, inputLabel="Processing Task"):

        wx.Frame.__init__(self, None, wx.ID_ANY, title=inputLabel, style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(tss.get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Process bar Section
        processBarPanel = wx.Panel(self, wx.ID_ANY)
        processBarSizer = wx.BoxSizer(wx.VERTICAL)

        self.count = 0
        self.gauge = wx.Gauge(processBarPanel, wx.ID_ANY, 100, size=(300, 30))
        self.gauge.SetBezelFace(3)
        self.gauge.SetShadowWidth(3)

        processBarSizer.Add(self.gauge, 0, wx.ALL | wx.EXPAND, 5)
        processBarPanel.SetSizer(processBarSizer)
        processBarPanel.Fit()
        # End of Process bar Section

        # Text Section
        textPanel = wx.Panel(self, wx.ID_ANY)
        textSizer = wx.BoxSizer(wx.VERTICAL)
        self.label = wx.StaticText(textPanel, wx.ID_ANY, '', style=wx.ALIGN_CENTRE_HORIZONTAL|wx.ST_NO_AUTORESIZE)

        textSizer.Add(self.label, 0, wx.ALL | wx.EXPAND, 5)
        textPanel.SetSizer(textSizer)
        textPanel.Fit()
        # End of Text Section

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(processBarPanel, 0, flag=wx.EXPAND)
        mainSizer.Add(textPanel, 0, flag=wx.EXPAND)
        self.SetSizer(mainSizer)
        self.Fit()
        self.CenterOnParent()
        self.Show(True)

        # create a pubsub receiver
        pub.subscribe(self.UpdateContents, "update_contents")
        pub.subscribe(self.UpdateProcessBar, "update_process_bar")
        pub.subscribe(self.UpdateNotification, "update_notification")

    # def OnOK(self, event):
    #     """ """
    #     self.Destroy()

    def OnClose(self, event):
        """ """
        #TODO: dialog won't close in ArcMap. Figure out why.
        # event.Skip()
        self.Destroy()

    # Issue: process bar will not refresh intermediately after calling SetValue(). Figure out why. Consider the
    #        tips before this issue got fixed.
    # Tips: when calling these functions, consider value as the percentage of completeness after the process of notification
    #       finished.
    def UpdateProcessBar(self, progress):
        self.gauge.SetValue(int(progress))
        # wx.Yield()

    def UpdateNotification(self, progress):
        self.label.SetLabel(str(progress))
        # wx.Yield()

    def UpdateContents(self, progress, notification):
        self.gauge.SetValue(int(progress))
        self.label.SetLabel(str(notification))
        # wx.Yield()


class ConfigurationDialog(wx.Frame):
    def __init__(self):
        """Initialize the Frame and add wx widgets."""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Paramters Configuration",
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(tss.get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
        self.MinSize = 500, 400
        self.MaxSize = 600, 600
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # Content Section
        contentPanel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        contentSizer = wx.BoxSizer(wx.VERTICAL)

        self.workspace = WorkspaceInputGroup(contentPanel, -1, "Workspace", topFrame=self, key="workspace")
        self.network_input = FileInputGroup(contentPanel, -1, "Network Feature Class", topFrame=self, key="network")
        self.network_rid_input = TextInputGroup(contentPanel, -1, "Network Route Id Field Name",
                                                key="network_route_id_field")
        self.network_rname_input = TextInputGroup(contentPanel, -1, "Network Route Name Field Name",
                                                  key="network_route_name_field")
        self.network_fd_input = TextInputGroup(contentPanel, -1, "Network From Date Field Name",
                                               key="network_from_date_field")
        self.network_td_input = TextInputGroup(contentPanel, -1, "Network To Date Field Name",
                                               key="network_to_date_field")

        self.intersection_fp_input = FileInputGroup(contentPanel, -1, "Intersection Filter Point", topFrame=self,
                                                    key="intersection_filter_event")
        self.intersection_fp_fd_input = TextInputGroup(contentPanel, -1,
                                                       "Intersection Filter Point From Date Field Name",
                                                       key="intersection_filter_from_date_field")
        self.intersection_fp_td_input = TextInputGroup(contentPanel, -1, "Intersection Filter Point To Date Field Name",
                                                       key="intersection_filter_to_date_field")

        self.functional_class_input = FileInputGroup(contentPanel, -1, "Functional Class Feature Event", topFrame=self,
                                                     key="function_class_event")
        self.functional_class_value_input = TextInputGroup(contentPanel, -1, "Functional Class Value Field",
                                                           key="function_class_field")
        self.functional_class_rid_input = TextInputGroup(contentPanel, -1, "Functional Class Route Id Field",
                                                         key="function_class_rid_field")
        self.functional_class_fm_input = TextInputGroup(contentPanel, -1, "Functional Class From Measure Field",
                                                        key="function_class_from_meas_field")
        self.functional_class_tm_input = TextInputGroup(contentPanel, -1, "Functional Class To Measure Field",
                                                        key="function_class_to_meas_field")
        self.functional_class_fd_input = TextInputGroup(contentPanel, -1, "Functional Class From Date Field",
                                                        key="function_class_from_date_field")
        self.functional_class_td_input = TextInputGroup(contentPanel, -1, "Functional Class To Date Field",
                                                        key="function_class_to_date_field")

        self.aadt_input = FileInputGroup(contentPanel, -1, "AADT Feature Event", topFrame=self, key="aadt_event")
        self.aadt_value_input = TextInputGroup(contentPanel, -1, "AADT Value Field", key="aadt_field")
        self.aadt_rid_input = TextInputGroup(contentPanel, -1, "AADT Route Id Field", key="aadt_rid_field")
        self.aadt_fm_input = TextInputGroup(contentPanel, -1, "AADT From Measure Field", key="aadt_from_meas_field")
        self.aadt_tm_input = TextInputGroup(contentPanel, -1, "AADT To Measure Field", key="aadt_to_meas_field")
        self.aadt_fd_input = TextInputGroup(contentPanel, -1, "AADT From Date Field", key="aadt_from_date_field")
        self.aadt_td_input = TextInputGroup(contentPanel, -1, "AADT To Date Field", key="aadt_to_date_field")

        self.search_radius_input = TextInputGroup(contentPanel, -1, "XY Tolerance (Feet)", key="search_radius")
        self.leg_angle_cal_distance_input = TextInputGroup(contentPanel, -1, "Leg Angle Calculation Distance (Feet)",
                                                           key="angle_calculation_distance")
        self.intersection_influecne_distance_input = TextInputGroup(contentPanel, -1,
                                                                    "Intersection Influence Distance (Feet)",
                                                                    key="area_of_influence")
        self.azumith_direction_input = ComboBoxInputGroup(contentPanel, -1, "Azumith Direction Used As 0 Degree",
                                                          options=["N", "S", "W", "E"], key="azumith_zero_direction")
        self.measure_scale = TextInputGroup(contentPanel, -1, "Measure Scale", key="measure_scale")

        self.inputs = [
            self.workspace,
            self.network_input, self.network_rid_input, self.network_rname_input, self.network_fd_input,
            self.network_td_input,
            self.intersection_fp_input, self.intersection_fp_fd_input, self.intersection_fp_td_input,
            self.functional_class_input, self.functional_class_value_input, self.functional_class_rid_input,
            self.functional_class_fm_input, self.functional_class_tm_input, self.functional_class_fd_input,
            self.functional_class_td_input,
            self.aadt_input, self.aadt_value_input, self.aadt_rid_input, self.aadt_fm_input, self.aadt_tm_input,
            self.aadt_fd_input, self.aadt_td_input,
            self.search_radius_input, self.leg_angle_cal_distance_input, self.intersection_influecne_distance_input,
            self.azumith_direction_input, self.measure_scale
        ]

        for input in self.inputs:
            contentSizer.Add(input, 0, wx.ALL | wx.EXPAND, 5)

        contentPanel.SetSizer(contentSizer)
        contentPanel.SetupScrolling()
        contentPanel.Fit()
        # End of Content Section

        # Button Toolbar
        btnPanel = wx.Panel(self, -1, size=(400, 40))

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
        self.CenterOnScreen()

        # # Uncomment line below when testing as a standalone application.
        # self.LoadDefaultValues
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


class PopulateIMTablesDialog(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Populate Intersections Info",
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(tss.get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
        self.MinSize = 500, 400
        self.MaxSize = 600, 600
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Content Section
        contentPanel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        contentSizer = wx.BoxSizer(wx.VERTICAL)

        self.dateTime = DateTimeInputGroup(contentPanel, -1, "Date", topFrame=self)

        self.inputs = [
            self.dateTime
        ]

        for input in self.inputs:
            contentSizer.Add(input, 0, wx.ALL | wx.EXPAND, 5)

        contentPanel.SetSizer(contentSizer)
        contentPanel.SetupScrolling()
        contentPanel.Fit()
        # End of content Section

        # Button Toolbar
        btnPanel = wx.Panel(self, -1, size=(400, 40))

        okBtn = wx.Button(btnPanel, wx.ID_OK, 'Ok')
        closeBtn = wx.Button(btnPanel, wx.ID_CANCEL, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.OnOK, okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(okBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        btnSizer.Add(closeBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)

        btnPanel.SetSizer(btnSizer)
        # End of Button Toolbar

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(contentPanel, 1, flag=wx.EXPAND)
        mainSizer.Add(btnPanel, flag=wx.EXPAND)
        self.SetSizer(mainSizer)
        self.Fit()
        self.CenterOnScreen()

        # # Uncomment line below when testing as a standalone application.
        self.LoadDefaultValues()
        self.Show(True)

    # End __init__ built-in

    def LoadDefaultValues(self):
        """Load Configurations To Dialog"""
        readConfigFile()

    def OnClose(self, event):
        """Close the frame. Do not use destroy."""
        self.Show(False)

    # End OnClose event method

    def OnOK(self, event):
        """Close the frame. Do not use destroy."""
        try:
            self.Show(False)

            self.progress_bar = ProgressBarDialog("Populate Intersection Tables")

            create_date = self.dateTime.value
            PopulateIMTablesTasks(create_date)


            # return

        except Exception as ex:
            # self.process_bar.Destroy()
            log_message(ex.args[0])
            wx.MessageBox(ex.args[0], caption="Error", style=wx.OK | wx.ICON_ERROR)

    # End OnOK event method


class UpdateTMTablesDialog(wx.Frame):
    def __init__(self):
        """Initialize the Frame and add wx widgets."""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Update Intersections Info",
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(tss.get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
        self.Size = 200, 200

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Context Section
        contextPanel = wx.Panel(self, wx.ID_ANY)
        contextSizer = wx.BoxSizer(wx.HORIZONTAL)

        context = "Intersection manager tables will be updated based on the changes made to the ALRS. Do you want to continue?"
        self.label = wx.StaticText(contextPanel, wx.ID_ANY, context, size = (190,100), style = wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        font = wx.Font(11, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.label.SetFont(font)

        png = wx.Image(os.path.join(tss.get_parent_directory(__file__), "img", "information.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.picture = wx.StaticBitmap(contextPanel, wx.ID_ANY, png)

        contextSizer.Add(self.picture, 0, wx.ALL | wx.EXPAND, 10)
        contextSizer.Add(self.label, 0, wx.ALL | wx.EXPAND, 10)
        contextPanel.SetSizer(contextSizer)
        contextPanel.Fit()
        # End of Context Section

        # Button Toolbar
        btnPanel = wx.Panel(self, -1, size=(180, 40))

        yesBtn = wx.Button(btnPanel, wx.ID_YES, 'Yes')
        noBtn = wx.Button(btnPanel, wx.ID_NO, 'No')

        self.Bind(wx.EVT_BUTTON, self.OnOK, yesBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, noBtn)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(yesBtn, 1, wx.ALL | wx.ALIGN_RIGHT, 5)
        btnSizer.Add(noBtn, 1, wx.ALL | wx.ALIGN_RIGHT, 5)

        btnPanel.SetSizer(btnSizer)
        # End of Button Toolbar

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(contextPanel, 1, flag=wx.EXPAND)
        mainSizer.Add(btnPanel, flag=wx.EXPAND)
        self.SetSizer(mainSizer)
        self.Fit()
        self.CenterOnScreen()

        # # Uncomment line below when testing as a standalone application.
        # self.LoadDefaultValues()
        # self.Show(True)

    def LoadDefaultValues(self):
        """Load Configurations To Dialog"""
        readConfigFile()

    def OnClose(self, event):
        self.Show(False)

    def OnOK(self, event):
        try:
            self.Show(False)

            # processBar = ProgressBarDialog("Update Intersection Manager Tables")
            # processBar.UpdateContents(10,"Initializing task...")

            from int3_update_intersection import update_intersection_tables, check_intersection_tables_updates
            from intersection_util import read_im_meta_data, write_im_meta_data
            from ohio_dot_update import custom_update_odot
            from roll_back_changes_since_date import roll_back

            # Input
            workspace = Config.get(SECTION, "workspace")
            meta_date_dict = read_im_meta_data(workspace)
            create_date = meta_date_dict["create_date"]
            last_update_date =  meta_date_dict["last_update_date"]
            today_date = truncate_datetime(datetime.now())

            if  last_update_date == today_date:
                # If the last_update_date is today, we will have to roll back the changes to the intersection tables
                # we have made today and also set the last_update_date to one day before to mimic the intersection related
                # events are all created yesterday. This is a workaround since the date in the network is the only
                # indicator we can use the differentiate the new and old features
                roll_back(workspace, last_update_date)
                last_update_date = last_update_date - timedelta(days=1)
            elif last_update_date is None:
                last_update_date = create_date - timedelta(days=1)

            if check_intersection_tables_updates(workspace, last_update_date):
                msg_dlg= wx.MessageDialog(None,"Changed have been made since %s. Do you want to update intersection tables?" % last_update_date,
                                          "Update Intersections Info", wx.YES_NO | wx.ICON_INFORMATION)
                result = msg_dlg.ShowModal()

                if result == wx.ID_OK:
                    update_intersection_tables(workspace, last_update_date)
                    custom_update_odot(workspace, today_date)
                    write_im_meta_data(workspace, None, today_date)
            else:
                msg_dlg= wx.MessageDialog(None,"No changed have been made since %s" % last_update_date,
                                          "Update Intersections Info", wx.OK | wx.ICON_INFORMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()

                data = [["1","11",""],["2","22",""],["3","33",""]]
                col_name = ["Object ID","Current Intersection ID", "New Intersection ID"]

                TableDialog("Update Itersection Info",data,3,3,col_name)

                # processBar.UpdateContents(100,"Done!")

            # processBar.UpdateNotification("Done!")

        except Exception as ex:
            wx.MessageBox(ex.args[0], caption="Error", style=wx.OK | wx.ICON_ERROR)

class SetViewDate(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Set View Date",
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(tss.get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
        self.MinSize = 500, 400
        self.MaxSize = 600, 600
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Content Section
        contentPanel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
        contentSizer = wx.BoxSizer(wx.VERTICAL)

        self.dateTime = DateTimeInputGroup(contentPanel, -1, "Date", topFrame=self)

        self.dateTime.inputText.SetValue(truncate_datetime(datetime.now()).strftime("%Y-%m-%d"))

        self.inputs = [
            self.dateTime
        ]

        for input in self.inputs:
            contentSizer.Add(input, 0, wx.ALL | wx.EXPAND, 5)

        contentPanel.SetSizer(contentSizer)
        contentPanel.SetupScrolling()
        contentPanel.Fit()
        # End of content Section

        # Button Toolbar
        btnPanel = wx.Panel(self, -1, size=(400, 40))

        okBtn = wx.Button(btnPanel, wx.ID_OK, 'Ok')
        closeBtn = wx.Button(btnPanel, wx.ID_CANCEL, 'Cancel')
        self.Bind(wx.EVT_BUTTON, self.OnOK, okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(okBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
        btnSizer.Add(closeBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)

        btnPanel.SetSizer(btnSizer)
        # End of Button Toolbar

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(contentPanel, 1, flag=wx.EXPAND)
        mainSizer.Add(btnPanel, flag=wx.EXPAND)
        self.SetSizer(mainSizer)
        self.Fit()
        self.CenterOnScreen()

        # # Uncomment line below when testing as a standalone application.
        # self.LoadDefaultValues()
        # self.Show(True)

    # End __init__ built-in

    def LoadDefaultValues(self):
        """Load Configurations To Dialog"""
        readConfigFile()

    def OnClose(self, event):
        """Close the frame. Do not use destroy."""
        self.Show(False)
        self.Close()

    # End OnClose event method

    def OnOK(self, event):
        """Close the frame. Do not use destroy."""
        try:
            self.Show(False)

            from schema import default_schemas
            from tss_util import format_sql_date
            parameters = get_default_parameters()

            schemas = default_schemas.get("Default")
            dbtype = parameters.get("Default", "dbtype")

            from_date_field = schemas.get("from_date_field")
            to_date_field = schemas.get("to_date_field")
            intersection_event = schemas.get("intersection_event")
            intersection_route_event = schemas.get("intersection_route_event")
            roadway_segment_event = schemas.get("roadway_segment_event")
            intersection_approach_event = schemas.get("intersection_approach_event")
            view_date = self.dateTime.inputText.GetValue() or truncate_datetime(datetime.now())
            view_date_query_string = format_sql_date(view_date, dbtype)
            mxd = arcpy.mapping.MapDocument("CURRENT")
            tba_items = arcpy.mapping.ListLayers(mxd) + arcpy.mapping.ListTableViews(mxd)

            for item in tba_items:
                if item.name in [intersection_event, intersection_route_event, roadway_segment_event, intersection_approach_event]:
                    item.definitionQuery = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(from_date_field, to_date_field, view_date_query_string)

            arcpy.RefreshActiveView()
            del mxd

            self.Show(True)

        except Exception as ex:
            wx.MessageBox(ex.args[0], caption="Error", style=wx.OK | wx.ICON_ERROR)

    # End OnOK event method

# Threading section ----------------------------------------------------------------------------------------------------

class PopulateIMTablesTasks(Thread):
    def __init__(self,create_date):
        """Init Worker Thread Class."""
        Thread.__init__(self)

        self.create_date = create_date

        # start the thread
        self.start()

    def run(self):

        wx.CallAfter(pub.sendMessage, "update_contents", progress=0, notification="Initiating task...")

        from int1_populate_base_info_for_intersections import populate_intersections_info
        from int2_generate_intersection_approach_records import populate_intersection_leg_info
        from ohio_dot_create import custom_create_odot
        from intersection_util import write_im_meta_data

        # Input
        workspace = Config.get(SECTION, "workspace")
        create_date = self.create_date

        # Tasks
        wx.CallAfter(pub.sendMessage, "update_contents",progress=10, notification="Populating Intersection Info...")
        populate_intersections_info(workspace, create_date)

        wx.CallAfter(pub.sendMessage, "update_contents",progress=40, notification="Populating Intersection Leg Info...")
        populate_intersection_leg_info(workspace, create_date)

        wx.CallAfter(pub.sendMessage, "update_contents",progress=70, notification="ODOT Customization...")
        custom_create_odot(workspace)

        wx.CallAfter(pub.sendMessage, "update_contents",progress=85, notification="Updating meta file...")
        write_im_meta_data(workspace, create_date)

        wx.CallAfter(pub.sendMessage, "update_contents", progress=100, notification="Populate intersection manager tables success!")



# EVT_RESULT_ID = wx.NewId()
#
# def EVT_RESULT(win,func):
#     """ Define Result Event"""
#     win.Connect(-1,-1,EVT_RESULT_ID,func)
#
# class ResultEvent(wx.PyEvent):
#     """Simple event to carry arbitrary result data."""
#     def __init__(self, data):
#         """Init Result Event."""
#         wx.PyEvent.__init__(self)
#         self.SetEventType(EVT_RESULT_ID)
#         self.data = data

# ResultEvent, EVT_RESULT = NewEvent()
#-----------------------------------------------------------------------------------------------------------------------



# Uncomment code below to test as standalone application.
app = wx.App(False)
frame = PopulateIMTablesDialog()
app.MainLoop()
