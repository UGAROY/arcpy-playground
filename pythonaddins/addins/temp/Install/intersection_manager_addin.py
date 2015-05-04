import arcpy
import pythonaddins

import wx



class ButtonClass1(object):
    """Implementation for intersection_manager_addin.button (Button)"""

    dlg = None
    
    def __init__(self):
        self.enabled = True
        self.checked = False
        
    def onClick(self):
        if self.dlg is None:  
            self.dlg = TestDialog()  
        else:  
            self.dlg.Show(True)

class TestDialog(wx.Frame):  
    def __init__(self):  
        wxStyle = wx.CAPTION | wx.RESIZE_BORDER | wx.MINIMIZE_BOX |wx.CLOSE_BOX | wx.SYSTEM_MENU  
        wx.Frame.__init__(self, None, -1, "Set DataFrame Name", style=wxStyle, size=(300, 120))  
        self.SetMaxSize((300, 120))  
        self.SetMinSize((300, 120))  
        self.Bind(wx.EVT_CLOSE, self.OnClose)  
        panel = wx.Panel(self, -1)  
        self.lblStatus = wx.StaticText(panel, -1, "OK", pos=(8, 8))  
        wx.StaticText(panel, -1, "Title:", pos=(8,36))  
        self.tbTitle = wx.TextCtrl(panel, -1, value="", pos=(36, 36), size=(200,21))  
        self.btnSet = wx.Button(panel, label="Set", pos=(8, 66))  
        self.Bind(wx.EVT_BUTTON, self.OnSet, id=self.btnSet.GetId())  
        self.Show(True)  
          
    def OnClose(self, event):  
        self.Show(False) # self.Destroy() doesn't work  
  
    def OnSet(self, event):  
        # Use str() to strip away Unicode crap  
        # sTitle = str(self.tbTitle.GetValue())
        # mxd = arcpy.mapping.MapDocument("CURRENT")
        # df = mxd.activeDataFrame
        # df.name = sTitle
        # arcpy.RefreshTOC()
        a = pythonaddins.OpenDialog('Select Layers', True, r'C:\GISData', 'Add')
        with open(r'C:\Projects\VDOT\a.text', 'w') as f:
            f.write("JAJA")
            f.write(str(a))

  
app = wx.PySimpleApp()  
app.MainLoop()  
