import arcpy
from src.util.helper import get_default_parameters
from src.tss import truncate_datetime, setup_logger

from src.int1_populate_base_info_for_intersections import populate_intersections_info
from src.int2_generate_intersection_approach_records import populate_intersection_leg_info
from src.util.meta import write_im_meta_data

setup_logger("IntersectionManager")

SECTION = "Default"
input_datetime = arcpy.GetParameter(0)

# Input
parameters = get_default_parameters()
workspace = parameters.get(SECTION, "workspace")
create_date = truncate_datetime(input_datetime)

populate_intersections_info(workspace, create_date)
populate_intersection_leg_info(workspace, create_date)
# custom_create_odot(workspace)
write_im_meta_data(workspace, create_date)

