from datetime import datetime

import arcpy

from tss import format_sql_date, extract_number_from_string
from util.helper import get_default_parameters
from config.schema import default_schemas
from util.meta import write_im_meta_data
import intersection_approach_event as intersection_approach_event_mod


import logging
logger = logging.getLogger(__name__)


def populate_intersection_leg_info(workspace, create_date):

    client = "Default"
    parameters = get_default_parameters()
    schemas = default_schemas.get(client)

    dbtype = parameters.get(client, "dbtype")

    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False

    # source data -------------------------------------------------------------------------
    network = parameters.get(client, "network")
    network_route_id_field = parameters.get(client, "network_route_id_field")
    network_from_date_field = parameters.get(client, "network_from_date_field")
    network_to_date_field = parameters.get(client, "network_to_date_field")

    intersection_event = schemas.get("intersection_event")
    intersection_id_field = schemas.get("intersection_id_field")

    intersection_route_event = schemas.get("intersection_route_event")
    intersection_route_on_rid_field = schemas.get("intersection_route_on_rid_field")
    intersection_route_on_measure_field = schemas.get("intersection_route_on_measure_field")

    roadway_segment_event = schemas.get("roadway_segment_event")
    roadway_segment_id_field = schemas.get("roadway_segment_id_field")
    roadway_segment_rid_field = schemas.get("roadway_segment_rid_field")
    roadway_segment_from_meas_field = schemas.get("roadway_segment_from_meas_field")
    roadway_segment_to_meas_field = schemas.get("roadway_segment_to_meas_field")

    function_class_event = parameters.get(client, "function_class_event")
    function_class_field = parameters.get(client, "function_class_field")
    function_class_rid_field = parameters.get(client, "function_class_rid_field")
    function_class_from_meas_field = parameters.get(client, "function_class_from_meas_field")
    function_class_to_meas_field = parameters.get(client, "function_class_to_meas_field")
    function_class_from_date_field = parameters.get(client, "function_class_from_date_field")
    function_class_to_date_field = parameters.get(client, "function_class_to_date_field")

    aadt_event = parameters.get(client, "aadt_event")
    aadt_field = parameters.get(client, "aadt_field")
    aadt_rid_field = parameters.get(client, "aadt_rid_field")
    aadt_from_meas_field = parameters.get(client, "aadt_from_meas_field")
    aadt_to_meas_field = parameters.get(client, "aadt_to_meas_field")
    aadt_from_date_field = parameters.get(client, "aadt_from_date_field")
    aadt_to_date_field = parameters.get(client, "aadt_to_date_field")

    date = create_date or datetime.now()
    date_string = date.strftime("%Y-%m-%d")
    query_date_string = format_sql_date(date, dbtype)
    #--------------------------------------------------------------------------------------

    # output data -------------------------------------------------------------------------
    intersection_approach_event = schemas.get("intersection_approach_event")
    intersection_approach_id_field = schemas.get("intersection_approach_id_field")
    intersection_approach_leg_id_field = schemas.get("intersection_approach_leg_id_field")
    intersection_approach_leg_type_field = schemas.get("intersection_approach_leg_type_field")
    intersection_approach_leg_dir_field = schemas.get("intersection_approach_leg_dir_field")
    intersection_approach_angle_field = schemas.get("intersection_approach_angle_field")
    intersection_approach_beg_inf_field = schemas.get("intersection_approach_beg_inf_field")
    intersection_approach_end_inf_field = schemas.get("intersection_approach_end_inf_field")

    from_date_field = schemas.get("from_date_field")
    to_date_field = schemas.get("to_date_field")
    # -------------------------------------------------------------------------------------

    # configuration ----------------------------------------------------------------------
    search_radius = parameters.get(client, "search_radius")
    measure_scale = int(parameters.get(client, "measure_scale"))
    angle_calculation_distance = extract_number_from_string(parameters.get(client, "angle_calculation_distance"))[0] / 5280
    area_of_influence = extract_number_from_string(parameters.get(client, "area_of_influence"))[0] / 5280
    azumith_zero_direction = parameters.get(client, "azumith_zero_direction")
    # ------------------------------------------------------------------------------------

    # Data preprocessing-----------------------------------------------------------------
    query_filter = "{0} is not NULL and ({1} is null or {1} <= {3}) and ({2} is null or {2} > {3})".format(network_route_id_field, network_from_date_field, network_to_date_field, query_date_string)
    arcpy.MakeFeatureLayer_management(network, "network_layer", query_filter)
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(function_class_from_date_field, function_class_to_date_field, query_date_string) if function_class_from_date_field and function_class_to_date_field else "1=1"
    arcpy.MakeFeatureLayer_management(function_class_event, "function_class_layer", query_filter)
    if arcpy.Exists(aadt_event):
        query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(aadt_from_date_field, aadt_to_date_field, query_date_string) if aadt_from_date_field and aadt_to_date_field else "1=1"
        arcpy.MakeFeatureLayer_management(aadt_event, "aadt_layer", query_filter)
    # -------------------------------------------------------------------------------------

    intersection_approach_event_instance = intersection_approach_event_mod.IntersectionApproachEvent(
        network="network_layer",
        network_route_id_field=network_route_id_field,

        roadway_segment_event=roadway_segment_event,
        roadway_segment_id_field=roadway_segment_id_field,
        roadway_segment_rid_field=roadway_segment_rid_field,
        roadway_segment_from_meas_field=roadway_segment_from_meas_field,
        roadway_segment_to_meas_field=roadway_segment_to_meas_field,

        intersection_event=intersection_event,
        intersection_id_field=intersection_id_field,

        intersection_route_event=intersection_route_event,
        intersection_route_on_rid_field=intersection_route_on_rid_field,
        intersection_route_on_measure_field=intersection_route_on_measure_field,

        intersection_approach_event=intersection_approach_event,
        intersection_approach_id_field=intersection_approach_id_field,
        intersection_approach_leg_id_field=intersection_approach_leg_id_field,
        intersection_approach_leg_type_field=intersection_approach_leg_type_field,
        intersection_approach_leg_dir_field=intersection_approach_leg_dir_field,
        intersection_approach_angle_field=intersection_approach_angle_field,
        intersection_approach_beg_inf_field=intersection_approach_beg_inf_field,
        intersection_approach_end_inf_field=intersection_approach_end_inf_field,

        function_class_layer="function_class_layer",
        function_class_field=function_class_field,
        function_class_rid_field=function_class_rid_field,
        function_class_from_meas_field=function_class_from_meas_field,
        function_class_to_meas_field=function_class_to_meas_field,
        aadt_layer="aadt_layer",
        aadt_field=aadt_field,
        aadt_rid_field=aadt_rid_field,
        aadt_from_meas_field=aadt_from_meas_field,
        aadt_to_meas_field=aadt_to_meas_field,

        area_of_influence=area_of_influence,
        angle_calculation_distance=angle_calculation_distance,
        azumith_zero_direction=azumith_zero_direction,
        measure_scale=measure_scale,
        search_radius=search_radius,

        dbtype=dbtype
    )
    intersection_approach_event = intersection_approach_event_instance.create_intersection_approach_event()

    arcpy.AddField_management(intersection_approach_event, from_date_field, "DATE")
    arcpy.AddField_management(intersection_approach_event, to_date_field, "DATE")
    arcpy.CalculateField_management(intersection_approach_event, from_date_field, "'%s'" % date_string, "PYTHON")

    logger.info("Finished populating intersection approach event")


if __name__ == "__main__":
    from tss import truncate_datetime
    from odot.ohio_dot_create import custom_create_odot
    workspace  = r'C:\Projects\ODOT\Data\Raw.gdb'
    create_date = truncate_datetime(datetime.now())
    populate_intersection_leg_info(workspace, create_date)
    custom_create_odot(workspace)
    write_im_meta_data(workspace, create_date)