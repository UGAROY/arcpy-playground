import math
import os
import arcpy
from collections import OrderedDict

# Variables
intersection_manager_inf = "Intersection_Manager_Metadata"


def calculate_approach_angle(segment, intersection, influence_distance, azumith_zero_direction):
    intersection_point = intersection.firstPoint
    if intersection.distanceTo(segment.firstPoint) < intersection.distanceTo(segment.lastPoint):
        next_point = segment.positionAlongLine(influence_distance).firstPoint
    else:
        next_point = segment.positionAlongLine(segment.length - influence_distance).firstPoint

    if azumith_zero_direction == "N":
        return angle_between_two_vectors((0, 1), (intersection_point.X - next_point.X, intersection_point.Y - next_point.Y))
    else:
        return angle_between_two_vectors((1, 0), (intersection_point.X - next_point.X, intersection_point.Y - next_point.Y))


def angle_between_two_vectors(vector1, vector2):
    vector11_sum = 0
    vector12_sum = 0
    vector22_sum = 0
    for i in range(len(vector1)):
        vector11_sum += vector1[i] ** 2
        vector12_sum += vector1[i] * vector2[i]
        vector22_sum += vector2[i] ** 2

    try:
        angle = math.acos(vector12_sum / math.sqrt(vector11_sum*vector22_sum)) * 180 / math.pi
    except ZeroDivisionError:
        return -1
    if angle_larger_than_pi(vector1, vector2):
        angle = 360 - angle
    return angle


def angle_larger_than_pi(vector1, vector2):
    # clockwise angle from vector1 to vector2
    return vector1[0] * vector2[1] - vector1[1] * vector2[0] > 0


# Convert angle to direction descriptor
def angle_to_direction(angle, azumith_zero_direction):
    if azumith_zero_direction == "E":
        angle = angle + 90 if angle <= 270 else angle + 90 - 360
    if angle >= 337.5 or angle < 22.5:
        return "North"
    elif 22.5 <= angle < 67.5:
        return "NorthEast"
    elif 67.5 <= angle < 112.5:
        return "East"
    elif 112.5 <= angle < 157.5:
        return "SouthEast"
    elif 157.5 <= angle < 202.5:
        return "South"
    elif 202.5 <= angle < 247.5:
        return "SouthWest"
    elif 247.5 <= angle < 292.5:
        return "West"
    else:
        return "NorthWest"

def geodesic_angle_to_circular_angle(angle):
    return angle if angle > 0 else angle + 360

def geodesic_angle_to_direction(angle):
    if -22.5 < angle <=22.5:
        return "North"
    elif 22.5 < angle <= 67.5:
        return "NorthEast"
    elif 67.5 < angle <= 112.5:
        return "East"
    elif 112.5 < angle <= 157.5:
        return "SouthEast"
    elif angle > 157.5 or angle <= -157.5:
        return "South"
    elif -157.5 < angle <= -112.5:
        return "SouthWest"
    elif -112.5 < angle <= -67.5:
        return "West"
    else:
        return "NorthWest"



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


# def append_leg_type_property(seg_value_dict_list, value_key_name="Value"):
#     value_list = [seg_value_dict.get(value_key_name) for seg_value_dict in seg_value_dict_list]
#     for seg_value_dict in seg_value_dict_list:
#         if len(value_list) == 1:
#             seg_value_dict["Leg_Type"] = "Major"
#         else:
#             if seg_value_dict["Value"] is None:
#                 seg_value_dict["Leg_Type"] = None
#             elif seg_value_dict["Value"] == max(value_list):
#                 seg_value_dict["Leg_Type"] = "Major"
#             else:
#                 seg_value_dict["Leg_Type"] = "Minor"


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

if __name__ == "__main__":
    angle = angle_between_two_vectors((0, 1), (-1, -1))
    assert angle == 225