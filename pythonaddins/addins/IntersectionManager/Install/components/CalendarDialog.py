import wx
import os

from datetime import datetime
import wx.lib.masked as masked
import wx.calendar as calendar

class CalendarDialog(wx.Dialog):
    def __init__(self, inputLabel="Date"):
        """Initialize the Frame and add wx widgets."""
        wx.Dialog.__init__(self, None, wx.ID_ANY, title=inputLabel, style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), "img", "Tlogo.ico"), wx.BITMAP_TYPE_ICO))

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