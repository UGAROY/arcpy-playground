import arcpy
from tss_util import truncate_datetime, get_default_parameters
from datetime import timedelta, datetime

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Intersection Manager Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [CreateIntersections, UpdateIntersections, SetViewDate]


class CreateIntersections(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1 - Populate Intersections Info"
        self.description = "Populate all the intersection related tables"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        workspace_input = arcpy.Parameter(
            displayName="Workspace",
            name="workspace",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        create_date_input = arcpy.Parameter(
            displayName="Create Date",
            name="create_date",
            datatype="Date",
            parameterType="Optional",
            direction="Input")

        params = [workspace_input, create_date_input]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        from int1_populate_base_info_for_intersections import populate_intersections_info
        from int2_generate_intersection_approach_records import populate_intersection_leg_info
        from ohio_dot_create import custom_create_odot
        from intersection_util import write_im_meta_data
        workspace, create_date = parameters[0].valueAsText, truncate_datetime(parameters[1].value)
        populate_intersections_info(workspace, create_date)
        populate_intersection_leg_info(workspace, create_date)
        custom_create_odot(workspace)
        write_im_meta_data(workspace, create_date)
        return


class UpdateIntersections(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2 - Update Intersections Info"
        self.description = "Update all the intersection related tables"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        workspace_input = arcpy.Parameter(
            displayName="Workspace",
            name="workspace",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        params = [workspace_input]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        from int3_update_intersection import update_intersection_tables
        from intersection_util import read_im_meta_data, write_im_meta_data
        from ohio_dot_update import custom_update_odot
        from roll_back_changes_since_date import roll_back
        workspace= parameters[0].valueAsText
        meta_date_dict = read_im_meta_data(workspace)
        create_date = meta_date_dict["create_date"]
        last_update_date =  meta_date_dict["last_update_date"]
        today_date = truncate_datetime(datetime.now())
        if  last_update_date == today_date:
            # If the last_update_date is today, we will have to roll back the changes to the intersection tables
            # we have made today and also set the last_update_date to one day before to mimic the intersection related
            # events are all created yesterday. This is a workaround since the date in the network is the only
            # indicator we can use the differentiate the new and old features
            roll_back(workspace, last_update_date)
            last_update_date = last_update_date - timedelta(days=1)
        elif last_update_date is None:
            last_update_date = create_date
        update_intersection_tables(workspace, last_update_date)
        custom_update_odot(workspace, today_date)
        write_im_meta_data(workspace, None, today_date)
        return


class SetViewDate(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Set View Date"
        self.description = "Set the view date in the definition query of the events in current map document"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        date_input = arcpy.Parameter(
            displayName="View Date",
            name="date",
            datatype="Date",
            parameterType="Optional",
            direction="Input")

        date_input.value = truncate_datetime(datetime.now())

        params = [date_input]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        from schema import default_schemas
        from tss_util import format_sql_date
        default_parameters = get_default_parameters()

        schemas = default_schemas.get("default")
        dbtype = default_parameters.get("default").get("dbtype")

        from_date_field = schemas.get("from_date_field")
        to_date_field = schemas.get("to_date_field")
        intersection_event = schemas.get("intersection_event")
        intersection_route_event = schemas.get("intersection_route_event")
        roadway_segment_event = schemas.get("roadway_segment_event")
        intersection_approach_event = schemas.get("intersection_approach_event")
        view_date = parameters[0].value or truncate_datetime(datetime.now())
        view_date_query_string = format_sql_date(view_date, dbtype)
        mxd = arcpy.mapping.MapDocument("CURRENT")
        tba_items = arcpy.mapping.ListLayers(mxd) + arcpy.mapping.ListTableViews(mxd)
        for item in tba_items:
            if item.name in [intersection_event, intersection_route_event, roadway_segment_event, intersection_approach_event]:
                item.definitionQuery = "({0} is NULL or {0} <= {2}) AND ({1} is NULL or {1} > {2})".format(from_date_field, to_date_field, view_date_query_string)
        arcpy.RefreshActiveView()
        del mxd
        return