import arcpy

def keep_fields_fms(input, fields):
    fms = arcpy.FieldMappings()
    for field in fields:
        fm = arcpy.FieldMap()
        fm.addInputField(input, field)
        fms.addFieldMap(fm)
    return fms

def keep_rename_fields_fms(inputs, field_dict_list):
    fms = arcpy.FieldMappings()
    all_fields = []
    for input in inputs:
        fms.addTable(input)
        all_fields.extend(arcpy.ListFields(input))
    keep_fields = [field_dict['old'] for field_dict in field_dict_list]
    for field in all_fields:
        if field.required:
            continue
        field_name = field.name
        if field_name not in keep_fields:
            fm_index = fms.findFieldMapIndex(field_name)
            fms.removeFieldMap(fm_index)
    for field_dict in field_dict_list:
        field, new_field = field_dict['old'], field_dict['new']
        fm_index = fms.findFieldMapIndex(field)
        fm = fms.getFieldMap(fm_index)
        field = fm.outputField
        field.name = new_field
        field.aliasName = new_field
        fm.outputField = field
        fms.replaceFieldMap(fm_index, fm)
    return fms


