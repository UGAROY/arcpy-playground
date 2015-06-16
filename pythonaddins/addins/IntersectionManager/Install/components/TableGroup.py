import wx
import wx.grid as gridlib

class TableGroup(wx.Panel):
    """
    @:parameters
    data: data array, example: [[value1,value2,value3...],[value_x,value_y,value_z...],[...]]
    rowNum, colNum: int
    colName: array, example: [name1,name2,name3...]
    """
    def __init__(self, parent, data, rowNum, colNum, colNames):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.data = data

        self.myGrid = gridlib.Grid(self, wx.ID_ANY)
        self.myGrid.CreateGrid(rowNum, colNum, selmode=wx.grid.Grid.SelectRows)
        self.myGrid.EnableDragGridSize()
        self.myGrid.SetRowLabelSize(0)
        self.myGrid.SetLabelFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        for i in range(0,colNum):
            self.myGrid.SetColLabelValue(i, colNames[i])
            self.myGrid.AutoSizeColLabelSize(i)

        for row in data:
            rid = data.index(row)
            for i in range(0,colNum):
                self.myGrid.SetCellValue(rid,i, str(row[i]))
                self.myGrid.SetCellFont(rid,i,wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.myGrid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()

        self.myGrid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.ShowPopupMenu)

    def ClearEdits(self,colName):
        pos = None
        for i in range(0,self.myGrid.GetNumberCols()):
            if self.myGrid.GetColLabelValue(i) == colName:
                pos = i
        if pos:
            for i in range(0,self.myGrid.GetNumberRows()):
                self.myGrid.SetCellValue(i,pos,"")

    def ShowPopupMenu(self, event):
        """
        Create and display a popup menu on right-click event
        """
        row = event.GetRow()
        self.myGrid.SelectRow(row,False)
        self.myGrid.Refresh()

        self.popupID1 = wx.NewId()
        self.menu = wx.Menu()

        # Show how to put an icon in the menu
        item = wx.MenuItem(self.menu, self.popupID1, "Zoom to Intersection")
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.menu.AppendItem(item)

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(self.menu)
        self.menu.Destroy()

    def OnPopupItemSelected(self, event):

        row = self.myGrid.GetSelectedRows()
        value = self.myGrid.GetCellValue(row[0],0)

        # layer_name = ""
        # where_clause = ""
        # zoom_to_selected_features(layer_name,where_clause)

        wx.MessageBox("You selected Row '%s'" % value)

    def ZoomToSelectedFeature(self,event):
        pass

    @property
    def value(self):
        return self.data

    # @value.setter
    # def value(self, value):
    #     pass