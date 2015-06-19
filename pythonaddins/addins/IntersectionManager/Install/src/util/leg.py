import arcpy
from collections import OrderedDict

def determine_leg_type(dict):
    leg_id_type_dict = {}
    value_list = list(set(dict.values()))
    for key in dict.keys():
        if len(value_list) == 1:
            leg_id_type_dict[key] = "Major"
        else:
            if dict[key] == max(value_list):
                leg_id_type_dict[key] = "Major"
            else:
                leg_id_type_dict[key] = "Minor"
    return leg_id_type_dict


def calculate_leg_type_property(seg_value_dict, fc_key_name="function_class", aadt_key_name="aadt"):
    # Calculate the LegType and append it to the value_dict
    # {"function_class": 7}  =>  {"function_class":7, "Leg_Type": "Major"}
    # The major leg should have the lower functional_class, then higher aadt
    fc_value_list = [value_dict.get(fc_key_name) or '999' for value_dict in seg_value_dict.values()]
    min_fc_value = min(fc_value_list)
    aadt_value_list = [value_dict.get(aadt_key_name) or -1 for value_dict in seg_value_dict.values()]
    max_aadt_value = max(aadt_value_list)
    if fc_value_list.count(min_fc_value)  == 1:
        # Only one leg has the smallest fc, all the others will become minor
        for segment_id, value_dict in seg_value_dict.items():
            if value_dict.get(fc_key_name) == min_fc_value:
                value_dict['Leg_Type'] = "Major"
            else:
                value_dict['Leg_Type'] = "Minor"
    elif max_aadt_value != -1:
        # Need to use aadt as additional value to determine the major leg
        for segment_id, value_dict in seg_value_dict.items():
            if value_dict.get(fc_key_name) == min_fc_value and value_dict.get(aadt_key_name) == max_aadt_value:
                value_dict['Leg_Type'] = "Major"
            else:
                value_dict['Leg_Type'] = "Minor"
    elif min_fc_value != 999:
        # If no one single lowest functional_class exist and there are no aadt
        # Assign all the leg = min_fc_value with "Major"
        for segment_id, value_dict in seg_value_dict.items():
            if value_dict.get(fc_key_name) == min_fc_value:
                value_dict['Leg_Type'] = "Major"
            else:
                value_dict['Leg_Type'] = "Minor"
    else:
        # no function_class or addt exist for the intersection
        for segment_id, value_dict in seg_value_dict.items():
            value_dict['Leg_Type'] = None


def populate_leg_id_by_intersection(input_data, intersection_id_field, segment_id_field, leg_id_field, sort_field):
    inter__value_dict = {}
    with arcpy.da.SearchCursor(input_data, [intersection_id_field, segment_id_field, sort_field]) as sCursor:
        for sRow in sCursor:
            intersection_id, segment_id, sort_value = sRow[0], sRow[1], sRow[2]
            if intersection_id not in inter__value_dict:
                inter__value_dict[intersection_id] = {}
            inter__value_dict[intersection_id][segment_id] = sort_value
    # sort the value_list for each intersection
    for intersection_id in inter__value_dict.keys():
        sort_value_dict = inter__value_dict[intersection_id]
        inter__value_dict[intersection_id] = OrderedDict(sorted(sort_value_dict.items(), key=lambda x: x[1]))
    with arcpy.da.UpdateCursor(input_data, [intersection_id_field, segment_id_field, leg_id_field]) as uCursor:
        for uRow in uCursor:
            intersection_id, segment_id = uRow[0], uRow[1]
            uRow[2] = inter__value_dict[intersection_id].keys().index(segment_id) + 1
            uCursor.updateRow(uRow)
