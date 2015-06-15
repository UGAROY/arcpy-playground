def extract_number_from_string(input_string):
    """
    @param input_string:
    @return: A list of numeric value
    """
    import re
    return [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", input_string)]