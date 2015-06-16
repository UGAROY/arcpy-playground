import arcpy

def build_numeric_in_sql_expression(field_name, value_list):
    return "%s in (%s)" % (field_name, ",".join(str(value) for value in value_list)) if len(value_list) > 0 else "1=2"


def build_string_in_sql_expression(field_name, value_list):
    return "%s in (%s)" % (field_name, ",".join("'" + value + "'" for value in value_list)) if len(value_list) > 0 else "1=2"

def subset_data_exist(data, where_clause):
    with arcpy.da.SearchCursor(data, "OID@", where_clause) as sCursor:
        try:
            sCursor.next()
            return True
        except StopIteration:
            return False

def delete_subset_data(data, where_clause):
    with arcpy.da.UpdateCursor(data, "OID@", where_clause) as uCursor:
        for uRow in uCursor:
            uCursor.deleteRow()

def delete_identical_only_keep_min_oid(data, fields, xy_tolerance="1 meters"):
    identical_table = "in_memory\\identical_table"
    arcpy.FindIdentical_management(data, identical_table, fields, xy_tolerance, "", "ONLY_DUPLICATES")
    fseq_list = []
    delete_oid_list = []
    sCursor = arcpy.SearchCursor(identical_table, "", "", "FEAT_SEQ;IN_FID", "IN_FID A")
    for sRow in sCursor:
        feat_seq, in_fid = sRow.getValue("FEAT_SEQ"), sRow.getValue("IN_FID")
        if feat_seq not in fseq_list:
            fseq_list.append(feat_seq)
        else:
            delete_oid_list.append(in_fid)
    del sCursor
    oid_field = arcpy.Describe(data).OIDFieldName
    if len(delete_oid_list) != 0:
        where_clause = build_numeric_in_sql_expression(oid_field, delete_oid_list)
        delete_subset_data(data, where_clause)