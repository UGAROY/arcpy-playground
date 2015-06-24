from datetime import timedelta
import os
import time
import arcpy
from tss import format_sql_date, get_maximum_id, subset_data_exist, build_string_in_sql_expression, \
    delete_identical_only_keep_min_oid,extract_number_from_string
from util.helper import get_default_parameters
from config.schema import default_schemas
import intersection_event as intersection_event_mod
import intersection_route_event as intersection_route_event_mod
import roadway_segment_event as roadway_segment_event_mod
import intersection_approach_event as intersection_approach_event_mod

import logging
logger = logging.getLogger(__name__)


""" Some terminologies
current_active ---> (from_date is null or from_date <= CURRENT_TIMESTAMP) and (to_date is null or to_date > CURRENT_TIMESTAMP)
previous_active ---> (from_date is null or from_date <= last_update_date) and (to_date is null or to_date > last_update_date)
created ---> from_date > last_update_date
retired ---> to_date > last_update_date
One thing to keep in mind is that even if we are just re-aligning a route, there will still be one record marked as retired and another one as new
inserted ---> newly created route with fresh new id
updated ---> realigned or extended route or retired partial route
    updated_before ---> updated routes in previous network
    updated_after ---> updated routes in current network
deleted ---> real retired route, the route id no longer exists
new ---> result of tba_current...
old ---> result of tba_previous...
    the new and old here are not real new and old, just the results in two different states
    further comparison is needed to get the actual updates
real_new ---> real new records
real_old ---> real old records
tbr ---> to be marked as retired
tbn ---> to be marked as new
new_active ---> updated in the scripts for later use
old_active ---> active records before running this script
"""

# Parameter and schema settings ----------------------------------------------------------------------------------------
client = "Default"
parameters = get_default_parameters()
schemas = default_schemas.get(client)

dbtype = parameters.get(client, "dbtype")

# Source Data -----------------------------------------------------------------------------------------
network = parameters.get(client,"network")
network_route_id_field = parameters.get(client,"network_route_id_field")
network_route_name_field = parameters.get(client,"network_route_name_field")
network_from_date_field = parameters.get(client,"network_from_date_field")
network_to_date_field = parameters.get(client,"network_to_date_field")

intersection_id_field = schemas.get("intersection_id_field")

intersection_route_on_rid_field = schemas.get("intersection_route_on_rid_field")
intersection_route_on_rname_field = schemas.get("intersection_route_on_rname_field")
intersection_route_on_measure_field = schemas.get("intersection_route_on_measure_field")
intersection_route_at_rid_field = schemas.get("intersection_route_at_rid_field")
intersection_route_at_rname_field = schemas.get("intersection_route_at_rname_field")

roadway_segment_id_field = schemas.get("roadway_segment_id_field")
roadway_segment_rid_field = schemas.get("roadway_segment_rid_field")
roadway_segment_from_meas_field = schemas.get("roadway_segment_from_meas_field")
roadway_segment_to_meas_field = schemas.get("roadway_segment_to_meas_field")

function_class_event = parameters.get(client,"function_class_event")
function_class_field = parameters.get(client,"function_class_field")
function_class_rid_field = parameters.get(client,"function_class_rid_field")
function_class_from_meas_field = parameters.get(client,"function_class_from_meas_field")
function_class_to_meas_field = parameters.get(client,"function_class_to_meas_field")
function_class_from_date_field = parameters.get(client,"function_class_from_date_field")
function_class_to_date_field = parameters.get(client,"function_class_to_date_field")

aadt_event = parameters.get(client,"aadt_event")
aadt_field = parameters.get(client,"aadt_field")
aadt_rid_field = parameters.get(client,"aadt_rid_field")
aadt_from_meas_field = parameters.get(client,"aadt_from_meas_field")
aadt_to_meas_field = parameters.get(client,"aadt_to_meas_field")
aadt_from_date_field = parameters.get(client,"aadt_from_date_field")
aadt_to_date_field = parameters.get(client,"aadt_to_date_field")

intersection_approach_id_field = schemas.get("intersection_approach_id_field")
intersection_approach_leg_id_field = schemas.get("intersection_approach_leg_id_field")
intersection_approach_leg_type_field = schemas.get("intersection_approach_leg_type_field")
intersection_approach_leg_dir_field = schemas.get("intersection_approach_leg_dir_field")
intersection_approach_angle_field = schemas.get("intersection_approach_angle_field")
intersection_approach_beg_inf_field = schemas.get("intersection_approach_beg_inf_field")
intersection_approach_end_inf_field = schemas.get("intersection_approach_end_inf_field")

from_date_field = schemas.get("from_date_field")
to_date_field = schemas.get("to_date_field")
# -----------------------------------------------------------------------------------------------

# Configuration ---------------------------------------------------------------------------------
search_radius = parameters.get(client, "search_radius")
measure_scale = int(parameters.get(client, "measure_scale"))
angle_calculation_distance = extract_number_from_string(parameters.get(client, "angle_calculation_distance"))[0] / 5280
area_of_influence = extract_number_from_string(parameters.get(client, "area_of_influence"))[0] / 5280
azumith_zero_direction = parameters.get(client, "azumith_zero_direction")
#-----------------------------------------------------------------------------------------------

# intermediate data ----------------------------
current_active_network_layer = "current_active_network_layer"
previous_active_network_layer = "previous_active_network_layer"

inserted_network_layer = "inserted_network_layer"
updated_before_network_layer = "updated_before_network_layer"
updated_after_network_layer = "updated_after_network_layer"
deleted_network_layer = "deleted_network_layer"

tba_current_network_layer = "tba_current_network_layer"
tba_current_intersections = "tba_current_intersections"
current_along_tba_route_inters_layer = "current_along_tba_route_inters_layer"
new_intersections = "in_memory\\new_intersections"
new_intersections_layer = "new_intersections_layer"
real_new_intersections = "in_memory\\real_new_intersections"

tba_previous_network_layer = "tba_previous_network_layer"
tba_previous_intersections = "tba_previous_intersections"
previous_along_tba_route_inters_layer = "previous_along_tba_route_inters_layer"
old_intersections = "in_memory\\old_intersections"
old_intersections_layer = "old_intersections_layer"
real_old_intersections = "in_memory\\real_old_intersections"

tbr_intersection_layer = "tbr_intersection_layer"
new_active_intersection_layer = "new_active_intersection_layer"

# Intersection Route Event
re_tba_current_intersection_layer = "re_tba_current_intersection_layer"
re_tba_current_network_layer = "re_tba_current_network_layer"
new_intersection_route_event = "in_memory\\new_intersection_route_event"
re_tba_previous_intersection_layer = "re_tba_previous_intersection_layer"
new_active_intersection_route_event_layer = "new_active_intersection_route_event_layer"

# Roadway Segment Event
rs_tba_current_network_layer = "rs_tba_current_network_layer"
rs_tba_current_intersection_layer = "rs_tba_current_intersection_layer"
new_roadway_segment_event = "in_memory\\new_roadway_segment_event"
rs_tba_previous_network_layer = "rs_tba_previous_network_layer"
new_active_roadway_segment_event_layer = "new_active_roadway_segment_event_layer"
ia_tba_current_segment_event_layer = "ia_tba_current_segment_event_layer"

# Intersection Approach Event
ia_tba_current_intersection_layer = "ia_tba_current_intersection_layer"
new_intersection_approach_event = "in_memory\\new_intersection_approach_event"
ia_tba_previous_intersection_layer = "ia_tba_previous_intersection_layer"
ia_tba_current_network_layer = "ia_tba_current_network_layer"
ia_tba_current_intersection_route_event_layer = "ia_tba_current_intersection_route_event_layer"

active_current_function_class_layer = "active_current_function_class_layer"
active_current_aadt_layer = "active_current_aadt_layer"

created_network_layer = "created_network_layer"
retired_network_layer = "retired_network_layer"

old_active_intersection_layer = "old_active_intersection_layer"
old_active_intersection_route_event_layer = "old_active_intersection_route_event_layer"
old_active_segment_layer = "old_active_segment_layer"
old_active_intersection_approach_layer = "old_active_intersection_approach_layer"

created_retired_function_class_layer = "created_retired_function_class_layer"
created_retired_aadt_layer = "created_retired_aadt_layer"
#-----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

def check_intersection_event_updates(workspace, input_date):
    # global variables
    global tba_current_intersections

    # Parameter and schema settings
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False

    # Read Parameters and User Input -----------------------------------------------------------------------
    last_update_date = format_sql_date(input_date, dbtype)
    # ------------------------------------------------------------------------------------------------------

    # Source Data -----------------------------------------------------------------------------------------
    intersection_event = os.path.join(workspace,schemas.get("intersection_event"))
    intersection_route_event = os.path.join(workspace,schemas.get("intersection_route_event"))
    roadway_segment_event = os.path.join(workspace,schemas.get("roadway_segment_event"))
    intersection_approach_event = os.path.join(workspace,schemas.get("intersection_approach_event"))
    # -----------------------------------------------------------------------------------------------

    # Important parameters-------------------------
    today_date_string = time.strftime('%m/%d/%Y')
    current_active_network_string = "({0} is null or {0} <= CURRENT_TIMESTAMP) and ({1} is null or {1} > CURRENT_TIMESTAMP)".format(network_from_date_field, network_to_date_field)
    previous_active_network_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(network_from_date_field, network_to_date_field, last_update_date)
    network_created_since_date_string = "%s > %s" % (network_from_date_field, last_update_date)
    network_retired_since_date_string = "%s > %s" % (network_to_date_field, last_update_date)
    function_class_created_since_date_string = "%s > %s" % (function_class_from_date_field, last_update_date) if function_class_from_date_field else ""
    function_class_retired_since_date_string = "%s > %s" % (function_class_to_date_field, last_update_date) if function_class_to_date_field else ""
    aadt_created_since_date_string = "%s > %s" % (aadt_from_date_field, last_update_date) if aadt_from_date_field else ""
    aadt_retired_since_date_string = "%s > %s" % (aadt_to_date_field, last_update_date) if aadt_to_date_field else ""
    active_string = "%s is NULL" % to_date_field
    old_active_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(from_date_field, to_date_field, last_update_date)
    retired_route_ids = []
    created_route_ids = []
    created_retired_function_class_exist = False
    created_retired_aadt_exist = False
    #-----------------------------------------------

    # Data preprocessing-----------------------------------------------------------------
    query_date_string = "CURRENT_TIMESTAMP"
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(function_class_from_date_field, function_class_to_date_field, query_date_string) if function_class_from_date_field and function_class_to_date_field else ""
    arcpy.MakeFeatureLayer_management(function_class_event, active_current_function_class_layer, query_filter)
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(aadt_from_date_field, aadt_to_date_field, query_date_string) if aadt_from_date_field and aadt_to_date_field else ""
    arcpy.MakeFeatureLayer_management(aadt_event, active_current_aadt_layer, query_filter)
    # -------------------------------------------------------------------------------------

    """
    Get All Differences Between Previous and Current Dataset
    """

    arcpy.MakeFeatureLayer_management(network, previous_active_network_layer, previous_active_network_string)
    # Create current network layer
    arcpy.MakeFeatureLayer_management(network, current_active_network_layer, current_active_network_string)

    # Create created network layer since the last_update_date and get a list created route ids
    arcpy.MakeFeatureLayer_management(network, created_network_layer, network_created_since_date_string)
    with arcpy.da.SearchCursor(created_network_layer, [network_route_id_field]) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            if route_id not in created_route_ids:
                created_route_ids.append(route_id)
    # Create retired network layer and the retired route ids.
    arcpy.MakeFeatureLayer_management(network, retired_network_layer, network_retired_since_date_string)
    with arcpy.da.SearchCursor(retired_network_layer, [network_route_id_field]) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            if route_id not in retired_route_ids:
                retired_route_ids.append(route_id)
    # Get the updated and retired route ids based on the updated functional class and aadt
    if function_class_from_date_field and function_class_to_date_field:
        if subset_data_exist(function_class_event, "%s or %s" % (function_class_created_since_date_string, function_class_retired_since_date_string)):
            created_retired_function_class_exist = True
    if aadt_from_date_field and aadt_from_date_field:
        if subset_data_exist(aadt_event, "%s or %s" % (aadt_created_since_date_string, aadt_retired_since_date_string)):
            created_retired_aadt_exist = True

    if len(created_route_ids) == 0 and len(retired_route_ids) == 0 and not created_retired_function_class_exist and not created_retired_aadt_exist:
        logger.warning("No change/update has been made since %s" % last_update_date)
        logger.info("Finished checking change/update")
        return False
    else:
        logger.info("Finished checking change/update")
        return True
    #-------------------------------------------------------------------------------------------------------------------------------


def update_intersection_event(workspace, input_date):
    # global variables
    global tba_previous_intersections
    global tba_current_intersections

    # Parameter and schema settings
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False

    # Read Parameters and User Input -----------------------------------------------------------------------
    last_update_date = format_sql_date(input_date, dbtype)
    # ------------------------------------------------------------------------------------------------------

    # Source Data -----------------------------------------------------------------------------------------
    intersection_event = os.path.join(workspace,schemas.get("intersection_event"))
    intersection_route_event = os.path.join(workspace,schemas.get("intersection_route_event"))
    roadway_segment_event = os.path.join(workspace,schemas.get("roadway_segment_event"))
    intersection_approach_event = os.path.join(workspace,schemas.get("intersection_approach_event"))
    # -----------------------------------------------------------------------------------------------

    # Important parameters-------------------------
    today_date_string = time.strftime('%m/%d/%Y')
    current_active_network_string = "({0} is null or {0} <= CURRENT_TIMESTAMP) and ({1} is null or {1} > CURRENT_TIMESTAMP)".format(network_from_date_field, network_to_date_field)
    previous_active_network_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(network_from_date_field, network_to_date_field, last_update_date)
    network_created_since_date_string = "%s > %s" % (network_from_date_field, last_update_date)
    network_retired_since_date_string = "%s > %s" % (network_to_date_field, last_update_date)
    function_class_created_since_date_string = "%s > %s" % (function_class_from_date_field, last_update_date) if function_class_from_date_field else ""
    function_class_retired_since_date_string = "%s > %s" % (function_class_to_date_field, last_update_date) if function_class_to_date_field else ""
    aadt_created_since_date_string = "%s > %s" % (aadt_from_date_field, last_update_date) if aadt_from_date_field else ""
    aadt_retired_since_date_string = "%s > %s" % (aadt_to_date_field, last_update_date) if aadt_to_date_field else ""
    active_string = "%s is NULL" % to_date_field
    old_active_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(from_date_field, to_date_field, last_update_date)
    retired_route_ids = []
    created_route_ids = []
    created_retired_function_class_exist = False
    created_retired_aadt_exist = False
    #-----------------------------------------------

    # Data preprocessing-----------------------------------------------------------------
    query_date_string = "CURRENT_TIMESTAMP"
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(function_class_from_date_field, function_class_to_date_field, query_date_string) if function_class_from_date_field and function_class_to_date_field else ""
    arcpy.MakeFeatureLayer_management(function_class_event, active_current_function_class_layer, query_filter)
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(aadt_from_date_field, aadt_to_date_field, query_date_string) if aadt_from_date_field and aadt_to_date_field else ""
    arcpy.MakeFeatureLayer_management(aadt_event, active_current_aadt_layer, query_filter)
    # -------------------------------------------------------------------------------------

    """
    Get All Differences Between Previous and Current Dataset
    """
    arcpy.MakeFeatureLayer_management(network, previous_active_network_layer, previous_active_network_string)
    # Create current network layer
    arcpy.MakeFeatureLayer_management(network, current_active_network_layer, current_active_network_string)

    # Create created network layer since the last_update_date and get a list created route ids
    arcpy.MakeFeatureLayer_management(network, created_network_layer, network_created_since_date_string)
    with arcpy.da.SearchCursor(created_network_layer, [network_route_id_field]) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            if route_id not in created_route_ids:
                created_route_ids.append(route_id)
    # Create retired network layer and the retired route ids.
    arcpy.MakeFeatureLayer_management(network, retired_network_layer, network_retired_since_date_string)
    with arcpy.da.SearchCursor(retired_network_layer, [network_route_id_field]) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            if route_id not in retired_route_ids:
                retired_route_ids.append(route_id)

    #Created network at all states ----------------------------------------------------------------------------------------------
    inserted_route_ids = list(set(created_route_ids) - set(retired_route_ids))
    updated_route_ids = list(set(created_route_ids) & set(retired_route_ids))
    deleted_route_ids = list(set(retired_route_ids) - set(created_route_ids))
    arcpy.MakeFeatureLayer_management(current_active_network_layer, inserted_network_layer, build_string_in_sql_expression(network_route_id_field, inserted_route_ids))
    arcpy.MakeFeatureLayer_management(current_active_network_layer, updated_after_network_layer, build_string_in_sql_expression(network_route_id_field, updated_route_ids))
    arcpy.MakeFeatureLayer_management(previous_active_network_layer, updated_before_network_layer, build_string_in_sql_expression(network_route_id_field, updated_route_ids))
    arcpy.MakeFeatureLayer_management(previous_active_network_layer, deleted_network_layer, build_string_in_sql_expression(network_route_id_field, deleted_route_ids))
    #------------------------------------------------------------------------------------------------------------------------------

    """
    Update Intersection_Event
    """

    # The tba_current_network should include 1) inserted routes 2) updated after routes 3) routes intersecting inserted routes
    # 4) routes intersecting updated after routes 5) routes intersecting deleted routes
    arcpy.MakeFeatureLayer_management(current_active_network_layer, tba_current_network_layer)
    arcpy.SelectLayerByLocation_management(tba_current_network_layer, "INTERSECT", inserted_network_layer, search_radius, "NEW_SELECTION")
    arcpy.SelectLayerByLocation_management(tba_current_network_layer, "INTERSECT", updated_after_network_layer, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByLocation_management(tba_current_network_layer, "INTERSECT", deleted_network_layer, search_radius, "ADD_TO_SELECTION")
    # Generate tba_current_intersections
    intersection_event_instance_new = intersection_event_mod.IntersectionEvent(
        network=tba_current_network_layer,
        network_route_id_field=network_route_id_field,
        intersection_event=tba_current_intersections,
        intersection_id_field=intersection_id_field,
        search_radius=search_radius
    )

    tba_current_intersections = intersection_event_instance_new.detect_intersections()
    arcpy.CopyFeatures_management(tba_current_intersections, new_intersections)
    arcpy.MakeFeatureLayer_management(new_intersections, current_along_tba_route_inters_layer)
    arcpy.SelectLayerByLocation_management(current_along_tba_route_inters_layer, "INTERSECT", inserted_network_layer, search_radius, "NEW_SELECTION")
    arcpy.SelectLayerByLocation_management(current_along_tba_route_inters_layer, "INTERSECT", updated_after_network_layer, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByLocation_management(current_along_tba_route_inters_layer, "INTERSECT", deleted_network_layer, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByAttribute_management(current_along_tba_route_inters_layer, "SWITCH_SELECTION")
    arcpy.DeleteRows_management(current_along_tba_route_inters_layer)
    arcpy.Delete_management(tba_current_intersections)

    # The tba_previous_network should include 1) deleted routes 2) updated before routes 3) routes intersecting deleted routes
    # 4) routes intersecting updated before routes 5) routes intersecting inserted routes
    arcpy.MakeFeatureLayer_management(previous_active_network_layer, tba_previous_network_layer)
    arcpy.SelectLayerByLocation_management(tba_previous_network_layer, "INTERSECT", updated_before_network_layer, search_radius, "NEW_SELECTION")
    arcpy.SelectLayerByLocation_management(tba_previous_network_layer, "INTERSECT", deleted_network_layer, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByLocation_management(tba_previous_network_layer, "INTERSECT", inserted_network_layer, search_radius, "ADD_TO_SELECTION")
    intersection_event_instance_retire = intersection_event_mod.IntersectionEvent(
        network=tba_previous_network_layer,
        network_route_id_field=network_route_id_field,
        intersection_event=tba_previous_intersections,
        intersection_id_field=intersection_id_field,
        search_radius=search_radius
    )
    tba_previous_intersections = intersection_event_instance_retire.detect_intersections()
    arcpy.CopyFeatures_management(tba_previous_intersections, old_intersections)
    arcpy.MakeFeatureLayer_management(old_intersections, previous_along_tba_route_inters_layer)
    arcpy.SelectLayerByLocation_management(previous_along_tba_route_inters_layer, "INTERSECT", deleted_network_layer, search_radius, "NEW_SELECTION")
    arcpy.SelectLayerByLocation_management(previous_along_tba_route_inters_layer, "INTERSECT", updated_before_network_layer, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByAttribute_management(previous_along_tba_route_inters_layer, "SWITCH_SELECTION")
    arcpy.DeleteRows_management(previous_along_tba_route_inters_layer)
    arcpy.Delete_management(tba_previous_intersections)

    # Identify new intersections / old intersections by geometry
    arcpy.MakeFeatureLayer_management(new_intersections, new_intersections_layer)
    arcpy.SelectLayerByLocation_management(new_intersections_layer, "INTERSECT", old_intersections, search_radius, "NEW_SELECTION")
    arcpy.SelectLayerByAttribute_management(new_intersections_layer, "SWITCH_SELECTION")
    arcpy.Select_analysis(new_intersections_layer, real_new_intersections)
    arcpy.MakeFeatureLayer_management(old_intersections, old_intersections_layer)
    arcpy.SelectLayerByLocation_management(old_intersections_layer, "INTERSECT", new_intersections, search_radius, "NEW_SELECTION")
    arcpy.SelectLayerByAttribute_management(old_intersections_layer, "SWITCH_SELECTION")
    arcpy.Select_analysis(old_intersections_layer, real_old_intersections)

    # Mark retired in the Intersection_Event feature class
    arcpy.MakeFeatureLayer_management(intersection_event, old_active_intersection_layer, old_active_string)
    arcpy.MakeFeatureLayer_management(old_active_intersection_layer, tbr_intersection_layer)
    arcpy.SelectLayerByLocation_management(tbr_intersection_layer, "INTERSECT", real_old_intersections, search_radius, "NEW_SELECTION")
    arcpy.CalculateField_management(tbr_intersection_layer, to_date_field, "Date()")

    # Append new intersections to the Intersection_Event feature class
    arcpy.Append_management(real_new_intersections, intersection_event, "NO_TEST")
    max_intersection_id = get_maximum_id(intersection_event, intersection_id_field)
    with arcpy.da.UpdateCursor(intersection_event, [intersection_id_field, from_date_field], "%s is NULL" % from_date_field) as uCursor:
        for uRow in uCursor:
            max_intersection_id += 1
            uRow[0] = str(max_intersection_id)
            uRow[1] = today_date_string
            uCursor.updateRow(uRow)

    # Delete Duplicated Records
    delete_identical_only_keep_min_oid(intersection_event, [arcpy.Describe(intersection_event).shapeFieldName])

    logger.info("Finished updating intersection event")
    #-------------------------------------------------------------------------------------------------------------------


def get_new_intersection_event(workspace,input_date):
    # Parameter and schema settings
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False

    # Read Parameters and User Input -----------------------------------------------------------------------
    last_update_date = format_sql_date(input_date, dbtype)
    # ------------------------------------------------------------------------------------------------------

    # Source Data -----------------------------------------------------------------------------------------
    intersection_event = os.path.join(workspace,schemas.get("intersection_event"))
    intersection_route_event = os.path.join(workspace,schemas.get("intersection_route_event"))
    roadway_segment_event = os.path.join(workspace,schemas.get("roadway_segment_event"))
    intersection_approach_event = os.path.join(workspace,schemas.get("intersection_approach_event"))
    # -----------------------------------------------------------------------------------------------

    # Important parameters-------------------------
    today_date_string = time.strftime('%m/%d/%Y')
    current_active_network_string = "({0} is null or {0} <= CURRENT_TIMESTAMP) and ({1} is null or {1} > CURRENT_TIMESTAMP)".format(network_from_date_field, network_to_date_field)
    previous_active_network_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(network_from_date_field, network_to_date_field, last_update_date)
    network_created_since_date_string = "%s > %s" % (network_from_date_field, last_update_date)
    network_retired_since_date_string = "%s > %s" % (network_to_date_field, last_update_date)
    function_class_created_since_date_string = "%s > %s" % (function_class_from_date_field, last_update_date) if function_class_from_date_field else ""
    function_class_retired_since_date_string = "%s > %s" % (function_class_to_date_field, last_update_date) if function_class_to_date_field else ""
    aadt_created_since_date_string = "%s > %s" % (aadt_from_date_field, last_update_date) if aadt_from_date_field else ""
    aadt_retired_since_date_string = "%s > %s" % (aadt_to_date_field, last_update_date) if aadt_to_date_field else ""
    active_string = "%s is NULL" % to_date_field
    old_active_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(from_date_field, to_date_field, last_update_date)
    retired_route_ids = []
    created_route_ids = []
    created_retired_function_class_exist = False
    created_retired_aadt_exist = False
    #-----------------------------------------------

    # Data preprocessing-----------------------------------------------------------------
    query_date_string = "CURRENT_TIMESTAMP"
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(function_class_from_date_field, function_class_to_date_field, query_date_string) if function_class_from_date_field and function_class_to_date_field else ""
    arcpy.MakeFeatureLayer_management(function_class_event, active_current_function_class_layer, query_filter)
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(aadt_from_date_field, aadt_to_date_field, query_date_string) if aadt_from_date_field and aadt_to_date_field else ""
    arcpy.MakeFeatureLayer_management(aadt_event, active_current_aadt_layer, query_filter)
    # -------------------------------------------------------------------------------------

    # make a copy of network. Following operations will base on this copy.
    copied_network = "copied_network"
    arcpy.CopyFeatures_management(network,copied_network)

    # Create a previous active network layer. This is corresponding to the current state of all the intersection tables
    arcpy.MakeFeatureLayer_management(copied_network, previous_active_network_layer, previous_active_network_string)
    # Create current network layer
    arcpy.MakeFeatureLayer_management(copied_network, current_active_network_layer, current_active_network_string)

    """
    Get new intersection events
    """
    logger.info("Get new intersection events for user review")

    intersections = []

    # generate intersection layers for review
    new_intersection_string = "%s > %s" % (from_date_field, last_update_date)
    new_created_intersections = "new_created_intersections"
    arcpy.MakeFeatureLayer_management(intersection_event,new_created_intersections,new_intersection_string)

    count = arcpy.GetCount_management(new_created_intersections)
    if int(count.getOutput(0)):
        retired_intersection_string = "({0} >= {1}) AND ({0} <= CURRENT_TIMESTAMP)".format(to_date_field, last_update_date)
        new_retired_intersections = "new_retired_intersections"
        arcpy.MakeFeatureLayer_management(intersection_event,new_retired_intersections,retired_intersection_string)

        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = mxd.activeDataFrame

        # add layers to map document
        new_created_intersections_lyr = arcpy.mapping.Layer(new_created_intersections)
        arcpy.mapping.AddLayer(df,new_created_intersections_lyr,"BOTTOM")

        new_retired_intersections_lyr = arcpy.mapping.Layer(new_retired_intersections)
        arcpy.mapping.AddLayer(df,new_retired_intersections_lyr,"BOTTOM")

        current_active_network_layer_lyr = arcpy.mapping.Layer(current_active_network_layer)
        arcpy.mapping.AddLayer(df,current_active_network_layer_lyr,"BOTTOM")

        previous_active_network_layer_lyr = arcpy.mapping.Layer(previous_active_network_layer)
        arcpy.mapping.AddLayer(df,previous_active_network_layer_lyr,"BOTTOM")

        arcpy.RefreshActiveView()
        arcpy.RefreshTOC()

        # del new_created_intersections_lyr,new_retired_intersections_lyr,current_active_network_layer_lyr,previous_active_network_layer_lyr

        # Get new intersections -------------------------------------------------------------------------------
        with arcpy.da.UpdateCursor(new_created_intersections,["OBJECTID","Intersection_ID"]) as uCursor:
            for row in uCursor:
                tmp = []
                for value in row:
                    tmp.append(str(value))
                tmp.append("")
                intersections.append(tmp)
        del uCursor

    return intersections
    #-------------------------------------------------------------------------------------------------------------------


def update_new_intersection_id(workspace,input_date, updated_intersections):
    # Parameter and schema settings
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False

    # Source Data -----------------------------------------------------------------------------------------
    intersection_event = os.path.join(workspace,schemas.get("intersection_event"))
    # -----------------------------------------------------------------------------------------------

    """
    Apply user assigned new intersection ids
    """

    logger.info("Apply user assigned new intersection ids")

    keys = updated_intersections.keys()
    where_clause = "OBJECTID IN ("+",".join(keys)+")"

    with arcpy.da.UpdateCursor(intersection_event,["OBJECTID","Intersection_ID"],where_clause) as uCursor:
        for row in uCursor:
            oid = row[0]
            row[1] = updated_intersections[str(oid)]
            uCursor.updateRow(row)
    del uCursor

    logger.info("Finished updating user assigned new intersection ids")
    #------------------------------------------------------------------------------------------------------------------


def update_intersection_route_event(workspace, input_date):
    # global variables
    global new_intersection_route_event

    # Parameter and schema settings
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False

    # Read Parameters and User Input -----------------------------------------------------------------------
    last_update_date = format_sql_date(input_date, dbtype)
    # ------------------------------------------------------------------------------------------------------

    # Source Data -----------------------------------------------------------------------------------------
    intersection_event = os.path.join(workspace,schemas.get("intersection_event"))
    intersection_route_event = os.path.join(workspace,schemas.get("intersection_route_event"))
    roadway_segment_event = os.path.join(workspace,schemas.get("roadway_segment_event"))
    intersection_approach_event = os.path.join(workspace,schemas.get("intersection_approach_event"))
    # -----------------------------------------------------------------------------------------------

    # Important parameters-------------------------
    today_date_string = time.strftime('%m/%d/%Y')
    current_active_network_string = "({0} is null or {0} <= CURRENT_TIMESTAMP) and ({1} is null or {1} > CURRENT_TIMESTAMP)".format(network_from_date_field, network_to_date_field)
    previous_active_network_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(network_from_date_field, network_to_date_field, last_update_date)
    network_created_since_date_string = "%s > %s" % (network_from_date_field, last_update_date)
    network_retired_since_date_string = "%s > %s" % (network_to_date_field, last_update_date)
    function_class_created_since_date_string = "%s > %s" % (function_class_from_date_field, last_update_date) if function_class_from_date_field else ""
    function_class_retired_since_date_string = "%s > %s" % (function_class_to_date_field, last_update_date) if function_class_to_date_field else ""
    aadt_created_since_date_string = "%s > %s" % (aadt_from_date_field, last_update_date) if aadt_from_date_field else ""
    aadt_retired_since_date_string = "%s > %s" % (aadt_to_date_field, last_update_date) if aadt_to_date_field else ""
    active_string = "%s is NULL" % to_date_field
    old_active_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(from_date_field, to_date_field, last_update_date)
    retired_route_ids = []
    created_route_ids = []
    created_retired_function_class_exist = False
    created_retired_aadt_exist = False
    #-----------------------------------------------

    # Data preprocessing-----------------------------------------------------------------
    query_date_string = "CURRENT_TIMESTAMP"
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(function_class_from_date_field, function_class_to_date_field, query_date_string) if function_class_from_date_field and function_class_to_date_field else ""
    arcpy.MakeFeatureLayer_management(function_class_event, active_current_function_class_layer, query_filter)
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(aadt_from_date_field, aadt_to_date_field, query_date_string) if aadt_from_date_field and aadt_to_date_field else ""
    arcpy.MakeFeatureLayer_management(aadt_event, active_current_aadt_layer, query_filter)
    # -------------------------------------------------------------------------------------

    # Create a previous active network layer. This is corresponding to the current state of all the intersection tables
    arcpy.MakeFeatureLayer_management(network, previous_active_network_layer, previous_active_network_string)
    # Create current network layer
    arcpy.MakeFeatureLayer_management(network, current_active_network_layer, current_active_network_string)

    # Create created network layer since the last_update_date and get a list created route ids
    arcpy.MakeFeatureLayer_management(network, created_network_layer, network_created_since_date_string)
    with arcpy.da.SearchCursor(created_network_layer, [network_route_id_field]) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            if route_id not in created_route_ids:
                created_route_ids.append(route_id)
    # Create retired network layer and the retired route ids.
    arcpy.MakeFeatureLayer_management(network, retired_network_layer, network_retired_since_date_string)
    with arcpy.da.SearchCursor(retired_network_layer, [network_route_id_field]) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            if route_id not in retired_route_ids:
                retired_route_ids.append(route_id)
    # Get the updated and retired route ids based on the updated functional class and aadt
    if function_class_from_date_field and function_class_to_date_field:
        if subset_data_exist(function_class_event, "%s or %s" % (function_class_created_since_date_string, function_class_retired_since_date_string)):
            created_retired_function_class_exist = True
    if aadt_from_date_field and aadt_from_date_field:
        if subset_data_exist(aadt_event, "%s or %s" % (aadt_created_since_date_string, aadt_retired_since_date_string)):
            created_retired_aadt_exist = True

    #Created network at all states ----------------------------------------------------------------------------------------------
    inserted_route_ids = list(set(created_route_ids) - set(retired_route_ids))
    updated_route_ids = list(set(created_route_ids) & set(retired_route_ids))
    deleted_route_ids = list(set(retired_route_ids) - set(created_route_ids))
    arcpy.MakeFeatureLayer_management(current_active_network_layer, inserted_network_layer, build_string_in_sql_expression(network_route_id_field, inserted_route_ids))
    arcpy.MakeFeatureLayer_management(current_active_network_layer, updated_after_network_layer, build_string_in_sql_expression(network_route_id_field, updated_route_ids))
    arcpy.MakeFeatureLayer_management(previous_active_network_layer, updated_before_network_layer, build_string_in_sql_expression(network_route_id_field, updated_route_ids))
    arcpy.MakeFeatureLayer_management(previous_active_network_layer, deleted_network_layer, build_string_in_sql_expression(network_route_id_field, deleted_route_ids))
    #------------------------------------------------------------------------------------------------------------------------------

    """
    Update Intersection_Route_Event
    """

    # Recreate the active intersections
    arcpy.MakeFeatureLayer_management(intersection_event, new_active_intersection_layer, active_string)
    # Keep a copy of old active intersections
    arcpy.MakeFeatureLayer_management(intersection_event, old_active_intersection_layer, old_active_string)

    # to be analysis current intersections should include 1) intersections along inserted routes 3) intersections along updated after routes 3)intersections intersected with deleted routes but still active
    arcpy.MakeFeatureLayer_management(new_active_intersection_layer, re_tba_current_intersection_layer)
    arcpy.SelectLayerByLocation_management(re_tba_current_intersection_layer, "INTERSECT", inserted_network_layer, search_radius, "NEW_SELECTION")
    arcpy.SelectLayerByLocation_management(re_tba_current_intersection_layer, "INTERSECT", updated_after_network_layer, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByLocation_management(re_tba_current_intersection_layer, "INTERSECT", deleted_network_layer, search_radius, "ADD_TO_SELECTION")
    # to be analysis network is the same as tba_current_network_layer
    arcpy.MakeFeatureLayer_management(tba_current_network_layer, re_tba_current_network_layer)

    intersection_route_event_instance_new = intersection_route_event_mod.IntersectionRouteEvent(
        network=re_tba_current_network_layer,
        network_route_id_field=network_route_id_field,
        network_route_name_field=network_route_name_field,
        intersection_event=re_tba_current_intersection_layer,
        intersection_id_field=intersection_id_field,
        intersection_route_event=new_intersection_route_event,
        intersection_route_on_rid_field=intersection_route_on_rid_field,
        intersection_route_on_rname_field=intersection_route_on_rname_field,
        intersection_route_on_measure_field=intersection_route_on_measure_field,
        intersection_route_at_rid_field=intersection_route_at_rid_field,
        intersection_route_at_rname_field=intersection_route_at_rname_field,
        measure_scale=measure_scale,
        search_radius=search_radius
    )
    new_intersection_route_event = intersection_route_event_instance_new.create_intersection_route_event()
    inter__route__at_route__measure_name_dict = {}
    with arcpy.da.SearchCursor(new_intersection_route_event,
                               [intersection_id_field, intersection_route_on_rid_field, intersection_route_on_measure_field, intersection_route_on_rname_field, intersection_route_at_rid_field, intersection_route_at_rname_field]) as sCursor:
        for sRow in sCursor:
            intersection_id, on_route_id, on_route_measure, on_route_name, at_route_id, at_route_name = sRow[0], sRow[1], sRow[2], sRow[3], sRow[4], sRow[5]
            if intersection_id not in inter__route__at_route__measure_name_dict:
                inter__route__at_route__measure_name_dict[intersection_id] = {}
            if on_route_id not in inter__route__at_route__measure_name_dict[intersection_id]:
                inter__route__at_route__measure_name_dict[intersection_id][on_route_id] = {}
            inter__route__at_route__measure_name_dict[intersection_id][on_route_id][at_route_id] = {
                "On_Route_Measure": on_route_measure,
                "On_Route_Name": on_route_name,
                "At_Route_Name": at_route_name,
                "Processed": False
            }
    # Find records related with old routes
    # If attributes remain the same, marked as processed; else marked it as retired
    # to be analysis current intersections should include 1) intersections along updated before routes 2)intersections along deleted route 3) old active but intersected with the inserted routes
    arcpy.MakeFeatureLayer_management(old_active_intersection_layer, re_tba_previous_intersection_layer)
    arcpy.SelectLayerByLocation_management(re_tba_previous_intersection_layer, "INTERSECT", updated_before_network_layer, search_radius, "NEW_SELECTION")
    arcpy.SelectLayerByLocation_management(re_tba_previous_intersection_layer, "INTERSECT", deleted_network_layer, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByLocation_management(re_tba_previous_intersection_layer, "INTERSECT", inserted_network_layer, search_radius, "ADD_TO_SELECTION")
    with arcpy.da.SearchCursor(re_tba_previous_intersection_layer, intersection_id_field) as sCursor:
        re_tba_intersection_ids = [sRow[0] for sRow in sCursor]
    re_tba_intersection_where_clause = build_string_in_sql_expression(intersection_id_field, re_tba_intersection_ids)
    # Select the corresponding intersection-related record in the existing and active intersection_route_event
    arcpy.MakeTableView_management(intersection_route_event, old_active_intersection_route_event_layer, old_active_string)
    with arcpy.da.UpdateCursor(old_active_intersection_route_event_layer,
                               [intersection_id_field, intersection_route_on_rid_field, intersection_route_on_measure_field, intersection_route_on_rname_field, intersection_route_at_rid_field, intersection_route_at_rname_field, to_date_field],
                               re_tba_intersection_where_clause) as uCursor:
        for uRow in uCursor:
            intersection_id, on_route_id, on_route_measure, on_route_name, at_route_id, at_route_name = uRow[0], uRow[1], uRow[2], uRow[3], uRow[4], uRow[5]
            # Heads up! Need to handle a ESRI bug is calculating the starting measure as some weird number -2.394324e-11
            # Find a more generic way to do this
            if on_route_measure:
                on_route_measure = round(on_route_measure, measure_scale)
            if intersection_id in inter__route__at_route__measure_name_dict and on_route_id in inter__route__at_route__measure_name_dict[intersection_id] and at_route_id in inter__route__at_route__measure_name_dict[intersection_id][on_route_id]:
                measure_name_dict = inter__route__at_route__measure_name_dict[intersection_id][on_route_id][at_route_id]
                if measure_name_dict["On_Route_Measure"] == on_route_measure and measure_name_dict["On_Route_Name"] == on_route_name and measure_name_dict["At_Route_Name"] == at_route_name:
                    measure_name_dict["Processed"] = True
                    continue
                else:
                    uRow[6] = today_date_string
                    uCursor.updateRow(uRow)
            else:
                uRow[6] = today_date_string
                uCursor.updateRow(uRow)
    # Insert unprocessed records
    with arcpy.da.InsertCursor(intersection_route_event, [intersection_id_field, intersection_route_on_rid_field, intersection_route_on_measure_field, intersection_route_on_rname_field,
                                                          intersection_route_at_rid_field, intersection_route_at_rname_field, from_date_field]) as iCursor:
        for intersection_id, route__at_route_measure_name_dict in inter__route__at_route__measure_name_dict.items():
            for route_id, at_route__measure_name_dict in route__at_route_measure_name_dict.items():
                for at_route_id, on_measure_name_dict in at_route__measure_name_dict.items():
                    if not on_measure_name_dict["Processed"]:
                        on_route_measure = on_measure_name_dict["On_Route_Measure"]
                        on_route_name = on_measure_name_dict["On_Route_Name"]
                        at_route_name = on_measure_name_dict["At_Route_Name"]
                        from_date = today_date_string
                        iCursor.insertRow((intersection_id, route_id, on_route_measure, on_route_name, at_route_id, at_route_name, from_date))

    # Delete Duplicated Records
    delete_identical_only_keep_min_oid(intersection_route_event, [intersection_id_field, intersection_route_on_rid_field, intersection_route_on_measure_field, intersection_route_on_rname_field, intersection_route_at_rid_field, intersection_route_at_rname_field])
    # Recreate the active intersection route event
    arcpy.MakeTableView_management(intersection_route_event, new_active_intersection_route_event_layer, active_string)

    logger.info("Finished updating intersection route event")


def update_roadway_segment_event(workspace, input_date):
    # global variables
    global new_roadway_segment_event

    # Parameter and schema settings
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False

    # Read Parameters and User Input -----------------------------------------------------------------------
    last_update_date = format_sql_date(input_date, dbtype)
    # ------------------------------------------------------------------------------------------------------

    # Source Data -----------------------------------------------------------------------------------------
    intersection_event = os.path.join(workspace,schemas.get("intersection_event"))
    intersection_route_event = os.path.join(workspace,schemas.get("intersection_route_event"))
    roadway_segment_event = os.path.join(workspace,schemas.get("roadway_segment_event"))
    intersection_approach_event = os.path.join(workspace,schemas.get("intersection_approach_event"))
    # -----------------------------------------------------------------------------------------------

    # Important parameters-------------------------
    today_date_string = time.strftime('%m/%d/%Y')
    current_active_network_string = "({0} is null or {0} <= CURRENT_TIMESTAMP) and ({1} is null or {1} > CURRENT_TIMESTAMP)".format(network_from_date_field, network_to_date_field)
    previous_active_network_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(network_from_date_field, network_to_date_field, last_update_date)
    network_created_since_date_string = "%s > %s" % (network_from_date_field, last_update_date)
    network_retired_since_date_string = "%s > %s" % (network_to_date_field, last_update_date)
    function_class_created_since_date_string = "%s > %s" % (function_class_from_date_field, last_update_date) if function_class_from_date_field else ""
    function_class_retired_since_date_string = "%s > %s" % (function_class_to_date_field, last_update_date) if function_class_to_date_field else ""
    aadt_created_since_date_string = "%s > %s" % (aadt_from_date_field, last_update_date) if aadt_from_date_field else ""
    aadt_retired_since_date_string = "%s > %s" % (aadt_to_date_field, last_update_date) if aadt_to_date_field else ""
    active_string = "%s is NULL" % to_date_field
    old_active_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(from_date_field, to_date_field, last_update_date)
    retired_route_ids = []
    created_route_ids = []
    created_retired_function_class_exist = False
    created_retired_aadt_exist = False
    #-----------------------------------------------

    # Data preprocessing-----------------------------------------------------------------
    query_date_string = "CURRENT_TIMESTAMP"
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(function_class_from_date_field, function_class_to_date_field, query_date_string) if function_class_from_date_field and function_class_to_date_field else ""
    arcpy.MakeFeatureLayer_management(function_class_event, active_current_function_class_layer, query_filter)
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(aadt_from_date_field, aadt_to_date_field, query_date_string) if aadt_from_date_field and aadt_to_date_field else ""
    arcpy.MakeFeatureLayer_management(aadt_event, active_current_aadt_layer, query_filter)
    # -------------------------------------------------------------------------------------

    # Create a previous active network layer. This is corresponding to the current state of all the intersection tables
    arcpy.MakeFeatureLayer_management(network, previous_active_network_layer, previous_active_network_string)
    # Create current network layer
    arcpy.MakeFeatureLayer_management(network, current_active_network_layer, current_active_network_string)

    # Create created network layer since the last_update_date and get a list created route ids
    arcpy.MakeFeatureLayer_management(network, created_network_layer, network_created_since_date_string)
    with arcpy.da.SearchCursor(created_network_layer, [network_route_id_field]) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            if route_id not in created_route_ids:
                created_route_ids.append(route_id)
    # Create retired network layer and the retired route ids.
    arcpy.MakeFeatureLayer_management(network, retired_network_layer, network_retired_since_date_string)
    with arcpy.da.SearchCursor(retired_network_layer, [network_route_id_field]) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            if route_id not in retired_route_ids:
                retired_route_ids.append(route_id)
    # Get the updated and retired route ids based on the updated functional class and aadt
    if function_class_from_date_field and function_class_to_date_field:
        if subset_data_exist(function_class_event, "%s or %s" % (function_class_created_since_date_string, function_class_retired_since_date_string)):
            created_retired_function_class_exist = True
    if aadt_from_date_field and aadt_from_date_field:
        if subset_data_exist(aadt_event, "%s or %s" % (aadt_created_since_date_string, aadt_retired_since_date_string)):
            created_retired_aadt_exist = True

    #Created network at all states ----------------------------------------------------------------------------------------------
    inserted_route_ids = list(set(created_route_ids) - set(retired_route_ids))
    updated_route_ids = list(set(created_route_ids) & set(retired_route_ids))
    deleted_route_ids = list(set(retired_route_ids) - set(created_route_ids))
    arcpy.MakeFeatureLayer_management(current_active_network_layer, inserted_network_layer, build_string_in_sql_expression(network_route_id_field, inserted_route_ids))
    arcpy.MakeFeatureLayer_management(current_active_network_layer, updated_after_network_layer, build_string_in_sql_expression(network_route_id_field, updated_route_ids))
    arcpy.MakeFeatureLayer_management(previous_active_network_layer, updated_before_network_layer, build_string_in_sql_expression(network_route_id_field, updated_route_ids))
    arcpy.MakeFeatureLayer_management(previous_active_network_layer, deleted_network_layer, build_string_in_sql_expression(network_route_id_field, deleted_route_ids))
    #------------------------------------------------------------------------------------------------------------------------------

    """
    Update Roadway_Segment_Event
    """

    # to be analyze current network should include 1) inserted routes 2) updated after routes
    # 3) routes intersecting the real_new_intersections 4) routes intersecting real_old_intersections
    arcpy.MakeFeatureLayer_management(current_active_network_layer, rs_tba_current_network_layer)
    arcpy.SelectLayerByAttribute_management(rs_tba_current_network_layer, "NEW_SELECTION", build_string_in_sql_expression(network_route_id_field, inserted_route_ids))
    arcpy.SelectLayerByAttribute_management(rs_tba_current_network_layer, "ADD_TO_SELECTION", build_string_in_sql_expression(network_route_id_field, updated_route_ids))
    arcpy.SelectLayerByLocation_management(rs_tba_current_network_layer, "INTERSECT", real_new_intersections, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByLocation_management(rs_tba_current_network_layer, "INTERSECT", real_old_intersections, search_radius, "ADD_TO_SELECTION")
    # to be analyze intersections should include 1) new active 2) along the rs_tba_network_layer
    arcpy.MakeFeatureLayer_management(new_active_intersection_layer, rs_tba_current_intersection_layer)
    arcpy.SelectLayerByLocation_management(rs_tba_current_intersection_layer, "INTERSECT", rs_tba_current_network_layer, search_radius, "NEW_SELECTION")

    roadway_segment_event_instance_new = roadway_segment_event_mod.RoadwaySegmentEvent(
        network=rs_tba_current_network_layer,
        network_route_id_field=network_route_id_field,
        network_route_name_field=network_route_name_field,
        intersection_event=rs_tba_current_intersection_layer,
        roadway_segment_event=new_roadway_segment_event,
        roadway_segment_id_field=roadway_segment_id_field,
        roadway_segment_rid_field=roadway_segment_rid_field,
        roadway_segment_from_meas_field=roadway_segment_from_meas_field,
        roadway_segment_to_meas_field=roadway_segment_to_meas_field,
        measure_scale=measure_scale,
        search_radius=search_radius
    )
    new_roadway_segment_event = roadway_segment_event_instance_new.create_roadway_segment_event()
    # Use a slightly different way to handle the "Processed", since there is geometry field involved
    # 1 stands for a row has already been processed
    arcpy.AddField_management(new_roadway_segment_event, "Processed", "SHORT")
    with arcpy.da.UpdateCursor(new_roadway_segment_event, "Processed") as uCursor:
        for uRow in uCursor:
            uRow[0] = 0  # not processed
            uCursor.updateRow(uRow)

    # Find the related roadway segments
    # Remember to include routes that has been retired
    # to be analyzed routes previous network should include 1) deleted routes  2) updated before routes
    # 3) routes intersecting the real_new_intersections 4) routes intersecting the real_old_intersections
    arcpy.MakeFeatureLayer_management(previous_active_network_layer, rs_tba_previous_network_layer)
    arcpy.SelectLayerByAttribute_management(rs_tba_previous_network_layer, "NEW_SELECTION", build_string_in_sql_expression(network_route_id_field, deleted_route_ids))
    arcpy.SelectLayerByAttribute_management(rs_tba_previous_network_layer, "ADD_TO_SELECTION", build_string_in_sql_expression(network_route_id_field, updated_route_ids))
    arcpy.SelectLayerByLocation_management(rs_tba_previous_network_layer, "INTERSECT", real_new_intersections, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByLocation_management(rs_tba_previous_network_layer, "INTERSECT", real_old_intersections, search_radius, "ADD_TO_SELECTION")
    with arcpy.da.SearchCursor(rs_tba_previous_network_layer, network_route_id_field) as sCursor:
        re_tba_route_ids = [sRow[0] for sRow in sCursor]
    re_tba_route_where_clause = build_string_in_sql_expression(roadway_segment_rid_field, re_tba_route_ids)
    # Select the corresponding route-related record in the existing and active roadway_segment_event
    arcpy.MakeFeatureLayer_management(roadway_segment_event, old_active_segment_layer, old_active_string)
    with arcpy.da.UpdateCursor(old_active_segment_layer,
                               ["SHAPE@", roadway_segment_rid_field, roadway_segment_from_meas_field, roadway_segment_to_meas_field, to_date_field],
                               re_tba_route_where_clause) as uCursor:
        for uRow in uCursor:
            old_segment_shape, old_route_id, old_segment_from_measure, old_segment_to_measure = uRow[0], uRow[1], uRow[2], uRow[3]
            with arcpy.da.UpdateCursor(new_roadway_segment_event,
                                       ["SHAPE@", roadway_segment_rid_field, roadway_segment_from_meas_field, roadway_segment_to_meas_field, "Processed"],
                                       "{0} = '{1}' and {2} = {3} and {4} = {5}".format(roadway_segment_rid_field, old_route_id, roadway_segment_from_meas_field, old_segment_from_measure, roadway_segment_to_meas_field, old_segment_to_measure)) as uNewCursor:
                try:
                    uNewRow = uNewCursor.next()
                    if uNewRow[0].equals(old_segment_shape):
                        uNewRow[4] = 1  # Marked the records as processed
                        uNewCursor.updateRow(uNewRow)
                    else:
                        uRow[4] = today_date_string
                        uCursor.updateRow(uRow)
                except StopIteration:
                    uRow[4] = today_date_string
                    uCursor.updateRow(uRow)

    max_segment_id = get_maximum_id(roadway_segment_event, roadway_segment_id_field)
    with arcpy.da.InsertCursor(roadway_segment_event, ["SHAPE@", roadway_segment_rid_field, roadway_segment_from_meas_field, roadway_segment_to_meas_field, roadway_segment_id_field, from_date_field]) as iCursor:
        with arcpy.da.SearchCursor(new_roadway_segment_event,
                                   ["SHAPE@", roadway_segment_rid_field, roadway_segment_from_meas_field, roadway_segment_to_meas_field],
                                   "%s = 0" % "Processed") as sCursor:
            for sRow in sCursor:
                max_segment_id += 1
                segment_shape, route_id, segment_from_measure, segment_to_measure = sRow[0], sRow[1], sRow[2], sRow[3]
                iCursor.insertRow((segment_shape, route_id, segment_from_measure, segment_to_measure, max_segment_id, today_date_string))

    # Delete Duplicated Records
    delete_identical_only_keep_min_oid(roadway_segment_event, [arcpy.Describe(roadway_segment_event).shapeFieldName, roadway_segment_rid_field, roadway_segment_from_meas_field, roadway_segment_to_meas_field])
    # recreate the active roadways segment event
    arcpy.MakeFeatureLayer_management(roadway_segment_event, new_active_roadway_segment_event_layer, active_string)

    logger.info("Finished updating roadway segment event")


def update_intersection_approach_event(workspace, input_date):
    # global variables
    global new_intersection_approach_event

    # Parameter and schema settings
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    arcpy.env.addOutputsToMap = False

    # Read Parameters and User Input -----------------------------------------------------------------------
    last_update_date = format_sql_date(input_date, dbtype)
    # ------------------------------------------------------------------------------------------------------

    # Source Data -----------------------------------------------------------------------------------------
    intersection_event = os.path.join(workspace,schemas.get("intersection_event"))
    intersection_route_event = os.path.join(workspace,schemas.get("intersection_route_event"))
    roadway_segment_event = os.path.join(workspace,schemas.get("roadway_segment_event"))
    intersection_approach_event = os.path.join(workspace,schemas.get("intersection_approach_event"))
    # -----------------------------------------------------------------------------------------------

    # Important parameters-------------------------
    today_date_string = time.strftime('%m/%d/%Y')
    current_active_network_string = "({0} is null or {0} <= CURRENT_TIMESTAMP) and ({1} is null or {1} > CURRENT_TIMESTAMP)".format(network_from_date_field, network_to_date_field)
    previous_active_network_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(network_from_date_field, network_to_date_field, last_update_date)
    network_created_since_date_string = "%s > %s" % (network_from_date_field, last_update_date)
    network_retired_since_date_string = "%s > %s" % (network_to_date_field, last_update_date)
    function_class_created_since_date_string = "%s > %s" % (function_class_from_date_field, last_update_date) if function_class_from_date_field else ""
    function_class_retired_since_date_string = "%s > %s" % (function_class_to_date_field, last_update_date) if function_class_to_date_field else ""
    aadt_created_since_date_string = "%s > %s" % (aadt_from_date_field, last_update_date) if aadt_from_date_field else ""
    aadt_retired_since_date_string = "%s > %s" % (aadt_to_date_field, last_update_date) if aadt_to_date_field else ""
    active_string = "%s is NULL" % to_date_field
    old_active_string = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(from_date_field, to_date_field, last_update_date)
    retired_route_ids = []
    created_route_ids = []
    created_retired_function_class_exist = False
    created_retired_aadt_exist = False
    #-----------------------------------------------

    # Data preprocessing-----------------------------------------------------------------
    query_date_string = "CURRENT_TIMESTAMP"
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(function_class_from_date_field, function_class_to_date_field, query_date_string) if function_class_from_date_field and function_class_to_date_field else ""
    arcpy.MakeFeatureLayer_management(function_class_event, active_current_function_class_layer, query_filter)
    query_filter = "({0} is null or {0} <= {2}) and ({1} is null or {1} > {2})".format(aadt_from_date_field, aadt_to_date_field, query_date_string) if aadt_from_date_field and aadt_to_date_field else ""
    arcpy.MakeFeatureLayer_management(aadt_event, active_current_aadt_layer, query_filter)
    # -------------------------------------------------------------------------------------

    # Create a previous active network layer. This is corresponding to the current state of all the intersection tables
    arcpy.MakeFeatureLayer_management(network, previous_active_network_layer, previous_active_network_string)
    # Create current network layer
    arcpy.MakeFeatureLayer_management(network, current_active_network_layer, current_active_network_string)

    # Create created network layer since the last_update_date and get a list created route ids
    arcpy.MakeFeatureLayer_management(network, created_network_layer, network_created_since_date_string)
    with arcpy.da.SearchCursor(created_network_layer, [network_route_id_field]) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            if route_id not in created_route_ids:
                created_route_ids.append(route_id)
    # Create retired network layer and the retired route ids.
    arcpy.MakeFeatureLayer_management(network, retired_network_layer, network_retired_since_date_string)
    with arcpy.da.SearchCursor(retired_network_layer, [network_route_id_field]) as sCursor:
        for sRow in sCursor:
            route_id = sRow[0]
            if route_id not in retired_route_ids:
                retired_route_ids.append(route_id)
    # Get the updated and retired route ids based on the updated functional class and aadt
    if function_class_from_date_field and function_class_to_date_field:
        if subset_data_exist(function_class_event, "%s or %s" % (function_class_created_since_date_string, function_class_retired_since_date_string)):
            created_retired_function_class_exist = True
    if aadt_from_date_field and aadt_from_date_field:
        if subset_data_exist(aadt_event, "%s or %s" % (aadt_created_since_date_string, aadt_retired_since_date_string)):
            created_retired_aadt_exist = True

    #Created network at all states ----------------------------------------------------------------------------------------------
    inserted_route_ids = list(set(created_route_ids) - set(retired_route_ids))
    updated_route_ids = list(set(created_route_ids) & set(retired_route_ids))
    deleted_route_ids = list(set(retired_route_ids) - set(created_route_ids))
    arcpy.MakeFeatureLayer_management(current_active_network_layer, inserted_network_layer, build_string_in_sql_expression(network_route_id_field, inserted_route_ids))
    arcpy.MakeFeatureLayer_management(current_active_network_layer, updated_after_network_layer, build_string_in_sql_expression(network_route_id_field, updated_route_ids))
    arcpy.MakeFeatureLayer_management(previous_active_network_layer, updated_before_network_layer, build_string_in_sql_expression(network_route_id_field, updated_route_ids))
    arcpy.MakeFeatureLayer_management(previous_active_network_layer, deleted_network_layer, build_string_in_sql_expression(network_route_id_field, deleted_route_ids))
    #------------------------------------------------------------------------------------------------------------------------------

    """
    Update Intersection_Approach_Event
    """

    # One special thing here is the attribute changes can also affect the result
    if created_retired_function_class_exist:
        arcpy.MakeFeatureLayer_management(function_class_event, created_retired_function_class_layer, "%s or %s" % (function_class_created_since_date_string, function_class_retired_since_date_string))
    if created_retired_aadt_exist:
        arcpy.MakeFeatureLayer_management(aadt_event, created_retired_aadt_layer, "%s or %s" % (aadt_created_since_date_string, aadt_retired_since_date_string))
    # to be analyzed intersections should include 1) along the inserted routes 2) along the updated after routes 3) intersected with the deleted routes but still active 4) intersected with attributes changed layers
    arcpy.MakeFeatureLayer_management(new_active_intersection_layer, ia_tba_current_intersection_layer)
    arcpy.SelectLayerByLocation_management(ia_tba_current_intersection_layer, "INTERSECT", inserted_network_layer, search_radius, "NEW_SELECTION")
    arcpy.SelectLayerByLocation_management(ia_tba_current_intersection_layer, "INTERSECT", updated_after_network_layer, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByLocation_management(ia_tba_current_intersection_layer, "INTERSECT", deleted_network_layer, search_radius, "ADD_TO_SELECTION")
    if created_retired_function_class_exist:
        arcpy.SelectLayerByLocation_management(ia_tba_current_intersection_layer, "INTERSECT", created_retired_function_class_layer, search_radius, "ADD_TO_SELECTION")
    if created_retired_aadt_exist:
        arcpy.SelectLayerByLocation_management(ia_tba_current_intersection_layer, "INTERSECT", created_retired_function_class_layer, search_radius, "ADD_TO_SELECTION")

    # to be analyzed network should includes routes intersecting with the above intersections
    arcpy.MakeFeatureLayer_management(current_active_network_layer, ia_tba_current_network_layer)
    arcpy.SelectLayerByLocation_management(ia_tba_current_network_layer, "INTERSECT", ia_tba_current_intersection_layer, search_radius, "NEW_SELECTION")

    # to be analyzed intersection route event, this is just used to get route measure value, so no need to make any sub selection
    arcpy.MakeTableView_management(new_active_intersection_route_event_layer, ia_tba_current_intersection_route_event_layer)

    # to be analyzed roadway segments should includes segments intersecting with the above intersections
    arcpy.MakeFeatureLayer_management(new_active_roadway_segment_event_layer, ia_tba_current_segment_event_layer)
    arcpy.SelectLayerByLocation_management(ia_tba_current_segment_event_layer, "INTERSECT", ia_tba_current_intersection_layer, search_radius)

    # Run analysis against the selected dataset
    intersection_approach_event_instance_new = intersection_approach_event_mod.IntersectionApproachEvent(
        network=ia_tba_current_network_layer,
        network_route_id_field=network_route_id_field,

        roadway_segment_event=ia_tba_current_segment_event_layer,
        roadway_segment_id_field=roadway_segment_id_field,
        roadway_segment_rid_field=roadway_segment_rid_field,
        roadway_segment_from_meas_field=roadway_segment_from_meas_field,
        roadway_segment_to_meas_field=roadway_segment_to_meas_field,

        intersection_event=ia_tba_current_intersection_layer,
        intersection_id_field=intersection_id_field,

        intersection_route_event=ia_tba_current_intersection_route_event_layer,
        intersection_route_on_rid_field=intersection_route_on_rid_field,
        intersection_route_on_measure_field=intersection_route_on_measure_field,

        intersection_approach_event= new_intersection_approach_event,
        intersection_approach_id_field=intersection_approach_id_field,
        intersection_approach_leg_id_field=intersection_approach_leg_id_field,
        intersection_approach_leg_type_field=intersection_approach_leg_type_field,
        intersection_approach_leg_dir_field=intersection_approach_leg_dir_field,
        intersection_approach_angle_field=intersection_approach_angle_field,
        intersection_approach_beg_inf_field=intersection_approach_beg_inf_field,
        intersection_approach_end_inf_field=intersection_approach_end_inf_field,

        function_class_layer=active_current_function_class_layer,
        function_class_field=function_class_field,
        function_class_rid_field=function_class_rid_field,
        function_class_from_meas_field=function_class_from_meas_field,
        function_class_to_meas_field=function_class_to_meas_field,
        aadt_layer=active_current_aadt_layer,
        aadt_field=aadt_field,
        aadt_rid_field=aadt_rid_field,
        aadt_from_meas_field=aadt_from_meas_field,
        aadt_to_meas_field=aadt_to_meas_field,

        area_of_influence=area_of_influence,
        angle_calculation_distance=angle_calculation_distance,
        azumith_zero_direction=azumith_zero_direction,
        measure_scale=measure_scale,
        search_radius=search_radius
    )
    new_intersection_approach_event = intersection_approach_event_instance_new.create_intersection_approach_event()
    inter_seg__info_dict = {}
    with arcpy.da.SearchCursor(new_intersection_approach_event, [intersection_approach_id_field, roadway_segment_rid_field, intersection_approach_angle_field, intersection_approach_leg_dir_field,
                                                                 intersection_approach_beg_inf_field, intersection_approach_end_inf_field, intersection_approach_leg_type_field, intersection_approach_leg_id_field]) as sCursor:
        for sRow in sCursor:
            intersection_approach_id, route_id, intersection_approach_angle, intersection_approach_direction, beg_inf, end_inf, leg_type, leg_id = sRow[0], sRow[1], sRow[2], sRow[3], sRow[4], sRow[5], sRow[6], sRow[7]
            inter_seg__info_dict[intersection_approach_id] = {
                "Route_ID": route_id,
                "Approach_Angle": intersection_approach_angle,
                "Approach_Direction": intersection_approach_direction,
                "Beg_Inf": beg_inf,
                "End_Inf": end_inf,
                "Leg_Type": leg_type,
                "Leg_Id": leg_id,
                "Processed": False
            }

    # Find the corresponding records in the old timestamp and process
    # to be analyzed intersections should include 1) along the deleted routes 2) along the updated before routes 3) old active but intersected with the inserted route  4) intersected with attributes changed layers
    arcpy.MakeFeatureLayer_management(old_active_intersection_layer, ia_tba_previous_intersection_layer)
    arcpy.SelectLayerByLocation_management(ia_tba_previous_intersection_layer, "INTERSECT", deleted_network_layer, search_radius, "NEW_SELECTION")
    arcpy.SelectLayerByLocation_management(ia_tba_previous_intersection_layer, "INTERSECT", updated_before_network_layer, search_radius, "ADD_TO_SELECTION")
    arcpy.SelectLayerByLocation_management(ia_tba_previous_intersection_layer, "INTERSECT", inserted_network_layer, search_radius, "ADD_TO_SELECTION")
    if created_retired_function_class_exist:
        arcpy.SelectLayerByLocation_management(ia_tba_previous_intersection_layer, "INTERSECT", created_retired_function_class_layer, search_radius, "ADD_TO_SELECTION")
    if created_retired_aadt_exist:
        arcpy.SelectLayerByLocation_management(ia_tba_previous_intersection_layer, "INTERSECT", created_retired_function_class_layer, search_radius, "ADD_TO_SELECTION")
    with arcpy.da.SearchCursor(ia_tba_previous_intersection_layer, intersection_id_field) as sCursor:
        ia_tba_previous_intersection_ids = [sRow[0] for sRow in sCursor]
    ia_tba_previous_inters_where_clause = build_string_in_sql_expression(intersection_id_field, ia_tba_previous_intersection_ids)

    arcpy.MakeTableView_management(intersection_approach_event, old_active_intersection_approach_layer, old_active_string)
    with arcpy.da.UpdateCursor(old_active_intersection_approach_layer, [to_date_field, intersection_approach_id_field, roadway_segment_rid_field,
                                                                        intersection_approach_angle_field, intersection_approach_leg_dir_field,
                                                                        intersection_approach_beg_inf_field, intersection_approach_end_inf_field,
                                                                        intersection_approach_leg_type_field, intersection_approach_leg_id_field],
                               ia_tba_previous_inters_where_clause) as uCursor:
        for uRow in uCursor:
            intersection_approach_id, route_id, intersection_approach_angle, intersection_approach_direction, beg_inf, end_inf, leg_type, leg_id = uRow[1], uRow[2], uRow[3], uRow[4], uRow[5], uRow[6], uRow[7], uRow[8]
            if intersection_approach_id in inter_seg__info_dict:
                info_dict = inter_seg__info_dict[intersection_approach_id]
                if info_dict["Route_ID"] == route_id and info_dict["Beg_Inf"] == beg_inf and info_dict["End_Inf"] == end_inf and info_dict["Approach_Angle"] == intersection_approach_angle and info_dict["Approach_Direction"] == intersection_approach_direction and info_dict["Leg_Type"] == leg_type and info_dict["Leg_Id"] == leg_id:
                    info_dict["Processed"] = True
                    continue
                else:
                    uRow[0] = today_date_string
                    uCursor.updateRow(uRow)
            else:
                uRow[0] = today_date_string
                uCursor.updateRow(uRow)

    # Insert unprocessed records
    with arcpy.da.InsertCursor(intersection_approach_event, [from_date_field, roadway_segment_rid_field,
                                                             intersection_id_field, roadway_segment_id_field, intersection_approach_id_field,
                                                             intersection_approach_angle_field, intersection_approach_leg_dir_field,
                                                             intersection_approach_beg_inf_field, intersection_approach_end_inf_field,
                                                             intersection_approach_leg_type_field, intersection_approach_leg_id_field]) as iCursor:
        for inter_approach_id, info_dict in inter_seg__info_dict.items():
            intersection_id = inter_approach_id.split("-")[0]
            segment_id = inter_approach_id.split("-")[1]
            if not info_dict["Processed"]:
                from_date = today_date_string
                route_id = info_dict["Route_ID"]
                approach_angle = info_dict["Approach_Angle"]
                approach_direction = info_dict["Approach_Direction"]
                beg_inf = info_dict["Beg_Inf"]
                end_inf = info_dict["End_Inf"]
                leg_type = info_dict["Leg_Type"]
                leg_id = info_dict["Leg_Id"]
                iCursor.insertRow((from_date, route_id,
                                   intersection_id, segment_id, inter_approach_id,
                                   approach_angle, approach_direction,
                                   beg_inf, end_inf,
                                   leg_type, leg_id))

    # Delete Duplicated Records
    delete_identical_only_keep_min_oid(intersection_approach_event, [roadway_segment_rid_field, intersection_id_field, roadway_segment_id_field,
                                                                     intersection_approach_angle_field, intersection_approach_leg_dir_field,
                                                                     intersection_approach_beg_inf_field, intersection_approach_end_inf_field,
                                                                     intersection_approach_leg_type_field, intersection_approach_leg_id_field])

    logger.info("Finished updating intersection approach event")


if __name__ == "__main__":
    from tss import truncate_datetime
    from util.meta import read_im_meta_data, write_im_meta_data
    # from roll_back_changes_since_date import roll_back
    # from datetime import datetime
    # workspace  = r'C:\Projects\ODOT\Data\Raw.gdb'
    # meta_date_dict = read_im_meta_data(workspace)
    # create_date = meta_date_dict["create_date"]
    # last_update_date =  meta_date_dict["last_update_date"]
    # today_date = truncate_datetime(datetime.now())
    # if  last_update_date == today_date:
    #     # If the last_update_date is today, we will have to roll back the changes to the intersection tables
    #     # we have made today. This is a workaround since the date in the network is the only indicator we can
    #     # use the differentiate the new and old features
    #     roll_back(workspace, last_update_date)
    #     last_update_date = last_update_date - timedelta(days=1)
    # elif last_update_date is None:
    #     last_update_date = create_date
    # update_intersection_tables(workspace, last_update_date)
    # write_im_meta_data(workspace, None, today_date)

    pass