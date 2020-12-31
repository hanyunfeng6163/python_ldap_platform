def to_bool(str):
    """
    Converts a given string to a boolean value. Leading and trailing
    whitespace is ignored, so strings of whitespace are evaluated as
    ``False``.
    """
    if str:
        return bool(str.strip())
    return False