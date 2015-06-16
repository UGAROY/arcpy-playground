import arcpy

def transform_dataset_keep_fields(dataset, keep_fields):
    for field in arcpy.ListFields(dataset):
        if field.required:
            continue
        if field.type in ["OID", "Geometry"]:
            continue
        if field.name.lower() not in [kfld.lower() for kfld in keep_fields]:
            arcpy.DeleteField_management(dataset, field.name)

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