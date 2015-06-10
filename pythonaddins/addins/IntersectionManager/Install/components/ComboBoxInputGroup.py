import wx

class ComboBoxInputGroup(wx.Panel):
    def __init__(self, parent, ID=-1, inputLabel="", options=None, key=""):
        self.key = key
        wx.Panel.__init__(self, parent, ID)

        inputGroupSizer = wx.GridBagSizer(hgap=5, vgap=5)
        inputLabel = wx.StaticText(self, wx.ID_ANY, inputLabel)
        self.inputText = wx.ComboBox(self, wx.ID_ANY, choices=options)
        inputGroupSizer.Add(inputLabel, pos=(0, 0))
        inputGroupSizer.Add(self.inputText, pos=(1, 0), flag=wx.EXPAND)
        inputGroupSizer.AddGrowableCol(0)

        self.SetSizer(inputGroupSizer)

    @property
    def value(self):
        return self.inputText.GetStringSelection()

    @value.setter
    def value(self, value):
        self.inputText.SetValue(str(value))