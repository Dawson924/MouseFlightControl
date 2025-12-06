def is_integer(string):
    try:
        cleaned_str = string.strip()
        int(cleaned_str)
        return True
    except (ValueError, TypeError):
        return False


def is_float(string):
    cleaned_str = string.strip()
    if not cleaned_str:
        return False
    if is_integer(cleaned_str):
        return False
    try:
        float(cleaned_str)
        return True
    except (ValueError, TypeError):
        return False
