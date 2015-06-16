import arcpy

from src.util.helper import set_parameters

key_value_dict = {}
fields = ['workspace', 'network', 'network_route_id_field', 'network_route_name_field', 'network_from_date_field', 'network_to_date_field', 'intersection_filter_point', 'intersection_filter_from_date_field', 'intersection_filter_to_date_field', 'function_class_event', 'function_class_field', 'function_class_rid_field', 'function_class_from_meas_field', 'function_class_to_meas_field', 'function_class_from_date_field', 'function_class_to_date_field', 'aadt_event', 'aadt_field', 'aadt_rid_field', 'aadt_from_meas_field', 'aadt_to_meas_field', 'aadt_from_date_field', 'aadt_to_date_field', 'search_radius', 'angle_calculation_distance', 'area_of_influence', 'azumith_zero_direction', 'measure_scale', 'dbtype']

for index, value in enumerate(fields):
    key_value_dict[value] = arcpy.GetParameterAsText(index)

SECTION = "Default"
set_parameters(SECTION, key_value_dict)