import os
import wx
import arcpy

import wx.lib.scrolledpanel as scrolled
from components.DateTimeInputGroup import DateTimeInputGroup

from datetime import datetime
from src.tss import truncate_datetime, format_sql_date
from src.config.schema import default_schemas
from src.util.helper import get_default_parameters

class SetViewDateDialog(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Set View Date",
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), "components/img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
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
        # self.Show(True)

    # End __init__ built-in

    def OnClose(self, event):
        """Close the frame. Do not use destroy."""
        self.Show(False)
        self.Close()

    # End OnClose event method

    def OnOK(self, event):
        """Close the frame. Do not use destroy."""
        try:
            self.Show(False)

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


# app = wx.App(False)
# frame = SetViewDateDialog()
# app.MainLoop()