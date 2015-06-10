import arcpy

from pythonaddins.addins.IntersectionManager.Install.src.odot.ohio_dot_util import calculate_latitude_longitude, calculate_county_jurisdiction_district, calculate_intersection_geometry
from tss import keep_fields_fms
from pythonaddins.addins.IntersectionManager.Install.src.config.schema import default_schemas


def custom_create_odot(workspace):
    """
     Post-processing script for ODOT customization
    """
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    schemas = default_schemas.get("Default")

    # Input and Configurations ----------------------------------------------------------
    intersection_event = schemas.get("intersection_event")
    intersection_id_field = schemas.get("intersection_id_field")
    # -------------------------------------------------------------------------------------

    # Output --------------------------------------------------------------------------
    intersection_table = "Intersection_Table"
    latitude_field = "Latitude"
    longitude_field = "Longitude"
    county_code_field = "CountyCd"
    district_code_field = "DistrictCd"
    jurisdiction_name_field = "JurisdictionName"
    intersection_geometry_field = "Intersection_Geometry"
    # ---------------------------------------------------------------------------------

    # Create a copy of the intersection_event with only the intersection_id
    arcpy.TableToTable_conversion(intersection_event, workspace, intersection_table, "", keep_fields_fms(intersection_event, [intersection_id_field]))

    # Add Latitude and Longitude
    arcpy.AddField_management(intersection_table, longitude_field, "DOUBLE")
    arcpy.AddField_management(intersection_table, latitude_field, "DOUBLE")
    calculate_latitude_longitude(intersection_event, intersection_table)

    # Add County and Jurisdiction Name
    arcpy.AddField_management(intersection_table, county_code_field, "TEXT", "#", "#", 3)
    arcpy.AddField_management(intersection_table, jurisdiction_name_field, "TEXT", "#", "#", 1)
    arcpy.AddField_management(intersection_table, district_code_field, "LONG")
    calculate_county_jurisdiction_district(intersection_table)

    # Add Intersection Geometry
    arcpy.AddField_management(intersection_table, intersection_geometry_field, "SHORT")
    calculate_intersection_geometry(intersection_table)

if __name__ == "__main__":
    workspace = r'C:\Projects\ODOT\Data\Raw.gdb'
    custom_create_odot(workspace)