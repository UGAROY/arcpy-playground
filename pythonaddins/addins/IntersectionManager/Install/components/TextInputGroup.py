import wx

class TextInputGroup(wx.Panel):
    def __init__(self, parent, ID=-1, inputLabel="", key=""):
        self.key = key
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.TextCtrl(self, wx.ID_ANY)
        inputGroupSizer.Add(inputLabel, pos=(0, 0))
        inputGroupSizer.Add(self.inputText, pos=(1, 0), flag=wx.EXPAND)
        inputGroupSizer.AddGrowableCol(0)

        self.SetSizer(inputGroupSizer)

    @property
    def value(self):
        return self.inputText.GetValue()

    @value.setter
    def value(self, value):
        self.inputText.SetValue(str(value))