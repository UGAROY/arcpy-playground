import wx

class AgsProgressDialog(wx.ProgressDialog):

    def __init__(self, title, message):
        """ """
        wx.ProgressDialog.__init__(self, title, message, style=wx.PD_ELAPSED_TIME)

    def Exit(self, message):
        self.Update(100, message)