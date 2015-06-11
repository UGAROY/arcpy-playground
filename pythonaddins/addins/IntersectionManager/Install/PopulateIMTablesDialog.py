import os
import wx
import wx.lib.scrolledpanel as scrolled

from components.DateTimeInputGroup import DateTimeInputGroup
from components.AgsProgressDialog import AgsProgressDialog

import sys
sys.path.append(os.path.dirname(__file__))

from src.int1_populate_base_info_for_intersections import populate_intersections_info
from src.int2_generate_intersection_approach_records import populate_intersection_leg_info
from src.util.meta import write_im_meta_data
from src.util.helper import get_default_parameters


SECTION = "Default"

class PopulateIMTablesDialog(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Populate Intersections Info",
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), "components/img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
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
        # self.Show(True)

    # End __init__ built-in

    def OnClose(self, event):
        """Close the frame. Do not use destroy."""
        self.Show(False)

    # End OnClose event method

    def OnOK(self, event):
        """Close the frame. Do not use destroy."""
        try:
            self.Show(False)

            self.progress_bar = AgsProgressDialog("Populate Intersection Tables", "Progress")

            # Input
            parameters = get_default_parameters()
            workspace = parameters.get(SECTION, "workspace")
            create_date = self.dateTime.value

            # Tasks
            self.progress_bar.Update(10, "Populating Intersection Info...")
            populate_intersections_info(workspace, create_date)

            self.progress_bar.Update(40, "Populating Intersection Leg Info...")
            populate_intersection_leg_info(workspace, create_date)

            self.progress_bar.Update(70, "ODOT Customization...")
            # custom_create_odot(workspace)

            self.progress_bar.Update(85,"Updating meta file...")
            write_im_meta_data(workspace, create_date)

            self.progress_bar.Update(100, "Populate intersection manager tables success!")

        except Exception, err:
            # self.progress_bar.Update(100, err.args[0])
            # wx.MessageBox(err.args[0], caption="Error", style=wx.OK | wx.ICON_ERROR)
            self.progress_bar.Exit(err.args[0])

    # End OnOK event method

# app = wx.App(False)
# frame = PopulateIMTablesDialog()
# app.MainLoop()
