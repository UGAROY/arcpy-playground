import arcpy

def get_maximum_id(dataset, id_field):
    # the id field need to be an integer field, or at least be filled with integer value
    """
    Get maximum id in the current dataset. The id field needs to be a numeric value. If not, it will be converted to
    int first, and then returns the maximum number.
    :param dataset:
    :param id_field:
    :return:
    """
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
    """
    Return the maximum value based on the where clause
    :param dataset:
    :param field:
    :param where_clause:
    :return:
    """
    sCursor = arcpy.SearchCursor(dataset, where_clause, "", "", "%s A" % field)
    sRow = sCursor.next()
    del sCursor
    return sRow.getValue(field)


def populate_auto_increment_id(input_data, id_field, existing_max_id=0):
    """
    Automatically increment the id by 1 based on the existing maximum id
    :param input_data:
    :param id_field:
    :param existing_max_id:
    """
    with arcpy.da.UpdateCursor(input_data, id_field, "%s is NULL" % id_field) as uCursor:
        for uRow in uCursor:
            existing_max_id += 1
            uRow[0] = existing_max_id
            uCursor.updateRow(uRow)