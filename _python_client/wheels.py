

def crop_float(val: float, decimals: int = 3) -> float:
    return float("{:.{nd}f}".format(val, nd = decimals))
