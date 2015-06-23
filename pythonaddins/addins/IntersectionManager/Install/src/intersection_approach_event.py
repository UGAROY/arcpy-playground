import arcpy

from tss import geodesic_angle_to_circular_angle, geodesic_angle_to_direction
from util.leg import calculate_leg_type_property, populate_leg_id_by_intersection
from tss import transform_dataset_keep_fields, alter_field_name


# Intermediate data
segments_join_intersections = "segments_join_intersections"
leg_type_points = "leg_type_points"
leg_angle_points = "leg_angle_points"
near_table = "near_table"
leg_type_calculation_mileage = 0.0001  # Set a distance away from the intersection to avoid confusion
function_class_join = "function_class_join"
aadt_join = "aadt_join"

# Intermediate fields
intersection_measure_field = "Intersection_Measure"
leg_type_measure_field = "Leg_Type_Measure"
leg_angle_measure_field = "Leg_Angle_Measure"

# Scale of the approach angle, TODO: verify if we want to make it configurable
angle_scale = 3

import logging
logger = logging.getLogger(__name__)


class IntersectionApproachEvent:

    def __init__(self, **kwargs):

        self.network = kwargs.get("network", None)
        self.network_route_id_field = kwargs.get("network_route_id_field", None)

        self.roadway_segment_event = kwargs.get("roadway_segment_event", None)
        self.roadway_segment_rid_field = kwargs.get("roadway_segment_rid_field", None)
        self.roadway_segment_id_field = kwargs.get("roadway_segment_id_field", None)
        self.roadway_segment_from_meas_field = kwargs.get("roadway_segment_from_meas_field", None)
        self.roadway_segment_to_meas_field = kwargs.get("roadway_segment_to_meas_field", None)

        self.intersection_event = kwargs.get("intersection_event", None)
        self.intersection_id_field = kwargs.get("intersection_id_field", None)

        self.intersection_route_event = kwargs.get("intersection_route_event", None)
        self.intersection_route_on_rid_field = kwargs.get("intersection_route_on_rid_field", None)
        self.intersection_route_on_measure_field = kwargs.get("intersection_route_on_measure_field", None)

        self.intersection_approach_event = kwargs.get("intersection_approach_event", None)
        self.intersection_approach_id_field = kwargs.get("intersection_approach_id_field", None)
        self.intersection_approach_leg_id_field = kwargs.get("intersection_approach_leg_id_field", None)
        self.intersection_approach_leg_type_field = kwargs.get("intersection_approach_leg_type_field", None)
        self.intersection_approach_leg_dir_field = kwargs.get("intersection_approach_leg_dir_field", None)
        self.intersection_approach_angle_field = kwargs.get("intersection_approach_angle_field", None)
        self.intersection_approach_beg_inf_field = kwargs.get("intersection_approach_beg_inf_field", None)
        self.intersection_approach_end_inf_field = kwargs.get("intersection_approach_end_inf_field", None)

        self.function_class_layer = kwargs.get("function_class_layer", None)
        self.function_class_field = kwargs.get("function_class_field", None)
        self.function_class_rid_field = kwargs.get("function_class_rid_field", None)
        self.function_class_from_meas_field = kwargs.get("function_class_from_meas_field", None)
        self.function_class_to_meas_field = kwargs.get("function_class_to_meas_field", None)
        self.aadt_layer = kwargs.get("aadt_layer", None)
        self.aadt_field = kwargs.get("aadt_field", None)
        self.aadt_rid_field = kwargs.get("aadt_rid_field", None)
        self.aadt_from_meas_field = kwargs.get("aadt_from_meas_field", None)
        self.aadt_to_meas_field = kwargs.get("aadt_to_meas_field", None)

        self.angle_calculation_distance = kwargs.get("angle_calculation_distance", None)
        self.azumith_zero_direction = kwargs.get("azumith_zero_direction", None)
        self.measure_scale = kwargs.get("measure_scale", None)
        self.search_radius = kwargs.get("search_radius", "1 meters")
        self.area_of_influence = kwargs.get("area_of_influence", None)

        self.no_null_measure_where_clause = "%s is not NULL and %s is not NULL and %s is not NULL" % (self.roadway_segment_from_meas_field, self.roadway_segment_to_meas_field, intersection_measure_field)

        self.dbtype = kwargs.get("dbtype", None)

    def create_intersection_approach_event(self):
        arcpy.SpatialJoin_analysis(self.roadway_segment_event, self.intersection_event, segments_join_intersections, "JOIN_ONE_TO_MANY", "KEEP_COMMON", "#", "INTERSECT", self.search_radius, "#")
        logger.info("Finished joining roadway segment event to intersection event")
        self.populate_intersection_measure()
        logger.info("Finished populating the intersection measure")
        self.populate_approach_id()
        logger.info("Finished populating the approach id")
        self.populate_approach_ang_dir()
        logger.info("Finished populating the approach angle and direction")
        self.populate_beg_end_inf()
        logger.info("Finished populating the begin and end influence area")
        self.populate_leg_id()
        logger.info("Finished populating the leg id")
        self.populate_leg_type()
        logger.info("Finished populating the leg type")
        self.adjust_output_schema()
        self.clear_intermediate_date()

        return self.intersection_approach_event

    def populate_intersection_measure(self):
        inter_route__measure_dict = {}
        with arcpy.da.SearchCursor(self.intersection_route_event, (self.intersection_id_field, self.intersection_route_on_rid_field, self.intersection_route_on_measure_field)) as sCursor:
            for sRow in sCursor:
                inter_route__measure_dict[sRow[0] + "-" + sRow[1]] = sRow[2]
        arcpy.AddField_management(segments_join_intersections, intersection_measure_field, "Double")
        with arcpy.da.UpdateCursor(segments_join_intersections, (self.intersection_id_field, self.roadway_segment_rid_field, intersection_measure_field)) as uCursor:
            for uRow in uCursor:
                uRow[2] = inter_route__measure_dict.get(uRow[0] + "-" + uRow[1], None)
                uCursor.updateRow(uRow)

    def populate_beg_end_inf(self):
        arcpy.AddField_management(segments_join_intersections, self.intersection_approach_beg_inf_field, "DOUBLE")
        arcpy.AddField_management(segments_join_intersections, self.intersection_approach_end_inf_field, "DOUBLE")
        with arcpy.da.UpdateCursor(segments_join_intersections,
                                   (intersection_measure_field, self.roadway_segment_from_meas_field, self.roadway_segment_to_meas_field,
                                    self.intersection_approach_beg_inf_field, self.intersection_approach_end_inf_field),
                                   self.no_null_measure_where_clause) as uCursor:
            for uRow in uCursor:
                intersection_measure, segment_from_measure, segment_to_measure  = uRow[0], uRow[1], uRow[2]
                if abs(intersection_measure - segment_from_measure) < 0.0001:
                    uRow[3] = intersection_measure
                    uRow[4] = min(segment_from_measure + self.area_of_influence, segment_to_measure)
                else:
                    uRow[3] = max(segment_to_measure - self.area_of_influence, segment_from_measure)
                    uRow[4] = segment_to_measure
                uRow[3] = round(uRow[3], int(self.measure_scale))
                uRow[4] = round(uRow[4], int(self.measure_scale))
                uCursor.updateRow(uRow)

    def populate_approach_id(self):
        arcpy.AddField_management(segments_join_intersections, self.intersection_approach_id_field, "TEXT", "", "", 20)
        arcpy.CalculateField_management(segments_join_intersections, self.intersection_approach_id_field, "[%s] + \"-\" + [%s]" % (self.intersection_id_field, self.roadway_segment_id_field))

    def populate_approach_ang_dir(self):
        arcpy.AddField_management(segments_join_intersections, self.intersection_approach_angle_field, "DOUBLE")
        arcpy.AddField_management(segments_join_intersections, self.intersection_approach_leg_dir_field, "TEXT", "", "", "10")
        # Implement a new way to calculate the leg type direction and angle
        arcpy.AddField_management(segments_join_intersections, leg_angle_measure_field, "DOUBLE")
        with arcpy.da.UpdateCursor(segments_join_intersections, [self.roadway_segment_from_meas_field, self.roadway_segment_to_meas_field, intersection_measure_field, leg_angle_measure_field], self.no_null_measure_where_clause) as uCursor:
            for uRow in uCursor:
                segment_from_measure, segment_to_measure, intersection_measure = uRow[0], uRow[1], uRow[2]
                if abs(segment_from_measure - intersection_measure) <= 0.0001:
                    uRow[3] = intersection_measure + self.angle_calculation_distance
                else:
                    uRow[3] = intersection_measure - self.angle_calculation_distance
                uCursor.updateRow(uRow)
        arcpy.MakeRouteEventLayer_lr(self.network, self.network_route_id_field, segments_join_intersections, "%s POINT %s" % (self.roadway_segment_rid_field, leg_angle_measure_field), "leg_angle_point_layer")
        arcpy.CopyFeatures_management("leg_angle_point_layer", leg_angle_points)

        # Use near function to generate the near angle
        # For now just hard code the angle calculation method to "GEODESIC". TODO: verify what the user want
        arcpy.GenerateNearTable_analysis(leg_angle_points, self.intersection_event, near_table, "{0} MILES".format(float(self.angle_calculation_distance) + 0.001), "NO_LOCATION", "ANGLE", "ALL", "0", "GEODESIC")
        arcpy.JoinField_management(near_table, "IN_FID", leg_angle_points, "OBJECTID", "%s;%s" % (self.roadway_segment_id_field, self.intersection_id_field))
        alter_field_name(near_table, self.intersection_id_field, "lap_%s" % self.intersection_id_field, self.dbtype!="FileGdb")
        arcpy.JoinField_management(near_table, "NEAR_FID", self.intersection_event, "OBJECTID", self.intersection_id_field)
        inter__seg_angle_dict = {}
        with arcpy.da.SearchCursor(near_table, [self.intersection_id_field, self.roadway_segment_id_field, "NEAR_ANGLE"], "lap_{0} = {0}".format(self.intersection_id_field)) as sCursor:
            for sRow in sCursor:
                intersection_id, segment_id, leg_angle = sRow[0], sRow[1], sRow[2]
                if intersection_id not in inter__seg_angle_dict:
                    inter__seg_angle_dict[intersection_id] = {}
                inter__seg_angle_dict[intersection_id][segment_id] = round(leg_angle, angle_scale)

        with arcpy.da.UpdateCursor(segments_join_intersections, [self.intersection_id_field, self.roadway_segment_id_field, self.intersection_approach_angle_field, self.intersection_approach_leg_dir_field]) as uCursor:
            for uRow in uCursor:
                intersection_id, segment_id = uRow[0], uRow[1]
                try:
                    geodesic_angle = inter__seg_angle_dict[intersection_id][segment_id]
                    uRow[2] = geodesic_angle_to_circular_angle(geodesic_angle)
                    uRow[3] = geodesic_angle_to_direction(geodesic_angle)
                except KeyError:
                    uRow[2], uRow[3] = None, None
                uCursor.updateRow(uRow)


    def populate_leg_id(self):
        arcpy.AddField_management(segments_join_intersections, self.intersection_approach_leg_id_field, "SHORT")
        populate_leg_id_by_intersection(segments_join_intersections, self.intersection_id_field, self.roadway_segment_id_field, self.intersection_approach_leg_id_field, self.intersection_approach_angle_field)

    def populate_leg_type(self):
        # Create a point for each leg for leg type calculation
        arcpy.AddField_management(segments_join_intersections, leg_type_measure_field, "DOUBLE")
        with arcpy.da.UpdateCursor(segments_join_intersections, [self.roadway_segment_from_meas_field, self.roadway_segment_to_meas_field, intersection_measure_field, leg_type_measure_field], self.no_null_measure_where_clause) as uCursor:
            for uRow in uCursor:
                segment_from_measure, segment_to_measure, intersection_measure = uRow[0], uRow[1], uRow[2]
                if abs(segment_from_measure - intersection_measure) <= 0.0001:
                    uRow[3] = intersection_measure + leg_type_calculation_mileage
                else:
                    uRow[3] = intersection_measure - leg_type_calculation_mileage
                uCursor.updateRow(uRow)
        arcpy.MakeRouteEventLayer_lr(self.network, self.network_route_id_field, segments_join_intersections, "%s POINT %s" % (self.roadway_segment_rid_field, leg_type_measure_field), "leg_type_point_layer")
        arcpy.CopyFeatures_management("leg_type_point_layer", leg_type_points)

        logger.info("Finished creating leg type points")

        self.join_event_fields_to_leg_type_points(self.function_class_layer, self.function_class_rid_field, [self.function_class_field], function_class_join)
        if arcpy.Exists(self.aadt_layer):
            self.join_event_fields_to_leg_type_points(self.aadt_layer, self.aadt_rid_field, [self.aadt_field], aadt_join)
            logger.info("Finished joining the function class and addt values to leg type points")

        # Build the intersection__seg__value_dict
        inter__seg__leg_value_dict = {}
        self.build_inter__seg__value_dict(function_class_join, self.function_class_rid_field, self.function_class_field, inter__seg__leg_value_dict)

        if arcpy.Exists(aadt_join):
            self.build_inter__seg__value_dict(aadt_join, self.aadt_rid_field, self.aadt_field, inter__seg__leg_value_dict)

        # calcuate the leg type for each intersection and segment
        for intersection_id, seg__value_dict in inter__seg__leg_value_dict.items():
            calculate_leg_type_property(seg__value_dict, self.function_class_field, self.aadt_field)

        logger.info("Finished building intersection leg type dictionary")

        # Assign the calculated leg type to table
        arcpy.AddField_management(segments_join_intersections, self.intersection_approach_leg_type_field, "TEXT", "", "", 10)
        with arcpy.da.UpdateCursor(segments_join_intersections, [self.intersection_id_field, self.roadway_segment_id_field, self.intersection_approach_leg_type_field]) as uCursor:
            for uRow in uCursor:
                intersection_id, segment_id = uRow[0], uRow[1]
                try:
                    uRow[2] = inter__seg__leg_value_dict[intersection_id][segment_id]["Leg_Type"]
                except KeyError:
                    if intersection_id in inter__seg__leg_value_dict and inter__seg__leg_value_dict[intersection_id]:
                        # If there is at least one leg for the current intersection that has attributes
                        # Then all the other legs should be "Minor"
                        uRow[2] = "Minor"
                    else:
                        uRow[2] = None
                uCursor.updateRow(uRow)

        # Export to Table
        arcpy.CopyRows_management(segments_join_intersections, self.intersection_approach_event)

    def join_event_fields_to_leg_type_points(self, event_layer, rid_field_name, fields, output_join):
        fms = arcpy.FieldMappings()
        fms.addTable(event_layer)

        fields.append(rid_field_name)
        for field in arcpy.ListFields(event_layer):
            if field.required:
                continue
            field_name = field.name
            if field_name not in fields:
                fm_index = fms.findFieldMapIndex(field_name)
                if fm_index != -1:
                    # Exclude shape and oid field, which will not be included in the fieldMappings.addTable
                    fms.removeFieldMap(fm_index)

        # Tod avoid the conflicts, need to rename the rid_field
        rid_field_index = fms.findFieldMapIndex(rid_field_name)
        rid_fm = fms.getFieldMap(rid_field_index)
        rid_field = rid_fm.outputField
        rid_field.name = "event_%s" % rid_field_name
        rid_field.aliasName = "event_%s" % rid_field_name
        rid_fm.outputField = rid_field
        fms.replaceFieldMap(rid_field_index, rid_fm)

        fms.addTable(leg_type_points)
        arcpy.SpatialJoin_analysis(leg_type_points, event_layer, output_join, "JOIN_ONE_TO_MANY", "KEEP_ALL", fms, "INTERSECT", "#")

    def build_inter__seg__value_dict(self, event_join, rid_field, field, inter__seg__leg_value_dict):
        output_fields = [self.intersection_id_field, self.roadway_segment_id_field]
        output_fields.append(field)
        with arcpy.da.SearchCursor(event_join, output_fields,
                                   "%s=event_%s" % (self.roadway_segment_rid_field, rid_field)) as sCursor:
            for sRow in sCursor:
                intersection_id, segment_id, event_value = sRow[0], sRow[1], sRow[2]
                if intersection_id not in inter__seg__leg_value_dict:
                    inter__seg__leg_value_dict[intersection_id] = {}
                if segment_id not in inter__seg__leg_value_dict[intersection_id]:
                    inter__seg__leg_value_dict[intersection_id][segment_id] = {}
                inter__seg__leg_value_dict[intersection_id][segment_id][field] = event_value


    def adjust_output_schema(self):
        transform_dataset_keep_fields(self.intersection_approach_event,
                                      [self.intersection_approach_id_field, self.intersection_id_field,
                                       self.roadway_segment_id_field,
                                       self.intersection_approach_leg_id_field, self.intersection_approach_leg_type_field,
                                       self.intersection_approach_leg_dir_field,
                                       self.intersection_approach_angle_field,
                                       self.roadway_segment_rid_field, self.intersection_approach_beg_inf_field,
                                       self.intersection_approach_end_inf_field])

    def clear_intermediate_date(self):
        to_be_deleted_items = [segments_join_intersections, leg_type_points, leg_angle_points, near_table, function_class_join, aadt_join]
        for item in to_be_deleted_items:
            arcpy.Delete_management(item)