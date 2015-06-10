__author__ = 'yluo'

from datetime import datetime
import os

import arcpy

from config.schema import default_schemas
from tss import format_sql_date
from util.helper import get_default_parameters

default_parameters = get_default_parameters()

def roll_back(workspace, input_date):

    client = "Default"
    parameters = default_parameters.get(client)
    schemas = default_schemas.get(client)

    dbtype = parameters.get(client, "dbtype")

    since_date = format_sql_date(input_date, dbtype)

    # Source Data ----------------------------------------------------------------
    intersection_event = os.path.join(workspace, schemas.get("intersection_event"))
    intersection_route_event = os.path.join(workspace, schemas.get("intersection_route_event"))
    roadway_segment_event = os.path.join(workspace, schemas.get("roadway_segment_event"))
    intersection_approach_event = os.path.join(workspace, schemas.get("intersection_approach_event"))

    from_date_field = schemas.get("from_date_field")
    to_date_field = schemas.get("to_date_field")
    # ----------------------------------------------------------------------------

    # Date Query String ----------------------------------------------------------
    since_date_string = "{0} >= {2} or {1} >= {2}".format(from_date_field, to_date_field, since_date)
    # ----------------------------------------------------------------------------

    events_to_be_rolled_back = [intersection_event, intersection_route_event, roadway_segment_event, intersection_approach_event]

    for event in events_to_be_rolled_back:
        with arcpy.da.UpdateCursor(event, [from_date_field, to_date_field], since_date_string) as uCursor:
            for uRow in uCursor:
                from_date, to_date = uRow[0], uRow[1]
                if to_date:
                    uRow[1] = None
                    uCursor.updateRow(uRow)
                else:
                    uCursor.deleteRow()

if __name__ == "__main__":
    workspace = r'C:\Projects\ODOT\Data\Raw.gdb'
    input_date = datetime.now()
    roll_back(workspace, input_date)