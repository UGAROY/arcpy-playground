import os
import arcpy

# Variables
intersection_manager_inf = "Intersection_Manager_Metadata"


def write_im_meta_data(outputGdb, create_date=None, update_date=None):
    meta_data_table = os.path.join(outputGdb, intersection_manager_inf)
    if create_date is not None:
        if arcpy.Exists(meta_data_table):
            arcpy.Delete_management(meta_data_table)
        arcpy.CreateTable_management(outputGdb, intersection_manager_inf)
        arcpy.AddField_management(meta_data_table, "create_date", "DATE")
        arcpy.AddField_management(meta_data_table, "last_update_date", "Date")
        with arcpy.da.InsertCursor(meta_data_table, ["create_date", "last_update_date"]) as iCursor:
            iCursor.insertRow((None, None))
    with arcpy.da.UpdateCursor(meta_data_table, ["create_date", "last_update_date"]) as uCursor:
        uRow = uCursor.next()
        if create_date is not None:
            uRow[0] = create_date
        if update_date is not None:
            uRow[1] = update_date
        uCursor.updateRow(uRow)

def read_im_meta_data(outputGdb):
    meta_data_table = os.path.join(outputGdb, intersection_manager_inf)
    if not arcpy.Exists(meta_data_table):
        return {"create_date": None, "last_update_date": None}
    with arcpy.da.SearchCursor(meta_data_table, ["create_date", "last_update_date"]) as sCursor:
        sRow = sCursor.next()
        create_update_date_dict = {"create_date": sRow[0], "last_update_date": sRow[1]}
    return create_update_date_dict