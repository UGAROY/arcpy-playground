import arcpy

from tss.ags import transform_dataset_keep_fields


# Intermediate data
simplify_network = "simplify_network"
no_mz_network = "no_mz_network"


class IntersectionEvent:

    def __init__(self, **kwargs):
        self.network = kwargs.get("network", None)
        self.intersection_event = kwargs.get("intersection_event", None)
        self.intersection_filter_layer = kwargs.get("intersection_filter_layer", None)
        self.intersection_id_field = kwargs.get("intersection_id_field", None)
        self.network_route_id_field = kwargs.get("network_route_id_field", None)
        self.search_radius = kwargs.get("search_radius", "1 meters")

    def create_intersection_event(self):
        self.detect_intersections()
        self.populate_intersection_id()
        self.adjust_output_schema()
        return self.intersection_event

    def detect_intersections(self):
        outputZFlag = arcpy.env.outputZFlag
        outputMFlag = arcpy.env.outputMFlag
        arcpy.env.outputZFlag = "Disabled"
        arcpy.env.outputMFlag = "Disabled"

        arcpy.CopyFeatures_management(self.network, no_mz_network)
        arcpy.SimplifyLine_cartography(no_mz_network, simplify_network, "POINT_REMOVE", "999999 meters")

        arcpy.FeatureVerticesToPoints_management(simplify_network, self.intersection_event, "ALL")
        self.filter_out_none_intersections()

        with arcpy.da.SearchCursor(self.intersection_event, ["SHAPE@XY", self.network_route_id_field]) as sCursor:
            xy__rid_list_dict = {}
            for sRow in sCursor:
                xy_tuple, route_id = sRow[0], sRow[1]
                if xy_tuple not in xy__rid_list_dict:
                    xy__rid_list_dict[xy_tuple] = []
                xy__rid_list_dict[xy_tuple].append(route_id)

        xy_type_dict = {}
        with arcpy.da.UpdateCursor(self.intersection_event, ["SHAPE@XY"]) as uCursor:
            for uRow in uCursor:
                xy= uRow[0]
                rid_list = xy__rid_list_dict[xy]
                length = len(rid_list)
                if length == 1:
                    xy_type_dict[xy] = "DELETE"  # Dangle points or loop skeleton, not real intersections, need to be deleted
                elif length == 2:
                    if rid_list[0] == rid_list[1]:
                        xy_type_dict[xy] = "CIRCULAR INTERSECTIONS"  # The loop intersection point
                    else:
                        xy_type_dict[xy] = "TRUE INTERSECTIONS"
                elif length >= 3:
                    unique_length = len(set(rid_list))
                    if unique_length == length:
                        xy_type_dict[xy] = "TRUE INTERSECTIONS"
                    elif unique_length == 1:
                        xy_type_dict[xy] = "CIRCULAR INTERSECTIONS"
                    else:
                        xy_type_dict[xy] = "CONCURRENT INTERSECTIONS OR OTHERS"

                if xy_type_dict[xy] in ["DELETE"]:
                    uCursor.deleteRow()

        arcpy.DeleteIdentical_management(self.intersection_event, arcpy.Describe(self.intersection_event).shapeFieldName)

        arcpy.env.outputZFlag = outputZFlag
        arcpy.env.outputMFlag = outputMFlag
        arcpy.Delete_management(simplify_network)
        arcpy.Delete_management("%s_Pnt" % simplify_network)

        return self.intersection_event

    def filter_out_none_intersections(self):
        if self.intersection_filter_layer:
            arcpy.MakeFeatureLayer_management(self.intersection_event, "intersection_event_layer")
            arcpy.SelectLayerByLocation_management("intersection_event_layer", "INTERSECT", self.intersection_filter_layer, self.search_radius)
            arcpy.SelectLayerByAttribute_management("intersection_event_layer", "SWITCH_SELECTION")
            if int(arcpy.GetCount_management("intersection_event_layer").getOutput(0)) > 0:
                arcpy.DeleteRows_management("intersection_event_layer")

    def populate_intersection_id(self):
        arcpy.AddField_management(self.intersection_event, self.intersection_id_field, "TEXT", "", "", 20)
        with arcpy.da.UpdateCursor(self.intersection_event, self.intersection_id_field) as cursor:
            max_id = 0
            for row in cursor:
                max_id += 1
                row[0] = "%s" % max_id
                cursor.updateRow(row)

    def adjust_output_schema(self):
        transform_dataset_keep_fields(self.intersection_event, [self.intersection_id_field])

