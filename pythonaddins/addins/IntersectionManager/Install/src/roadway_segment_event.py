import arcpy
from tss.ags import transform_dataset_keep_fields, populate_auto_increment_id, alter_field_name


class RoadwaySegmentEvent:

    def __init__(self, **kwargs):
        self.network = kwargs.get("network", None)
        self.network_route_id_field = kwargs.get("network_route_id_field", None)

        self.intersection_event = kwargs.get("intersection_event", None)

        self.roadway_segment_event = kwargs.get("roadway_segment_event", None)
        self.roadway_segment_rid_field = kwargs.get("roadway_segment_rid_field", None)
        self.roadway_segment_id_field = kwargs.get("roadway_segment_id_field", None)
        self.roadway_segment_from_meas_field = kwargs.get("roadway_segment_from_meas_field", None)
        self.roadway_segment_to_meas_field = kwargs.get("roadway_segment_to_meas_field", None)

        self.measure_scale = kwargs.get("measure_scale", 3)
        self.search_radius = kwargs.get("search_radius", "1 meters")

    def create_roadway_segment_event(self):
        self.generate_int_to_int_features()
        self.populate_from_to_measure_fields()
        populate_auto_increment_id(self.roadway_segment_event, self.roadway_segment_id_field)
        self.adjust_output_schema()
        return self.roadway_segment_event

    def generate_int_to_int_features(self):
        arcpy.SplitLineAtPoint_management(self.network, self.intersection_event, self.roadway_segment_event, self.search_radius)
        arcpy.DeleteIdentical_management(self.roadway_segment_event, [arcpy.Describe(self.roadway_segment_event).shapeFieldName, self.network_route_id_field], '#', '0')

    def populate_from_to_measure_fields(self):
        arcpy.AddField_management(self.roadway_segment_event, self.roadway_segment_id_field, "TEXT", "", "", 20)
        arcpy.AddField_management(self.roadway_segment_event, self.roadway_segment_from_meas_field, "DOUBLE")
        arcpy.AddField_management(self.roadway_segment_event, self.roadway_segment_to_meas_field, "DOUBLE")
        with arcpy.da.UpdateCursor(self.roadway_segment_event, ("SHAPE@", self.roadway_segment_from_meas_field, self.roadway_segment_to_meas_field)) as cursor:
            for row in cursor:
                shape = row[0]
                row[1] = round(min(shape.firstPoint.M, shape.lastPoint.M), int(self.measure_scale))
                row[2] = round(max(shape.firstPoint.M, shape.lastPoint.M), int(self.measure_scale))
                cursor.updateRow(row)

    def adjust_output_schema(self):
        if self.roadway_segment_rid_field != self.network_route_id_field:
            alter_field_name(self.roadway_segment_event, self.network_route_id_field, self.roadway_segment_rid_field)
        transform_dataset_keep_fields(self.roadway_segment_event,
                                      [self.roadway_segment_rid_field, self.roadway_segment_id_field, self.roadway_segment_from_meas_field, self.roadway_segment_to_meas_field])


