__author__ = 'yluo'

import arcpy

def keep_fields_fms(input, fields):
    """
    Create a fieldmappings with the input fields
    :param input:
    :param fields:
    :return:
    """
    fms = arcpy.FieldMappings()
    for field in fields:
        fm = arcpy.FieldMap()
        fm.addInputField(input, field)
        fms.addFieldMap(fm)
    return fms

def keep_rename_fields_fms(inputs, field_dict_list):
    """
    Create a fieldmappings with the keep-rename rules specified. Need to be tested
    :param inputs:
    :param field_dict_list:
    :return:
    """
    fms = arcpy.FieldMappings()
    all_fields = []
    for input in inputs:
        fms.addTable(input)
        all_fields.extend(arcpy.ListFields(input))
    keep_fields = [field_dict['old'] for field_dict in field_dict_list]
    for field in all_fields:
        if field.required:
            continue
        if field.type in ["OID", "Geometry"]:
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


