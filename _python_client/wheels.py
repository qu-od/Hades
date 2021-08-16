from typing import List, Dict, Tuple, Optional, Any

def crop_float(
        val: float, decimals: int = 3,
        len_in_symbols: Optional[int] = None
        ) -> float:
    if not len_in_symbols:
        return float("{:.{nd}f}".format(val, nd = decimals))
    if len_in_symbols:
        raise NotImplementedError()

def grow_string(
        raw_string: str,
        new_string_length: int,
        additional_symbol: str = "_"
        ):
    if len(raw_string) >= new_string_length:
        raise ValueError(
            f"String is already contains at least {new_string_length} symbols") 
    number_of_symbols_to_add: int = new_string_length - len(raw_string) 
    return additional_symbol * number_of_symbols_to_add + raw_string
