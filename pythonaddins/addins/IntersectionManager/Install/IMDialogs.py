# import os
# import ConfigParser
# from datetime import datetime,timedelta
#
# import arcpy
# import wx
# import wx.wizard
# import wx.lib.scrolledpanel as scrolled
# import wx.lib.masked as masked
# import wx.calendar as calendar
# import wx.grid as gridlib
#
# import pythonaddins
# from src.tss import truncate_datetime, get_parent_directory
# from src.util.helper import get_default_parameters, log_message
#
#
# Config = ConfigParser.ConfigParser()
# init_cfg = os.path.join(os.path.dirname(__file__), "src/config/params.ini")
# updated_cfg = os.path.join(os.path.dirname(__file__), "params_updated.ini")
# SECTION = "Default"
#
#
# def readConfigFile():
#     if os.path.exists(updated_cfg):
#         Config.read(updated_cfg)
#     else:
#         Config.read(init_cfg)
#
# class ProgressBarDialog(wx.Frame):
#
#     def __init__(self, inputLabel="Processing Task"):
#
#         wx.Frame.__init__(self, None, wx.ID_ANY, title=inputLabel, style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
#         self.SetIcon(wx.Icon(os.path.join(get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
#
#         self.Bind(wx.EVT_CLOSE, self.OnClose)
#
#         # Process bar Section
#         processBarPanel = wx.Panel(self, wx.ID_ANY)
#         processBarSizer = wx.BoxSizer(wx.VERTICAL)
#
#         self.count = 0
#         self.gauge = wx.Gauge(processBarPanel, wx.ID_ANY, 100, size=(300, 30))
#         self.gauge.SetBezelFace(3)
#         self.gauge.SetShadowWidth(3)
#
#         processBarSizer.Add(self.gauge, 0, wx.ALL | wx.EXPAND, 5)
#         processBarPanel.SetSizer(processBarSizer)
#         processBarPanel.Fit()
#         # End of Process bar Section
#
#         # Text Section
#         textPanel = wx.Panel(self, wx.ID_ANY)
#         textSizer = wx.BoxSizer(wx.VERTICAL)
#         self.label = wx.StaticText(textPanel, wx.ID_ANY, '', style=wx.ALIGN_CENTRE_HORIZONTAL|wx.ST_NO_AUTORESIZE)
#
#         textSizer.Add(self.label, 0, wx.ALL | wx.EXPAND, 5)
#         textPanel.SetSizer(textSizer)
#         textPanel.Fit()
#         # End of Text Section
#
#         mainSizer = wx.BoxSizer(wx.VERTICAL)
#         mainSizer.Add(processBarPanel, 0, flag=wx.EXPAND)
#         mainSizer.Add(textPanel, 0, flag=wx.EXPAND)
#         self.SetSizer(mainSizer)
#         self.Fit()
#         self.CenterOnParent()
#         self.Show(True)
#
#     # def OnOK(self, event):
#     #     """ """
#     #     self.Destroy()
#
#     def OnClose(self, event):
#         """ """
#         #TODO: dialog won't close in ArcMap. Figure out why.
#         event.Skip()
#         self.Destroy()
#         # self.Close()
#
#     # Issue: process bar will not refresh intermediately after calling SetValue(). Figure out why. Consider the
#     #        tips before this issue got fixed.
#     # Tips: when calling these functions, consider value as the percentage of completeness after the process of notification
#     #       finished.
#     def UpdateProcessBar(self, value):
#         self.gauge.SetValue(value)
#         wx.Yield()
#
#     def UpdateNotification(self, value):
#         self.label.SetLabel(str(value))
#         wx.Yield()
#
#     def UpdateContents(self, value, notification):
#         self.gauge.SetValue(value)
#         self.label.SetLabel(str(notification))
#         wx.Yield()
#
#
# class ConfigurationDialog(wx.Frame):
#     def __init__(self):
#         """Initialize the Frame and add wx widgets."""
#         wx.Frame.__init__(self, None, wx.ID_ANY, title="Paramters Configuration",
#                           style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
#         self.SetIcon(wx.Icon(os.path.join(get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
#         self.MinSize = 500, 400
#         self.MaxSize = 600, 600
#         self.Bind(wx.EVT_CLOSE, self.OnClose)
#
#         mainSizer = wx.BoxSizer(wx.VERTICAL)
#
#         # Content Section
#         contentPanel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
#         contentSizer = wx.BoxSizer(wx.VERTICAL)
#
#         self.workspace = WorkspaceInputGroup(contentPanel, -1, "Workspace", topFrame=self, key="workspace")
#         self.network_input = FileInputGroup(contentPanel, -1, "Network Feature Class", topFrame=self, key="network")
#         self.network_rid_input = TextInputGroup(contentPanel, -1, "Network Route Id Field Name",
#                                                 key="network_route_id_field")
#         self.network_rname_input = TextInputGroup(contentPanel, -1, "Network Route Name Field Name",
#                                                   key="network_route_name_field")
#         self.network_fd_input = TextInputGroup(contentPanel, -1, "Network From Date Field Name",
#                                                key="network_from_date_field")
#         self.network_td_input = TextInputGroup(contentPanel, -1, "Network To Date Field Name",
#                                                key="network_to_date_field")
#
#         self.intersection_fp_input = FileInputGroup(contentPanel, -1, "Intersection Filter Point", topFrame=self,
#                                                     key="intersection_filter_event")
#         self.intersection_fp_fd_input = TextInputGroup(contentPanel, -1,
#                                                        "Intersection Filter Point From Date Field Name",
#                                                        key="intersection_filter_from_date_field")
#         self.intersection_fp_td_input = TextInputGroup(contentPanel, -1, "Intersection Filter Point To Date Field Name",
#                                                        key="intersection_filter_to_date_field")
#
#         self.functional_class_input = FileInputGroup(contentPanel, -1, "Functional Class Feature Event", topFrame=self,
#                                                      key="function_class_event")
#         self.functional_class_value_input = TextInputGroup(contentPanel, -1, "Functional Class Value Field",
#                                                            key="function_class_field")
#         self.functional_class_rid_input = TextInputGroup(contentPanel, -1, "Functional Class Route Id Field",
#                                                          key="function_class_rid_field")
#         self.functional_class_fm_input = TextInputGroup(contentPanel, -1, "Functional Class From Measure Field",
#                                                         key="function_class_from_meas_field")
#         self.functional_class_tm_input = TextInputGroup(contentPanel, -1, "Functional Class To Measure Field",
#                                                         key="function_class_to_meas_field")
#         self.functional_class_fd_input = TextInputGroup(contentPanel, -1, "Functional Class From Date Field",
#                                                         key="function_class_from_date_field")
#         self.functional_class_td_input = TextInputGroup(contentPanel, -1, "Functional Class To Date Field",
#                                                         key="function_class_to_date_field")
#
#         self.aadt_input = FileInputGroup(contentPanel, -1, "AADT Feature Event", topFrame=self, key="aadt_event")
#         self.aadt_value_input = TextInputGroup(contentPanel, -1, "AADT Value Field", key="aadt_field")
#         self.aadt_rid_input = TextInputGroup(contentPanel, -1, "AADT Route Id Field", key="aadt_rid_field")
#         self.aadt_fm_input = TextInputGroup(contentPanel, -1, "AADT From Measure Field", key="aadt_from_meas_field")
#         self.aadt_tm_input = TextInputGroup(contentPanel, -1, "AADT To Measure Field", key="aadt_to_meas_field")
#         self.aadt_fd_input = TextInputGroup(contentPanel, -1, "AADT From Date Field", key="aadt_from_date_field")
#         self.aadt_td_input = TextInputGroup(contentPanel, -1, "AADT To Date Field", key="aadt_to_date_field")
#
#         self.search_radius_input = TextInputGroup(contentPanel, -1, "XY Tolerance (Feet)", key="search_radius")
#         self.leg_angle_cal_distance_input = TextInputGroup(contentPanel, -1, "Leg Angle Calculation Distance (Feet)",
#                                                            key="angle_calculation_distance")
#         self.intersection_influecne_distance_input = TextInputGroup(contentPanel, -1,
#                                                                     "Intersection Influence Distance (Feet)",
#                                                                     key="area_of_influence")
#         self.azumith_direction_input = ComboBoxInputGroup(contentPanel, -1, "Azumith Direction Used As 0 Degree",
#                                                           options=["N", "S", "W", "E"], key="azumith_zero_direction")
#         self.measure_scale = TextInputGroup(contentPanel, -1, "Measure Scale", key="measure_scale")
#
#         self.inputs = [
#             self.workspace,
#             self.network_input, self.network_rid_input, self.network_rname_input, self.network_fd_input,
#             self.network_td_input,
#             self.intersection_fp_input, self.intersection_fp_fd_input, self.intersection_fp_td_input,
#             self.functional_class_input, self.functional_class_value_input, self.functional_class_rid_input,
#             self.functional_class_fm_input, self.functional_class_tm_input, self.functional_class_fd_input,
#             self.functional_class_td_input,
#             self.aadt_input, self.aadt_value_input, self.aadt_rid_input, self.aadt_fm_input, self.aadt_tm_input,
#             self.aadt_fd_input, self.aadt_td_input,
#             self.search_radius_input, self.leg_angle_cal_distance_input, self.intersection_influecne_distance_input,
#             self.azumith_direction_input, self.measure_scale
#         ]
#
#         for input in self.inputs:
#             contentSizer.Add(input, 0, wx.ALL | wx.EXPAND, 5)
#
#         contentPanel.SetSizer(contentSizer)
#         contentPanel.SetupScrolling()
#         contentPanel.Fit()
#         # End of Content Section
#
#         # Button Toolbar
#         btnPanel = wx.Panel(self, -1, size=(400, 40))
#
#         okBtn = wx.Button(btnPanel, wx.ID_OK, 'Save')
#         closeBtn = wx.Button(btnPanel, wx.ID_CANCEL, 'Cancel')
#         self.Bind(wx.EVT_BUTTON, self.OnOK, okBtn)
#         self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)
#
#         btnSizer = wx.BoxSizer(wx.HORIZONTAL)
#         btnSizer.Add(okBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
#         btnSizer.Add(closeBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
#
#         btnPanel.SetSizer(btnSizer)
#         # End of Button Toolbar
#
#         mainSizer.Add(contentPanel, 1, flag=wx.EXPAND)
#         mainSizer.Add(btnPanel, flag=wx.EXPAND)
#         self.SetSizer(mainSizer)
#         self.Fit()
#         self.CenterOnScreen()
#
#         # # Uncomment line below when testing as a standalone application.
#         # self.LoadDefaultValues
#         self.Show(True)
#
#
#     # End __init__ built-in
#
#     def OnClose(self, event):
#         """Close the frame. Do not use destroy."""
#         self.Show(False)
#
#     # End OnClose event method
#
#     def OnOK(self, event):
#         """Renames the active data frame of map document."""
#         # sTitle = str(self.dfName.GetValue())
#         # mxd = arcpy.mapping.MapDocument("CURRENT")
#         # df = mxd.activeDataFrame
#         # df.name = sTitle
#         # arcpy.RefreshTOC()
#         self.SaveConfigValues()
#         self.Show(False)
#
#     # End OnOK event method
#
#
#     def LoadDefaultValues(self):
#         """Load Configurations To Dialog"""
#         readConfigFile()
#
#         for input in self.inputs:
#             input.value = Config.get(SECTION, input.key)
#
#
#     def SaveConfigValues(self):
#         """Save Values In the Dialogs To ConfigParser"""
#         for input in self.inputs:
#             Config.set(SECTION, input.key, input.value)
#         with open(updated_cfg, "wb") as cfg:
#             Config.write(cfg)
#
#
# class PopulateIMTablesDialog(wx.Frame):
#     def __init__(self):
#         wx.Frame.__init__(self, None, wx.ID_ANY, title="Populate Intersections Info",
#                           style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
#         self.SetIcon(wx.Icon(os.path.join(get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
#         self.MinSize = 500, 400
#         self.MaxSize = 600, 600
#         self.Bind(wx.EVT_CLOSE, self.OnClose)
#
#         # Content Section
#         contentPanel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
#         contentSizer = wx.BoxSizer(wx.VERTICAL)
#
#         self.dateTime = DateTimeInputGroup(contentPanel, -1, "Date", topFrame=self)
#
#         self.inputs = [
#             self.dateTime
#         ]
#
#         for input in self.inputs:
#             contentSizer.Add(input, 0, wx.ALL | wx.EXPAND, 5)
#
#         contentPanel.SetSizer(contentSizer)
#         contentPanel.SetupScrolling()
#         contentPanel.Fit()
#         # End of content Section
#
#         # Button Toolbar
#         btnPanel = wx.Panel(self, -1, size=(400, 40))
#
#         okBtn = wx.Button(btnPanel, wx.ID_OK, 'Ok')
#         closeBtn = wx.Button(btnPanel, wx.ID_CANCEL, 'Cancel')
#         self.Bind(wx.EVT_BUTTON, self.OnOK, okBtn)
#         self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)
#
#         btnSizer = wx.BoxSizer(wx.HORIZONTAL)
#         btnSizer.Add(okBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
#         btnSizer.Add(closeBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
#
#         btnPanel.SetSizer(btnSizer)
#         # End of Button Toolbar
#
#         mainSizer = wx.BoxSizer(wx.VERTICAL)
#         mainSizer.Add(contentPanel, 1, flag=wx.EXPAND)
#         mainSizer.Add(btnPanel, flag=wx.EXPAND)
#         self.SetSizer(mainSizer)
#         self.Fit()
#         self.CenterOnScreen()
#
#         # # Uncomment line below when testing as a standalone application.
#         self.LoadDefaultValues()
#         self.Show(True)
#
#     # End __init__ built-in
#
#     def LoadDefaultValues(self):
#         """Load Configurations To Dialog"""
#         readConfigFile()
#
#     def OnClose(self, event):
#         """Close the frame. Do not use destroy."""
#         self.Show(False)
#
#     # End OnClose event method
#
#     def OnOK(self, event):
#         """Close the frame. Do not use destroy."""
#         try:
#             self.Show(False)
#
#             processBar = ProgressBarDialog("Populate Intersection Manager Tables")
#             processBar.UpdateContents(10,"Initializing task...")
#
#             from src.int1_populate_base_info_for_intersections import populate_intersections_info
#             from src.int2_generate_intersection_approach_records import populate_intersection_leg_info
#             from src.odot.ohio_dot_create import custom_create_odot
#             from src.util.meta import write_im_meta_data
#
#             # Input
#             workspace = Config.get(SECTION, "workspace")
#             create_date = self.dateTime.value
#
#
#             processBar.UpdateContents(40,"Populating Intersection Info...")
#             populate_intersections_info(workspace, create_date)
#
#             processBar.UpdateContents(70,"Populating Intersection Leg Info...")
#             populate_intersection_leg_info(workspace, create_date)
#
#             processBar.UpdateContents(85,"ODOT Customization...")
#             custom_create_odot(workspace)
#
#             processBar.UpdateContents(100,"Updating meta file...")
#             write_im_meta_data(workspace, create_date)
#
#             processBar.UpdateNotification("Done!")
#
#             # return
#
#         except Exception as ex:
#             log_message(ex.args[0])
#             wx.MessageBox(ex.args[0], caption="Error", style=wx.OK | wx.ICON_ERROR)
#
#     # End OnOK event method
#
#
# class UpdateTMTablesDialog(wx.Frame):
#     def __init__(self):
#         """Initialize the Frame and add wx widgets."""
#         wx.Frame.__init__(self, None, wx.ID_ANY, title="Update Intersections Info",
#                           style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
#         self.SetIcon(wx.Icon(os.path.join(get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
#         self.Size = 200, 200
#
#         self.Bind(wx.EVT_CLOSE, self.OnClose)
#
#         # Context Section
#         contextPanel = wx.Panel(self, wx.ID_ANY)
#         contextSizer = wx.BoxSizer(wx.HORIZONTAL)
#
#         context = "Intersection manager tables will be updated based on the changes made to the ALRS. Do you want to continue?"
#         self.label = wx.StaticText(contextPanel, wx.ID_ANY, context, size = (190,100), style = wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
#         font = wx.Font(11, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
#         self.label.SetFont(font)
#
#         png = wx.Image(os.path.join(get_parent_directory(__file__), "img", "information.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
#         self.picture = wx.StaticBitmap(contextPanel, wx.ID_ANY, png)
#
#         contextSizer.Add(self.picture, 0, wx.ALL | wx.EXPAND, 10)
#         contextSizer.Add(self.label, 0, wx.ALL | wx.EXPAND, 10)
#         contextPanel.SetSizer(contextSizer)
#         contextPanel.Fit()
#         # End of Context Section
#
#         # Button Toolbar
#         btnPanel = wx.Panel(self, -1, size=(180, 40))
#
#         yesBtn = wx.Button(btnPanel, wx.ID_YES, 'Yes')
#         noBtn = wx.Button(btnPanel, wx.ID_NO, 'No')
#
#         self.Bind(wx.EVT_BUTTON, self.OnOK, yesBtn)
#         self.Bind(wx.EVT_BUTTON, self.OnClose, noBtn)
#
#         btnSizer = wx.BoxSizer(wx.HORIZONTAL)
#         btnSizer.Add(yesBtn, 1, wx.ALL | wx.ALIGN_RIGHT, 5)
#         btnSizer.Add(noBtn, 1, wx.ALL | wx.ALIGN_RIGHT, 5)
#
#         btnPanel.SetSizer(btnSizer)
#         # End of Button Toolbar
#
#         mainSizer = wx.BoxSizer(wx.VERTICAL)
#         mainSizer.Add(contextPanel, 1, flag=wx.EXPAND)
#         mainSizer.Add(btnPanel, flag=wx.EXPAND)
#         self.SetSizer(mainSizer)
#         self.Fit()
#         self.CenterOnScreen()
#
#         # # Uncomment line below when testing as a standalone application.
#         # self.LoadDefaultValues()
#         # self.Show(True)
#
#     def LoadDefaultValues(self):
#         """Load Configurations To Dialog"""
#         readConfigFile()
#
#     def OnClose(self, event):
#         self.Show(False)
#
#     def OnOK(self, event):
#         try:
#             self.Show(False)
#
#             # processBar = ProgressBarDialog("Update Intersection Manager Tables")
#             # processBar.UpdateContents(10,"Initializing task...")
#
#             from src.int3_update_intersection import update_intersection_tables, check_intersection_tables_updates
#             from src.util.meta import read_im_meta_data, write_im_meta_data
#             from src.odot.ohio_dot_update import custom_update_odot
#             from src.roll_back_changes_since_date import roll_back
#
#             # Input
#             workspace = Config.get(SECTION, "workspace")
#             meta_date_dict = read_im_meta_data(workspace)
#             create_date = meta_date_dict["create_date"]
#             last_update_date =  meta_date_dict["last_update_date"]
#             today_date = truncate_datetime(datetime.now())
#
#             if  last_update_date == today_date:
#                 # If the last_update_date is today, we will have to roll back the changes to the src tables
#                 # we have made today and also set the last_update_date to one day before to mimic the src related
#                 # events are all created yesterday. This is a workaround since the date in the network is the only
#                 # indicator we can use the differentiate the new and old features
#                 roll_back(workspace, last_update_date)
#                 last_update_date = last_update_date - timedelta(days=1)
#             elif last_update_date is None:
#                 last_update_date = create_date - timedelta(days=1)
#
#             if check_intersection_tables_updates(workspace, last_update_date):
#                 msg_dlg= wx.MessageDialog(None,"Changed have been made since %s. Do you want to update src tables?" % last_update_date,
#                                           "Update Intersections Info", wx.OK | wx.ICON_INFORMATION)
#                 msg_dlg.ShowModal()
#
#                 update_intersection_tables(workspace, last_update_date)
#                 custom_update_odot(workspace, today_date)
#                 write_im_meta_data(workspace, None, today_date)
#             else:
#                 msg_dlg= wx.MessageDialog(None,"No changed have been made since %s" % last_update_date,
#                                           "Update Intersections Info", wx.OK | wx.ICON_INFORMATION)
#                 msg_dlg.ShowModal()
#                 msg_dlg.Destroy()
#
#                 data = [["1","11",""],["2","22",""],["3","33",""]]
#                 col_name = ["Object ID","Current Intersection ID", "New Intersection ID"]
#
#                 TableDialog("Update Itersection Info",data,3,3,col_name)
#
#                 # processBar.UpdateContents(100,"Done!")
#
#             # processBar.UpdateNotification("Done!")
#
#         except Exception as ex:
#             wx.MessageBox(ex.args[0], caption="Error", style=wx.OK | wx.ICON_ERROR)
#
# class SetViewDate(wx.Frame):
#     def __init__(self):
#         wx.Frame.__init__(self, None, wx.ID_ANY, title="Set View Date",
#                           style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
#         self.SetIcon(wx.Icon(os.path.join(get_parent_directory(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))
#         self.MinSize = 500, 400
#         self.MaxSize = 600, 600
#         self.Bind(wx.EVT_CLOSE, self.OnClose)
#
#         # Content Section
#         contentPanel = scrolled.ScrolledPanel(self, wx.ID_ANY, style=wx.SUNKEN_BORDER)
#         contentSizer = wx.BoxSizer(wx.VERTICAL)
#
#         self.dateTime = DateTimeInputGroup(contentPanel, -1, "Date", topFrame=self)
#
#         self.dateTime.inputText.SetValue(truncate_datetime(datetime.now()).strftime("%Y-%m-%d"))
#
#         self.inputs = [
#             self.dateTime
#         ]
#
#         for input in self.inputs:
#             contentSizer.Add(input, 0, wx.ALL | wx.EXPAND, 5)
#
#         contentPanel.SetSizer(contentSizer)
#         contentPanel.SetupScrolling()
#         contentPanel.Fit()
#         # End of content Section
#
#         # Button Toolbar
#         btnPanel = wx.Panel(self, -1, size=(400, 40))
#
#         okBtn = wx.Button(btnPanel, wx.ID_OK, 'Ok')
#         closeBtn = wx.Button(btnPanel, wx.ID_CANCEL, 'Cancel')
#         self.Bind(wx.EVT_BUTTON, self.OnOK, okBtn)
#         self.Bind(wx.EVT_BUTTON, self.OnClose, closeBtn)
#
#         btnSizer = wx.BoxSizer(wx.HORIZONTAL)
#         btnSizer.Add(okBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
#         btnSizer.Add(closeBtn, 0, wx.ALL | wx.ALIGN_BOTTOM, 5)
#
#         btnPanel.SetSizer(btnSizer)
#         # End of Button Toolbar
#
#         mainSizer = wx.BoxSizer(wx.VERTICAL)
#         mainSizer.Add(contentPanel, 1, flag=wx.EXPAND)
#         mainSizer.Add(btnPanel, flag=wx.EXPAND)
#         self.SetSizer(mainSizer)
#         self.Fit()
#         self.CenterOnScreen()
#
#         # # Uncomment line below when testing as a standalone application.
#         # self.LoadDefaultValues()
#         # self.Show(True)
#
#     # End __init__ built-in
#
#     def LoadDefaultValues(self):
#         """Load Configurations To Dialog"""
#         readConfigFile()
#
#     def OnClose(self, event):
#         """Close the frame. Do not use destroy."""
#         self.Show(False)
#         self.Close()
#
#     # End OnClose event method
#
#     def OnOK(self, event):
#         """Close the frame. Do not use destroy."""
#         try:
#             self.Show(False)
#
#             from src.config.schema import default_schemas
#             from src.tss import format_sql_date
#             parameters = get_default_parameters()
#
#             schemas = default_schemas.get("Default")
#             dbtype = parameters.get("Default", "dbtype")
#
#             from_date_field = schemas.get("from_date_field")
#             to_date_field = schemas.get("to_date_field")
#             intersection_event = schemas.get("intersection_event")
#             intersection_route_event = schemas.get("intersection_route_event")
#             roadway_segment_event = schemas.get("roadway_segment_event")
#             intersection_approach_event = schemas.get("intersection_approach_event")
#             view_date = self.dateTime.inputText.GetValue() or truncate_datetime(datetime.now())
#             view_date_query_string = format_sql_date(view_date, dbtype)
#             mxd = arcpy.mapping.MapDocument("CURRENT")
#             tba_items = arcpy.mapping.ListLayers(mxd) + arcpy.mapping.ListTableViews(mxd)
#
#             for item in tba_items:
#                 if item.name in [intersection_event, intersection_route_event, roadway_segment_event, intersection_approach_event]:
#                     item.definitionQuery = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(from_date_field, to_date_field, view_date_query_string)
#
#             arcpy.RefreshActiveView()
#             del mxd
#
#             self.Show(True)
#
#         except Exception as ex:
#             wx.MessageBox(ex.args[0], caption="Error", style=wx.OK | wx.ICON_ERROR)
#
#     # End OnOK event method
#
# # Uncomment code below to test as standalone application.
# app = wx.App(False)
# frame = ConfigurationDialog()
# app.MainLoop()