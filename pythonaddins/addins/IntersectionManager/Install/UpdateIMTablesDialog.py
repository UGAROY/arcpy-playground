import os
import wx
import traceback
import datetime

from components.TableDialog import TableDialog
# from components.AgsProgressDialog import AgsProgressDialog

from src.tss import truncate_datetime
from src.util.helper import get_default_parameters

from src.int3_update_intersection import check_intersection_event_updates, update_intersection_event, \
    get_new_intersection_event, update_new_intersection_id, update_intersection_route_event, \
    update_roadway_segment_event, update_intersection_approach_event
from src.util.meta import read_im_meta_data, write_im_meta_data
from src.util.map import clear_table_of_content
from src.odot.ohio_dot_update import custom_update_odot
from src.roll_back_changes_since_date import roll_back

import logging
logger = logging.getLogger(__name__)

SECTION = "Default"
Config = get_default_parameters()

class UpdateIMTablesDialog(wx.Frame):
    def __init__(self):
        """Initialize the Frame and add wx widgets."""
        wx.Frame.__init__(self, None, wx.ID_ANY, title="Update Intersections Info",
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), "components/img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
        self.Size = 200, 200

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Context Section
        contextPanel = wx.Panel(self, wx.ID_ANY)
        contextSizer = wx.BoxSizer(wx.HORIZONTAL)

        context = "Intersection manager tables will be updated based on the changes made to the ALRS. Do you want to continue?"
        self.label = wx.StaticText(contextPanel, wx.ID_ANY, context, size = (190,100), style = wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        font = wx.Font(11, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.label.SetFont(font)

        png = wx.Image(os.path.join(os.path.dirname(__file__), "components/img", "information.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
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

        # Initiate table
        col_names = ["Object ID","New Intersection ID","Renamed Intersection ID"]
        self.table = TableDialog("Update Intersection Info",data=[],colLabels=col_names)

        # # Uncomment line below when testing as a standalone application.
        # self.Show(True)

    def OnClose(self, event):
        self.Show(False)

    def OnOK(self, event):
        self.Show(False)

        self.progress_bar = wx.ProgressDialog("Update Intersection Tables", "Checking updates...")

        # Input
        workspace = Config.get(SECTION, "workspace")
        meta_date_dict = read_im_meta_data(workspace)
        create_date = meta_date_dict["create_date"]
        last_update_date =  meta_date_dict["last_update_date"]
        today_date = truncate_datetime(datetime.datetime.now())

        try:
            if  last_update_date == today_date:
                # If the last_update_date is today, we will have to roll back the changes to the intersection tables
                # we have made today and also set the last_update_date to one day before to mimic the intersection related
                # events are all created yesterday. This is a workaround since the date in the network is the only
                # indicator we can use the differentiate the new and old features
                roll_back(workspace, last_update_date)
                last_update_date = last_update_date - datetime.timedelta(days=1)
            elif last_update_date is None:
                last_update_date = create_date

            if check_intersection_event_updates(workspace, last_update_date):
                # msg_dlg= wx.MessageDialog(None,"Changes have been made since %s. Do you want to update intersection tables?" % last_update_date,
                #                           "Update Intersections Info", wx.YES_NO | wx.ICON_INFORMATION)
                #
                # if msg_dlg.ShowModal() == wx.ID_YES:
                self.progress_bar.Update(10, "Updating Intersection Event...")
                update_intersection_event(workspace, last_update_date)
                self.progress_bar.Update(100, "Finished Updating New Intersection Event")

                # Review new intersections -------------------------------------------------------------------------
                intersections = get_new_intersection_event(workspace,last_update_date)

                if len(intersections):
                    self.table.PopulateTable(intersections)

                    if self.table.ShowModal() == wx.ID_OK:
                        updated_intersections = self.table.updated_data

                        if len(updated_intersections):
                            update_new_intersection_id(workspace,last_update_date,updated_intersections)
                # ---------------------------------------------------------------------------------------------------

                self.progress_bar = wx.ProgressDialog("Update Intersection Tables", "In Progress")
                self.progress_bar.Update(10, "Updating Intersection Route Event...")
                update_intersection_route_event(workspace,last_update_date)
                self.progress_bar.Update(40, "Updating Roadway Segment Event...")
                update_roadway_segment_event(workspace,last_update_date)
                self.progress_bar.Update(70, "Updating Intersection Approach Event...")
                update_intersection_approach_event(workspace,last_update_date)
                custom_update_odot(workspace, today_date)
                write_im_meta_data(workspace, None, today_date)
                clear_table_of_content(workspace)
                self.progress_bar.Update(100, "Done")

                self.progress_bar.Show(False)
                self.progress_bar.Destroy()

                dlg = wx.MessageDialog(None,"Update intersection tables success!",
                                      "Update Intersections Info", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                self.progress_bar.Update(100, "")
                self.progress_bar.Show(False)
                self.progress_bar.Destroy()

                msg_dlg= wx.MessageDialog(None,"No changed have been made since %s" % last_update_date,
                                          "Update Intersections Info", wx.OK | wx.ICON_INFORMATION)
                msg_dlg.ShowModal()
                msg_dlg.Destroy()

        except Exception, err:
            clear_table_of_content(workspace)
            logger.warning(traceback.format_exc())
            self.progress_bar.Update(100, "")
            self.progress_bar.Show(False)
            self.progress_bar.Destroy()
            wx.MessageBox(err.args[0], caption="Error", style=wx.OK | wx.ICON_ERROR)


# app = wx.App(False)
# frame = UpdateIMTablesDialog()
# app.MainLoop()