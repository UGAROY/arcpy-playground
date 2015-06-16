import arcpy
from datetime import datetime
from src.tss import format_sql_date,truncate_datetime
from src.config.schema import default_schemas
from src.util.helper import get_default_parameters

import logging
logger = logging.getLogger(__name__)

client = "Default"
parameters = get_default_parameters()
schemas = default_schemas.get(client)

dbtype = parameters.get(client, "dbtype")

# Inputs
from_date_field = schemas.get("from_date_field")
to_date_field = schemas.get("to_date_field")
intersection_event = schemas.get("intersection_event")
intersection_route_event = schemas.get("intersection_route_event")
roadway_segment_event = schemas.get("roadway_segment_event")
intersection_approach_event = schemas.get("intersection_approach_event")

view_date = arcpy.GetParameter(0) or truncate_datetime(datetime.now())
view_date_query_string = format_sql_date(view_date, dbtype)

mxd = arcpy.mapping.MapDocument("CURRENT")
tba_items = arcpy.mapping.ListLayers(mxd) + arcpy.mapping.ListTableViews(mxd)

logger.info("Start setting view date")

for item in tba_items:
    if item.name in [intersection_event, intersection_route_event, roadway_segment_event, intersection_approach_event]:
        item.definitionQuery = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(from_date_field, to_date_field, view_date_query_string)
arcpy.RefreshActiveView()

del mxd


