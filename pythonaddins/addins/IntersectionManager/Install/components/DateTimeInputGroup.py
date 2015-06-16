import wx
import os
from CalendarDialog import CalendarDialog

class DateTimeInputGroup(wx.Panel):
    def __init__(self, parent, ID=-1, inputLabel="", topFrame=None):
        self.topFrame = topFrame
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.TextCtrl(self, wx.ID_ANY)
        png = wx.Image(os.path.join(os.path.dirname(__file__), "img", "Calendar.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
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