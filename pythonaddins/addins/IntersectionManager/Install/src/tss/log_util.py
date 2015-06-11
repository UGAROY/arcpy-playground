import logging
from datetime_util import get_datetime_stamp

def setup_logger():
    time_stamp = get_datetime_stamp()
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                        datefmt="%m-%d %H:%M",
                        filename="myapp%s.log" % time_stamp,
                        filemode="w")