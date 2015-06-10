import os
import wx
import ConfigParser

from datetime import datetime, timedelta
from components.TableDialog import TableDialog

from src.tss import truncate_datetime
from src.util.helper import get_default_parameters

SECTION = "Default"

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

        # # Uncomment line below when testing as a standalone application.
        # self.LoadDefaultValues()
        # self.Show(True)

    def OnClose(self, event):
        self.Show(False)

    def OnOK(self, event):
        try:
            self.Show(False)

            # processBar = ProgressBarDialog("Update Intersection Manager Tables")
            # processBar.UpdateContents(10,"Initializing task...")

            from ..src.int3_update_intersection import update_intersection_tables, check_intersection_tables_updates
            from ..src.util.meta import read_im_meta_data, write_im_meta_data
            from ..src.odot.ohio_dot_update import custom_update_odot
            from ..src.roll_back_changes_since_date import roll_back

            # Input
            parameters = get_default_parameters()
            workspace = parameters.get(SECTION, "workspace")
            meta_date_dict = read_im_meta_data(workspace)
            create_date = meta_date_dict["create_date"]
            last_update_date =  meta_date_dict["last_update_date"]
            today_date = truncate_datetime(datetime.now())

            if  last_update_date == today_date:
                # If the last_update_date is today, we will have to roll back the changes to the src tables
                # we have made today and also set the last_update_date to one day before to mimic the src related
                # events are all created yesterday. This is a workaround since the date in the network is the only
                # indicator we can use the differentiate the new and old features
                roll_back(workspace, last_update_date)
                last_update_date = last_update_date - timedelta(days=1)
            elif last_update_date is None:
                last_update_date = create_date - timedelta(days=1)

            if check_intersection_tables_updates(workspace, last_update_date):
                msg_dlg= wx.MessageDialog(None,"Changed have been made since %s. Do you want to update src tables?" % last_update_date,
                                          "Update Intersections Info", wx.OK | wx.ICON_INFORMATION)
                msg_dlg.ShowModal()

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