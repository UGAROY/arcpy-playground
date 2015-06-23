import arcpy
import os
from itertools import combinations
from dao_util import build_string_in_sql_expression

overlap_segments = "in_memory\\overlap_segments"
active_centerline_sequence_view = "active_centerline_sequence_view"
centerline_layer = "centerline_layer"
unsplit_centerline = "in_memory\\unsplit_centerline"


def extract_concurrent_segment_end_points_from_geometry(network, concurrent_segment_end_points):
    """

    :param network:
    :param concurrent_segment_end_points:
    """
    find_overlap_segments(network, overlap_segments)
    overlap_segments_to_concurrent_end_points(overlap_segments, concurrent_segment_end_points)


def extract_concurrent_segment_end_points_from_centerline(centerline, centerline_sequence, network_id_field, centerline_rid_field, network_id,
                                                          concurrent_segment_end_points):
    """

    :param centerline:
    :param centerline_sequence:
    :param network_id_field:
    :param centerline_rid_field:
    :param network_id:
    :param concurrent_segment_end_points:
    """
    find_overlap_segments_from_centerline(centerline, centerline_sequence, network_id_field, centerline_rid_field, network_id, overlap_segments)
    overlap_segments_to_concurrent_end_points(overlap_segments, concurrent_segment_end_points)


# Not Tested Yet
def find_overlap_segments_from_centerline(centerline, centerline_sequence, network_id_field, centerline_rid_field, network_id, overlap_segments):
    arcpy.MakeTableView_management(centerline_sequence, active_centerline_sequence_view, "%s = %s" % (network_id_field, network_id))
    roadway__count_dict = {}
    with arcpy.da.SearchCursor(active_centerline_sequence_view, "RoadwayIdGuid") as sCursor:
        for sRow in sCursor:
            roadway_guid = sRow[0]
            roadway__count_dict[roadway_guid] = roadway__count_dict.get(roadway_guid, 0) + 1
    concurrent_roadway_guids = [roadway_guid for roadway_guid, count in roadway__count_dict.items() if count >= 2]
    concurrent_roadway_guid_where_clause = build_string_in_sql_expression("RoadwayIdGuid", concurrent_roadway_guids)
    route__roadway_guids_dict = {}
    with arcpy.da.SearchCursor(active_centerline_sequence_view, [centerline_rid_field, "RoadwayIdGuid"],
                               concurrent_roadway_guid_where_clause) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            roadway_guid = sRow[1]
            if route_id not in route__roadway_guids_dict:
                route__roadway_guids_dict[route_id] = [roadway_guid]
            else:
                route__roadway_guids_dict[route_id].append(roadway_guid)
    arcpy.Delete_management(overlap_segments)
    index = 0
    for route_id, roadway_guids in route__roadway_guids_dict.items():
        roadway_guid_where_clause = build_string_in_sql_expression("RoadwayIdGuid", roadway_guids)
        arcpy.MakeFeatureLayer_management(centerline, centerline_layer, roadway_guid_where_clause)
        if index == 0:
            arcpy.UnsplitLine_management(centerline_layer, overlap_segments)
            index += 1
        else:
            arcpy.UnsplitLine_management(centerline_layer, unsplit_centerline)
            arcpy.Append_management(unsplit_centerline, overlap_segments)


def find_overlap_segments(network, overlap_segments):
    """
    Find overlap segments using pure geometry
    :param network:
    :param overlap_segments:
    """
    arcpy.CreateFeatureclass_management(os.path.dirname(overlap_segments), os.path.basename(overlap_segments), "POLYLINE", "", "ENABLED", "DISABLED", network)
    with arcpy.da.InsertCursor(overlap_segments, ['SHAPE@']) as iCursor:
        with arcpy.da.SearchCursor(network, ['SHAPE@', 'OID@']) as sCursor:
            for line1, line2 in combinations(sCursor, 2):
                shape1 = line1[0]
                shape2 = line2[0]
                if shape1.overlaps(shape2):
                    print line1[1], line2[1]
                    overlap_shape = shape1.intersect(shape2, 2)
                    iCursor.insertRow([overlap_shape])


def overlap_segments_to_concurrent_end_points(overlap_segments, concurrent_end_points):
    """

    :param overlap_segments:
    :param concurrent_end_points:
    """
    arcpy.FeatureVerticesToPoints_management(overlap_segments, concurrent_end_points, "BOTH_ENDS")

if __name__ == "__main__":
    input_fc = r'C:\Project\Intersection_Analysis\WorkingData7_1.gdb\LRSN_Ohio_WIL_Portion'
    overlap_segments = r'C:\Project\Intersection_Analysis\WorkingData7_1.gdb\overlap_segments'
    concurrent_end_points = r'C:\Project\Intersection_Analysis\WorkingData7_1.gdb\concurrent_end_points'
    arcpy.env.overwriteOutput = True
    find_overlap_segments(r'C:\Project\Intersection_Analysis\WorkingData7_1.gdb\LRSN_Ohio_WIL_Portion', overlap_segments)
    overlap_segments_to_concurrent_end_points(overlap_segments, concurrent_end_points)
