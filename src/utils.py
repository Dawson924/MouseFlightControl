def check_overflow(a, min_val, max_val):
    if a < min_val:
        return min_val
    elif a > max_val:
        return max_val
    return a


def wheel_step(step, wheel_delta):
    if wheel_delta == 0:
        return 0
    if wheel_delta > 0:
        sign = 1
    else:
        sign = -1
    return sign * step


def pos(val):
    val = float(val)
    threshold = 1
    val = 1 if abs(val) < threshold else val
    return int(round(val))
