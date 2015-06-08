import arcpy
import os
import json
from time import strftime

curr_dir = os.path.dirname(os.path.realpath(__file__))

def truncate_datetime(datetime):
    return None if datetime is None else datetime.replace(hour=0, minute=0, second=0, microsecond=0)


def subset_data_exist(data, where_clause):
    with arcpy.da.SearchCursor(data, "OID@", where_clause) as sCursor:
        try:
            sCursor.next()
            return True
        except StopIteration:
            return False

def subset_data_count(data, where_clause):
    count = 0
    with arcpy.da.SearchCursor(data, "OID@",  where_clause) as sCursor:
        for sRow in sCursor:
            count += 1
    return count


def delete_subset_data(data, where_clause):
    # if subset_data_exist(data, where_clause):
    #     # Only process data when subset data actual exists
    #     dataSetType = arcpy.Describe(data).datasetType
    #     if dataSetType == "Table" or dataSetType == "TableView":
    #         arcpy.MakeTableView_management(data, "temp_view")
    #         arcpy.SelectLayerByAttribute_management("temp_view", "NEW_SELECTION", where_clause)
    #         arcpy.SelectLayerByAttribute_management("temp_view", "SWITCH_SELECTION")
    #         temp_table = "in_memory\\temp_table"
    #         arcpy.TableSelect_analysis("temp_view", temp_table)
    #         arcpy.Delete_management(data)
    #         arcpy.CopyRows_management(temp_table, data)
    #     elif dataSetType == "FeatureClass" or dataSetType == "FeatureLayer":
    #         arcpy.MakeFeatureLayer_management(data, "temp_view")
    #         arcpy.SelectLayerByAttribute_management("temp_view", "NEW_SELECTION", where_clause)
    #         arcpy.DeleteRows_management("temp_view")
    #     else:
    #         raise Exception("Incorrect input data")
    with arcpy.da.UpdateCursor(data, "OID@", where_clause) as uCursor:
        for uRow in uCursor:
            uCursor.deleteRow()

def transform_dataset_keep_fields(dataset, keep_fields):
    for field in arcpy.ListFields(dataset):
        if field.required:
            continue
        if field.type in ["OID", "Geometry"]:
            continue
        if field.name.lower() not in [kfld.lower() for kfld in keep_fields]:
            arcpy.DeleteField_management(dataset, field.name)


def get_maximum_id(dataset, id_field):
    # the id field need to be an integer field, or at least be filled with integer value
    max_id = 0
    with arcpy.da.SearchCursor(dataset, id_field) as sCursor:
        for sRow in sCursor:
            try:
                # Convert possible string to id
                id = int(sRow[0])
            except TypeError:
                continue
            max_id = max(id, max_id)
    return max_id


def get_minimum_value(dataset, field, where_clause):
    sCursor = arcpy.SearchCursor(dataset, where_clause, "", "", "%s A" % field)
    sRow = sCursor.next()
    del sCursor
    return sRow.getValue(field)


def populate_auto_increment_id(input_data, id_field, existing_max_id=0):
    with arcpy.da.UpdateCursor(input_data, id_field, "%s is NULL" % id_field) as uCursor:
        for uRow in uCursor:
            existing_max_id += 1
            uRow[0] = existing_max_id
            uCursor.updateRow(uRow)


def approximate_equal(value1, value2, tolerance=0.0001):
    return abs(value1 - value2) < tolerance


def build_numeric_in_sql_expression(field_name, value_list):
    return "%s in (%s)" % (field_name, ",".join(str(value) for value in value_list)) if len(value_list) > 0 else "1=2"


def build_string_in_sql_expression(field_name, value_list):
    return "%s in (%s)" % (field_name, ",".join("'" + value + "'" for value in value_list)) if len(value_list) > 0 else "1=2"


def delete_identical_only_keep_min_oid(data, fields, xy_tolerance="1 meters"):
    identical_table = "in_memory\\identical_table"
    arcpy.FindIdentical_management(data, identical_table, fields, xy_tolerance, "", "ONLY_DUPLICATES")
    fseq_list = []
    delete_oid_list = []
    sCursor = arcpy.SearchCursor(identical_table, "", "", "FEAT_SEQ;IN_FID", "IN_FID A")
    for sRow in sCursor:
        feat_seq, in_fid = sRow.getValue("FEAT_SEQ"), sRow.getValue("IN_FID")
        if feat_seq not in fseq_list:
            fseq_list.append(feat_seq)
        else:
            delete_oid_list.append(in_fid)
    del sCursor
    oid_field = arcpy.Describe(data).OIDFieldName
    if len(delete_oid_list) != 0:
        where_clause = build_numeric_in_sql_expression(oid_field, delete_oid_list)
        delete_subset_data(data, where_clause)

def alter_field_name(data, old_field_name, new_field_name):
    if old_field_name == new_field_name:
        return
    try:
        arcpy.AlterField_management(data, old_field_name, new_field_name, new_field_name)
    except Exception as e:
        arcpy.AddMessage(e)
        old_field = [field for field in arcpy.ListFields(data) if field.name == old_field_name][0]
        arcpy.AddField_management(data, new_field_name, old_field.type, old_field.precision,
                                  old_field.scale, old_field.length, old_field.aliasName, old_field.isNullable, old_field.required)
        arcpy.CalculateField_management(data, new_field_name, "!%s!" % old_field_name, "PYTHON")
        arcpy.DeleteField_management(data, old_field_name)

def format_sql_date(input_datetime, dbtype):
    date_string = input_datetime.strftime("%Y-%m-%d %H:%M:%S")
    if dbtype == "FileGdb":
        date_string = "date '%s'" % date_string
    elif dbtype == "Oracle":
        date_string = "TO_DATE('%s','YYYY-MM-DD HH24:MI:SS')" % date_string
    elif dbtype == "SQL Server":
        date_string = "'%s'" % date_string
    else:
        raise Exception("Unhandled DbType")

    return date_string

# def get_default_parameters():
#     try:
#         # import params
#         # reload(params)
#         # return params.default_parameters
#         with open(os.path.join(curr_dir, "params.py"), "r") as f:
#             data = f.read().replace("default_parameters=", "")
#         return json.loads(data)
#     except ImportError:
#         import params_init
#         return params_init.default_parameters

def get_default_parameters():
    try:
        import ConfigParser

        Config = ConfigParser.ConfigParser()
        init_cfg = os.path.join(curr_dir, "params.ini")
        updated_cfg = os.path.join(curr_dir, "params_updated.ini")

        if os.path.exists(updated_cfg):
            Config.read(updated_cfg)
        else:
            Config.read(init_cfg)

        return Config
    except ImportError:
        pass

import logging

def log_message(message):
    logger = setupLogger()
    # logger.warning(curr_dir)
    logger.info(message)
    # arcpy.AddMessage("%s : %s" % (message, strftime("%Y-%m-%d %H:%M:%S")))

def logger(name=__name__):
    """logger(name)

       The logger function returns a new logger by name.

         name(String):
       The name of the calling class/filename - if left empty it will use the tss name"""
    return logging.getLogger(name)

def setupLogger():
    """setupLogger()

       The setupLogger function sets the configuration for the logger."""
    # set up logging to file - see previous section for more details
    import os


    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=os.path.join('C:\Projects\IntersectionManager', 'tss.log'),
                        filemode='a')
    return logger()

def zoom_to_selected_features(layer_name, where_clause):
    """
    Look for a layer in TOC by name. Make a selection based on passing in where clause and zoom to selection features.
    """

    mxd = arcpy.mapping.MapDocument(r"CURRENT")
    df = mxd.activeDataFrame
    layers = arcpy.mapping.ListLayers(mxd,"",df)

    layer = None
    for lyr in layers:
        if lyr.name == layer_name:
            layer = lyr
            break

    if layer:
        arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", where_clause)
    else:
        raise Exception("Layer '%s' does not exist." %layer_name)

    df.extent = layer.getSelectedExtent()

    arcpy.RefreshActiveView()
    arcpy.RefreshTOC()

    return