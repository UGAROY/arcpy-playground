__author__ = 'yluo'

import arcpy

arcpy.env.overwriteOutput = True

def is_gapped_polyline(shape):
    """
    As long as two parts has common points, then they are considered to be continuous,
    @param shape: input geometry
    @return:
    """
    if not shape.isMultipart:
        return False
    for i in range(shape.partCount - 1):
        curr_part_set = set([(point.X, point.Y) for point in shape.getPart(i)])
        next_part_set = set([(point.X, point.Y) for point in shape.getPart(i+1)])
        # It is done this way to take overlap into account
        if not curr_part_set & next_part_set:
            return True
    return False

def is_gapped_polyline_strict(shape):
    """
    The endpoint of one part has to be the same as the begin point of next part
    @param shape: input geometry
    @return:
    """
    if not shape.isMultipart:
        return False
    for i in range(shape.partCount - 1):
        curr_part = shape.getPart(i)
        next_part = shape.getPart(i + 1)
        if not curr_part[-1].equals(next_part[0]):
            return True
    return False

if __name__ == "__main__":
    pass
