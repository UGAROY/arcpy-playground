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

if __name__ == "__main__":
    pass
