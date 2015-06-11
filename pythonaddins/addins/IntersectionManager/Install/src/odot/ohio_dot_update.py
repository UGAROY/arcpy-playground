from datetime import  datetime

import arcpy

from ohio_dot_util import calculate_latitude_longitude, calculate_county_jurisdiction_district, calculate_intersection_geometry
from ..config.schema import default_schemas
from ..tss import format_sql_date, build_string_in_sql_expression, delete_identical_only_keep_min_oid, delete_subset_data
from ..util.helper import get_default_parameters

default_parameters = get_default_parameters()

def custom_update_odot(workspace, date):
    """
     Post-processing script for ODOT customization
    """
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    client = "Default"
    parameters = get_default_parameters()
    schemas = default_schemas.get(client)

    dbtype = parameters.get(client,"dbtype")

    # Input and Configurations ----------------------------------------------------------
    intersection_event = schemas.get("intersection_event")
    intersection_id_field = schemas.get("intersection_id_field")

    intersection_approach_event = schemas.get("intersection_approach_event")

    date_string = format_sql_date(date, dbtype)
    from_date_field = schemas.get("from_date_field")
    last_date_field = schemas.get("to_date_field")

    intersection_table = "Intersection_Table"
    # -------------------------------------------------------------------------------------

    # Import Parameters ------------------------------------------------------------------
    created_query_string = "{0} = {1}".format(from_date_field, date_string)
    retired_query_string = "{0} = {1}".format(last_date_field, date_string)
    created_retired_query_string = "{0} = {2} or {1} = {2}".format(from_date_field, last_date_field, date_string)
    tba_new_intersection_ids = []
    tba_update_intersection_ids = []
    # -----------------------------------------------------------------------------------

    # Intermediate data ----------------------------------------------------------------
    tba_new_intersection_event_layer = "tba_new_intersection_event_layer"
    tba_update_intersection_event_layer = "tba_update_intersection_event_layer"
    #-----------------------------------------------------------------------------------

    # Find the records that need to be updated 1) new intersections 2) intersections with leg number updated
    with arcpy.da.SearchCursor(intersection_event, [intersection_id_field],
                               created_query_string) as sCursor:
        tba_new_intersection_ids = [sRow[0] for sRow in sCursor]
    with arcpy.da.SearchCursor(intersection_approach_event, [intersection_id_field],
                               created_retired_query_string) as sCursor:
        for sRow in sCursor:
            intersection_id = sRow[0]
            if intersection_id not in tba_update_intersection_ids:
                tba_update_intersection_ids.append(intersection_id)

    tba_new_intersection_where_clause = build_string_in_sql_expression(intersection_id_field, tba_new_intersection_ids)
    arcpy.MakeFeatureLayer_management(intersection_event, tba_new_intersection_event_layer,tba_new_intersection_where_clause)
    tba_update_intersection_where_clause = build_string_in_sql_expression(intersection_id_field, tba_update_intersection_ids)
    arcpy.MakeFeatureLayer_management(intersection_event, tba_update_intersection_event_layer, tba_update_intersection_where_clause)

    # Add new src records to intersection_table
    with arcpy.da.InsertCursor(intersection_table, intersection_id_field) as iCursor:
        for intersection_id in tba_new_intersection_ids:
            iCursor.insertRow((intersection_id,))
    delete_identical_only_keep_min_oid(intersection_table, [intersection_id_field])

    # Calculate Latitude and Longitude
    calculate_latitude_longitude(tba_new_intersection_event_layer, intersection_table, tba_new_intersection_ids)

    # Calculate County and Jurisdiction Name
    calculate_county_jurisdiction_district(intersection_table, tba_new_intersection_ids)

    # Calculate Intersection Geometry
    calculate_intersection_geometry(intersection_table, tba_update_intersection_ids)

    # Find the retired intersections and retire them in intersection_table
    with arcpy.da.SearchCursor(intersection_event, [intersection_id_field], retired_query_string) as sCursor:
        retired_intersection_ids = [sRow[0] for sRow in sCursor]
    retired_intersection_id_where_clause = build_string_in_sql_expression(intersection_id_field, retired_intersection_ids)
    arcpy.AddMessage(retired_intersection_id_where_clause)
    delete_subset_data(intersection_table, retired_intersection_id_where_clause)

if __name__ == "__main__":
    workspace = r'C:\Projects\ODOT\Data\Raw.gdb'
    date = datetime.now()
    custom_update_odot(workspace, date)