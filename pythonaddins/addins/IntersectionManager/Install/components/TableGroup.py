import wx
import wx.grid as gridlib
from src.util.map import zoom_to_selected_features


class TableGroup(wx.Panel):
    """
    @:parameters
    data: data array, example: [[value1,value2,value3...],[value_x,value_y,value_z...],[...]]
    rowLabels: array, example: [name1,name2,name3...]
    colLabels: array, example: [name1,name2,name3...]
    """
    def __init__(self, parent, data, rowLabels=None, colLabels=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)

        # UI
        self.data = data
        # self.row_labels = rowLabels
        # self.col_labels = colLabels

        self.myGrid = gridlib.Grid(self, wx.ID_ANY)
        self.myGrid.EnableDragGridSize()
        self.myGrid.SetRowLabelSize(0)
        self.myGrid.SetLabelFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        # self.myGrid.CreateGrid(rowNum, colNum, selmode=wx.grid.Grid.SelectRows)
        self.tableBase = TableBase(data,colLabels=colLabels)
        self.myGrid.SetTable(self.tableBase,selmode=wx.grid.Grid.SelectRows)

        self.myGrid.AutoSize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.myGrid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()

        # Event binding
        self.myGrid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.ShowPopupMenu)

    def ClearEdits(self, colName):
        pos = None
        for i in range(0, self.myGrid.GetNumberCols()):
            if self.myGrid.GetColLabelValue(i) == colName:
                pos = i
        if pos:
            for i in range(0, self.myGrid.GetNumberRows()):
                self.myGrid.SetCellValue(i, pos, "")

    def ClearTable(self):
        self.tableBase.ClearTable()
        self.data = self.tableBase.data
        self.myGrid.ForceRefresh()

    def PopulateTable(self,data):
        # self.data = data
        self.tableBase.PopulateTable(data)
        self.data = self.tableBase.data
        self.myGrid.ForceRefresh()

    def ShowPopupMenu(self, event):
        """
        Create and display a popup menu on right-click event
        """
        row = event.GetRow()
        self.myGrid.SelectRow(row, False)
        self.myGrid.Refresh()

        self.popupID1 = wx.NewId()
        self.menu = wx.Menu()

        # Show how to put an icon in the menu
        item = wx.MenuItem(self.menu, self.popupID1, "Zoom to Intersection")
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.menu.AppendItem(item)

        # Popup the menu.  If an item is selected then its handler will be called before PopupMenu returns.
        self.PopupMenu(self.menu)
        self.menu.Destroy()

    def OnPopupItemSelected(self, event):
        row = self.myGrid.GetSelectedRows()
        oid = self.myGrid.GetCellValue(row[0], 0)

        layer_name = "new_created_intersections"
        where_clause = "OBJECTID =" + oid
        self.ZoomToSelectedFeature(layer_name, where_clause)

    def ZoomToSelectedFeature(self, layer_name, where_clause):
        zoom_to_selected_features(layer_name, where_clause)

    def GetUpdatedData(self):
        dictionary = {}
        row_num =self.myGrid.GetNumberRows()

        for i in range(0,row_num):
            oid = self.myGrid.GetCellValue(i,0)
            value = self.myGrid.GetCellValue(i,2)

            if value and (not value.isspace()):
                dictionary[oid] = value

        return dictionary

        # if len(dictionary):
        #     return dictionary
        # else:
        #     return None

    @property
    def value(self):
        return self.data


class TableBase(wx.grid.PyGridTableBase):
    def __init__(self,data,rowLabels=None,colLabels=None):
        wx.grid.PyGridTableBase.__init__(self)

        self.data = data
        self.rowLabels = rowLabels
        self.colLabels = colLabels

        # Set fonts
        self.odd=wx.grid.GridCellAttr()
        self.odd.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.even=wx.grid.GridCellAttr()
        self.even.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.colLabels)

    def GetRowLabelValue(self, row):
        if self.rowLabels:
            return self.rowLabels[row]

    def GetColLabelValue(self, col):
        if self.colLabels:
            return self.colLabels[col]

    def IsEmptyCell(self, row, col):
        return self.data[row][col] is not None

    def GetValue(self, row, col):
        return self.data[row][col]

    def SetValue(self, row, col, value):
        if value is not None:
            self.data[row][col] = value
        else:
            self.data[row][col] = ""

    def ClearTable(self):
        # Begin clearing the whole table
        self.GetView().BeginBatch()

        # Delete all rows. Run it only to keep column headers.
        msg = gridlib.GridTableMessage(self,gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED,0,self.GetNumberRows())
        self.GetView().ProcessTableMessage(msg)

        # Delete all cols. Run it to delete all rows and column headers.
        # msg = gridlib.GridTableMessage(self,gridlib.GRIDTABLE_NOTIFY_COLS_DELETED,0,self.GetNumberCols())
        # self.GetView().ProcessTableMessage(msg)

        self.GetView().EndBatch()
        # End clearing process

        # Update table view
        self.data = []

        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.GetView().ProcessTableMessage(msg)

    def PopulateTable(self, data):
        self.ClearTable()
        self.data = data

        self.GetView().BeginBatch()
        msg = gridlib.GridTableMessage(self,gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED,self.GetNumberRows())
        self.GetView().ProcessTableMessage(msg)
        self.GetView().EndBatch()

        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.GetView().ProcessTableMessage(msg)