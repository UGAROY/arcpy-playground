import arcpy
from tss_util import build_string_in_sql_expression
from schema import default_schemas


# Source Data -------------------------------------------------------------------
schemas = default_schemas.get("Default")
intersection_id_field = schemas.get("intersection_id_field")
intersection_route_event = schemas.get("intersection_route_event")
intersection_route_on_rid_field = schemas.get("intersection_route_on_rid_field")
intersection_approach_event = schemas.get("intersection_approach_event")
intersection_approach_angle_field = schemas.get("intersection_approach_angle_field")
district = "District"
district_id_field = "D_DISTRICT_ID"
district_rid_field = "ROUTE_ID"


# Output --------------------------------------------------------------------------
latitude_field = "Latitude"
longitude_field = "Longitude"
county_code_field = "CountyCd"
district_code_field = "DistrictCd"
jurisdiction_name_field = "JurisdictionName"
intersection_geometry_field = "Intersection_Geometry"

# Intermediate data ----------------------------------------------------------------
intersection_event_proj = "intersection_event_proj"
intersection_approach_event_freq = "intersection_approach_event_freq"

def calculate_latitude_longitude(intersection_event_layer, intersection_table, intersection_id_list=None):
    intersection_id_where_clause = build_string_in_sql_expression(intersection_id_field, intersection_id_list) if intersection_id_list else "1=1"

    arcpy.Project_management(intersection_event_layer, intersection_event_proj, arcpy.SpatialReference(4326))
    arcpy.AddXY_management(intersection_event_proj)
    inter_xy_dict = {}
    with arcpy.da.SearchCursor(intersection_event_proj, [intersection_id_field, "POINT_X", "POINT_Y"]) as sCursor:
        for sRow in sCursor:
            intersection_id, longitude, latitude = sRow[0], sRow[1], sRow[2]
            inter_xy_dict[intersection_id] = {"Longitude": longitude, "Latitude": latitude}
    with arcpy.da.UpdateCursor(intersection_table, [intersection_id_field, longitude_field, latitude_field], intersection_id_where_clause) as uCursor:
        for uRow in uCursor:
            intersection_id = uRow[0]
            uRow[1] = inter_xy_dict[intersection_id]["Longitude"]
            uRow[2] = inter_xy_dict[intersection_id]["Latitude"]
            uCursor.updateRow(uRow)
    arcpy.Delete_management(intersection_event_proj)

def calculate_county_jurisdiction_district(intersection_table, intersection_id_list=None):
    intersection_id_where_clause = build_string_in_sql_expression(intersection_id_field, intersection_id_list) if intersection_id_list else "1=1"

    # Calculate county and jurisdiction name
    inter_route_dict = {}
    with arcpy.da.SearchCursor(intersection_route_event, [intersection_id_field, intersection_route_on_rid_field],
                               intersection_id_where_clause) as sCursor:
        for sRow in sCursor:
            intersection_id, route_id = sRow[0], sRow[1]
            if intersection_id not in inter_route_dict:
                inter_route_dict[intersection_id] = route_id
    with arcpy.da.UpdateCursor(intersection_table, [intersection_id_field, county_code_field, jurisdiction_name_field], intersection_id_where_clause) as uCursor:
        for uRow in uCursor:
            intersection_id = uRow[0]
            try:
                route_id = inter_route_dict[intersection_id]
                uRow[1] = route_id[1:4]
                uRow[2] = route_id[0]
                uCursor.updateRow(uRow)
            except KeyError:
                continue

    # Calculate District
    route_district_dict = {}
    with arcpy.da.SearchCursor(district, [district_id_field, district_rid_field]) as sCursor:
        for sRow in sCursor:
            district_id, district_rid = sRow[0], sRow[1]
            if district_rid not in route_district_dict:
                route_district_dict[district_rid] = district_id
    with arcpy.da.UpdateCursor(intersection_table, [intersection_id_field, district_code_field], intersection_id_where_clause) as uCursor:
        for uRow in uCursor:
            intersection_id = uRow[0]
            try:
                route_id = inter_route_dict[intersection_id]
                uRow[1] = route_district_dict[route_id]
                uCursor.updateRow(uRow)
            except KeyError:
                continue

def calculate_intersection_geometry(intersection_table, intersection_id_list=None):
    intersection_id_where_clause = build_string_in_sql_expression(intersection_id_field, intersection_id_list) if intersection_id_list else "1=1"

    arcpy.Frequency_analysis(intersection_approach_event, intersection_approach_event_freq, "%s;%s" % (intersection_id_field, intersection_approach_angle_field))
    inter_count_dict = {}
    with arcpy.da.SearchCursor(intersection_approach_event_freq, [intersection_id_field], intersection_id_where_clause) as sCursor:
        for sRow in sCursor:
            intersection_id = sRow[0]
            inter_count_dict[intersection_id] = inter_count_dict.get(intersection_id, 0) + 1
    with arcpy.da.UpdateCursor(intersection_table, [intersection_id_field, intersection_geometry_field], intersection_id_where_clause) as uCursor:
        for uRow in uCursor:
            intersection_id = uRow[0]
            uRow[1] = inter_count_dict[intersection_id]
            uCursor.updateRow(uRow)
