from datetime import datetime
import arcpy

from tss import format_sql_date
from util.helper import get_default_parameters
from config.schema import default_schemas

import intersection_event as intersection_event_mod
import roadway_segment_event as roadway_segment_event_mod
import intersection_route_event as intersection_route_event_mod

import logging
logger = logging.getLogger(__name__)


def populate_intersections_info(workspace, create_date):

    client = "Default"
    parameters = get_default_parameters()
    schemas = default_schemas.get(client)

    dbtype = parameters.get(client, "dbtype")

    # Read Paramters from User Input------------------------------------------------
    date = create_date or datetime.now()
    date_string = date.strftime("%Y-%m-%d")
    query_date_string = format_sql_date(date, dbtype)
    # ------------------------------------------------------------------------------

    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False

    # Source data -------------------------------------------------------------------
    network = parameters.get(client,"network")
    network_route_id_field = parameters.get(client, "network_route_id_field")
    network_route_name_field = parameters.get(client, "network_route_name_field")
    network_from_date_field = parameters.get(client, "network_from_date_field")
    network_to_date_field = parameters.get(client, "network_to_date_field")

    intersection_filter_point = parameters.get(client, "intersection_filter_point")
    intersection_filter_from_date_field = parameters.get(client, "intersection_filter_from_date_field")
    intersection_filter_to_date_field = parameters.get(client, "intersection_filter_to_date_field")
    #-------------------------------------------------------------------------------

    # output data and schema--------------------------------------------------------
    intersection_event = schemas.get("intersection_event")
    intersection_id_field = schemas.get("intersection_id_field")

    intersection_route_event = schemas.get("intersection_route_event")
    intersection_route_on_rid_field = schemas.get("intersection_route_on_rid_field")
    intersection_route_on_rname_field = schemas.get("intersection_route_on_rname_field")
    intersection_route_on_measure_field = schemas.get("intersection_route_on_measure_field")
    intersection_route_at_rid_field = schemas.get("intersection_route_at_rid_field")
    intersection_route_at_rname_field = schemas.get("intersection_route_at_rname_field")

    roadway_segment_event = schemas.get("roadway_segment_event")
    roadway_segment_id_field = schemas.get("roadway_segment_id_field")
    roadway_segment_rid_field = schemas.get("roadway_segment_rid_field")
    roadway_segment_from_meas_field = schemas.get("roadway_segment_from_meas_field")
    roadway_segment_to_meas_field = schemas.get("roadway_segment_to_meas_field")

    from_date_field = schemas.get("from_date_field")
    to_date_field = schemas.get("to_date_field")
    # ------------------------------------------------------------------------------

    # configuration ----------------------------------------------------------------
    search_radius = parameters.get(client, "search_radius")
    measure_scale = parameters.get(client, "measure_scale")
    # -----------------------------------------------------------------------------

    # Data pre-processing ----------------------------------------------------------
    query_filter = "{0} is not NULL and ({1} is null or {1} <= {3}) and ({2} is null or {2} > {3})".format(network_route_id_field, network_from_date_field, network_to_date_field, query_date_string)
    arcpy.MakeFeatureLayer_management(network, "network_layer", query_filter)
    if intersection_filter_point:
        if intersection_filter_from_date_field and intersection_filter_to_date_field:
            query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(intersection_filter_from_date_field, intersection_filter_to_date_field, query_date_string)
        else:
            query_filter = ""
        intersection_filter_layer = "intersection_filter_layer"
        arcpy.MakeFeatureLayer_management(intersection_filter_point, intersection_filter_layer, query_filter)
    else:
        intersection_filter_layer = ""
    #-------------------------------------------------------------------------------

    intersection_event_instance = intersection_event_mod.IntersectionEvent(
        network="network_layer",
        intersection_filter_layer=intersection_filter_layer,
        intersection_event=intersection_event,
        intersection_id_field=intersection_id_field,
        network_route_id_field=network_route_id_field,
        search_radius=search_radius)
    intersection_event = intersection_event_instance.create_intersection_event()

    logger.info("Finished creating the intersection event")

    intersection_route_event_instance = intersection_route_event_mod.IntersectionRouteEvent(
        network="network_layer",
        network_route_id_field=network_route_id_field,
        network_route_name_field=network_route_name_field,
        intersection_event=intersection_event,
        intersection_id_field=intersection_id_field,
        intersection_route_event=intersection_route_event,
        intersection_route_on_rid_field=intersection_route_on_rid_field,
        intersection_route_on_rname_field=intersection_route_on_rname_field,
        intersection_route_on_measure_field=intersection_route_on_measure_field,
        intersection_route_at_rid_field=intersection_route_at_rid_field,
        intersection_route_at_rname_field=intersection_route_at_rname_field,
        measure_scale=measure_scale,
        search_radius=search_radius
    )
    intersection_route_event = intersection_route_event_instance.create_intersection_route_event()

    logger.info("Finished creating the intersection route event")

    roadway_segment_event_instance = roadway_segment_event_mod.RoadwaySegmentEvent(
        network="network_layer",
        network_route_id_field=network_route_id_field,
        intersection_event=intersection_event,
        roadway_segment_event=roadway_segment_event,
        roadway_segment_id_field=roadway_segment_id_field,
        roadway_segment_rid_field=roadway_segment_rid_field,
        roadway_segment_from_meas_field=roadway_segment_from_meas_field,
        roadway_segment_to_meas_field=roadway_segment_to_meas_field,
        measure_scale=measure_scale,
        search_radius=search_radius
    )
    roadway_segment_event = roadway_segment_event_instance.create_roadway_segment_event()

    logger.info("Finished creating roadway segment event")

    # Populate date field
    arcpy.AddField_management(intersection_event, from_date_field, "DATE")
    arcpy.AddField_management(intersection_event, to_date_field, "DATE")
    arcpy.CalculateField_management(intersection_event, from_date_field, "'%s'" % date_string, "PYTHON")
    arcpy.AddField_management(intersection_route_event, from_date_field, "DATE")
    arcpy.AddField_management(intersection_route_event, to_date_field, "DATE")
    arcpy.CalculateField_management(intersection_route_event, from_date_field, "'%s'" % date_string, "PYTHON")
    arcpy.AddField_management(roadway_segment_event, from_date_field, "DATE")
    arcpy.AddField_management(roadway_segment_event, to_date_field, "DATE")
    arcpy.CalculateField_management(roadway_segment_event, from_date_field, "'%s'" % date_string, "PYTHON")


if __name__ == "__main__":
    pass