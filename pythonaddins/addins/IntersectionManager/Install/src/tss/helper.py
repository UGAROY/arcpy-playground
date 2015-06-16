def first_or_default(input_list, match_func, default_value=None):
    """
    Only return the first element that meet the requirement. If nothing found, then just return the default_value
    Equivalent to
    val = default_val
    for x in some_list:
        if match(x):
            val = x
            break
    @param input_list:
    @param match_func:
    @param default_value:
    @return:
    """
    return next((x for x in input_list if match_func(x)), default_value)