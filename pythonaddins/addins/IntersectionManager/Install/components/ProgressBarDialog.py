import wx
import os

class ProgressBarDialog(wx.Frame):

    def __init__(self, inputLabel="Processing Task"):

        wx.Frame.__init__(self, None, wx.ID_ANY, title=inputLabel, style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))

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

    # def OnOK(self, event):
    #     """ """
    #     self.Destroy()

    def OnClose(self, event):
        """ """
        #TODO: dialog won't close in ArcMap. Figure out why.
        event.Skip()
        self.Destroy()
        # self.Close()

    # Issue: process bar will not refresh intermediately after calling SetValue(). Figure out why. Consider the
    #        tips before this issue got fixed.
    # Tips: when calling these functions, consider value as the percentage of completeness after the process of notification
    #       finished.
    def UpdateProcessBar(self, value):
        self.gauge.SetValue(value)
        wx.Yield()

    def UpdateNotification(self, value):
        self.label.SetLabel(str(value))
        wx.Yield()

    def UpdateContents(self, value, notification):
        self.gauge.SetValue(value)
        self.label.SetLabel(str(notification))
        wx.Yield()
