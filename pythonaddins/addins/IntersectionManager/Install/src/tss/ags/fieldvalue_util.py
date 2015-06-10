import arcpy

def get_maximum_id(dataset, id_field):
    # the id field need to be an integer field, or at least be filled with integer value
    max_id = 0
    with arcpy.da.SearchCursor(dataset, id_field) as sCursor:
        for sRow in sCursor:
            try:
                # Convert possible string to id
                id = int(sRow[0])
            except TypeError:
                continue
            max_id = max(id, max_id)
    return max_id


def get_minimum_value(dataset, field, where_clause):
    sCursor = arcpy.SearchCursor(dataset, where_clause, "", "", "%s A" % field)
    sRow = sCursor.next()
    del sCursor
    return sRow.getValue(field)


def populate_auto_increment_id(input_data, id_field, existing_max_id=0):
    with arcpy.da.UpdateCursor(input_data, id_field, "%s is NULL" % id_field) as uCursor:
        for uRow in uCursor:
            existing_max_id += 1
            uRow[0] = existing_max_id
            uCursor.updateRow(uRow)