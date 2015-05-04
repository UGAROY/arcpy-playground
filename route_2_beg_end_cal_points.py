__author__ = 'yluo'

import arcpy
import os

arcpy.env.overwriteOutput = True


def is_gapped_polyline(shape):
    for i in range(shape.partCount - 1):
        curr_part_set = set([(point.X, point.Y) for point in shape.getPart(i)])
        next_part_set = set([(point.X, point.Y) for point in shape.getPart(i+1)])
        # It is done this way to take overlap into account
        if curr_part_set & next_part_set:
            return False
        else:
            return True


def route_to_be_calibration_points(route, calibration_poin):

    route_id_field = "RCLINK"
    measure_field = "MEASURE"

    arcpy.CreateFeatureclass_management(os.path.dirname(calibration_point), os.path.basename(calibration_point), 'POINT', '#', 'DISABLED', 'DISABLED', route)
    arcpy.AddField_management(calibration_point, route_id_field, 'TEXT')
    arcpy.AddField_management(calibration_point, measure_field, 'DOUBLE')


    with arcpy.da.InsertCursor(calibration_point, ["SHAPE@", route_id_field, measure_field]) as iCursor:
        with arcpy.da.SearchCursor(route, ["SHAPE@", route_id_field]) as sCursor:
            for sRow in sCursor:
                shape, route_id = sRow[0], sRow[1]
                if shape.isMultipart:
                    if is_gapped_polyline(shape):
                        for i in range(shape.partCount):
                            geometry_part = shape.getPart(i)
                            firstPoint = geometry_part.next()
                            for lastPoint in geometry_part:
                                pass
                            iCursor.insertRow((firstPoint, route_id, firstPoint.M))
                            iCursor.insertRow((lastPoint, route_id, lastPoint.M))
                    else:
                        firstPoint, lastPoint = None, None
                        for i in range(shape.partCount):
                            geometry_part = shape.getPart(i)
                            for point in geometry_part:
                                if firstPoint is None or lastPoint is None:
                                    firstPoint = point
                                    lastPoint = point
                                else:
                                    if point.M > firstPoint.M:
                                        lastPoint = point
                                    else:
                                        firstPoint = point
                        iCursor.insertRow((firstPoint, route_id, firstPoint.M))
                        iCursor.insertRow((lastPoint, route_id, lastPoint.M))
                else:
                    iCursor.insertRow((shape.firstPoint, route_id, shape.firstPoint.M))
                    iCursor.insertRow((shape.lastPoint, route_id, shape.lastPoint.M))


if __name__ == "__main__":
    route = arcpy.GetParameterAsText(0) or r'C:\Projects\GDOT\Data\GDOT_ROUTES_CREATE_CPs.gdb\MILEPOINT_ROUTE__SIX_COUNTY'
    calibration_point = arcpy.GetParameterAsText(1) or r'C:\Projects\GDOT\Data\GDOT_ROUTES_CREATE_CPs.gdb\calibration_point'
    route_to_be_calibration_points(route, calibration_point)
