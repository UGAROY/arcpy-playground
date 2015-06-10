import arcpy

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