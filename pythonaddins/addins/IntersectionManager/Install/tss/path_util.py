import os


def get_parent_directory(path, level=1):
    """
    Return the path of upper directory
    @param path: input path
    @param level: the upper level
    @return: @raise ValueError:
    """
    if level <= 0:
        raise ValueError("Level cannot be < 1")
    parent_path = path
    while level > 0:
        parent_path = os.path.dirname(parent_path)
        level -= 1
    return parent_path
