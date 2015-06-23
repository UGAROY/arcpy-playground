__author__ = 'yluo'

def truncate_datetime(datetime):
    """
    Truncate the input datetime object to only keep the date information
    :param datetime: input datetime object
    :return: datetime object with only date info
    """
    return None if datetime is None else datetime.replace(hour=0, minute=0, second=0, microsecond=0)

def format_sql_date(input_datetime, dbtype):
    """
    Format the datetime string to be used for different database type
    :param input_datetime:
    :param dbtype:
    :return: :raise Exception:
    """
    date_string = input_datetime.strftime("%Y-%m-%d %H:%M:%S")
    if dbtype == "FileGdb":
        date_string = "date '%s'" % date_string
    elif dbtype == "Oracle":
        date_string = "TO_DATE('%s','YYYY-MM-DD HH24:MI:SS')" % date_string
    elif dbtype == "SQL Server":
        date_string = "'%s'" % date_string
    else:
        # Update this if new database needs to be supported
        raise Exception("Unhandled DbType")
    return date_string

def get_datetime_stamp():
    """
    Get current timestamp
    :return:
    """
    import time
    return time.strftime("%m%d%H%M%S")