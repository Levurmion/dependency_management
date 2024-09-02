def all_args_are_int_or_float(*args) -> bool:
    return all([isinstance(arg, int) or isinstance(arg, float) for arg in args])


def c_from_ab(a: int, b: int):
    if not all_args_are_int_or_float(a, b):
        return None
    return a + b


def c_from_de(d: int, e: int):
    if not all_args_are_int_or_float(d, e):
        return None
    return e / d


def a_from_cb(c: int, b: int):
    if not all_args_are_int_or_float(c, b):
        return None
    return c - b


def b_from_ca(c: int, a: int):
    if not all_args_are_int_or_float(c, a):
        return None
    return c - a


def e_from_cd(c: int, d: int):
    if not all_args_are_int_or_float(c, d):
        return None
    return c * d


def e_from_fg(f: int, g: int):
    if not all_args_are_int_or_float(f, g):
        return None
    return g - f


def d_from_ce(c: int, e: int):
    if not all_args_are_int_or_float(c, e):
        return None
    return e / c


def g_from_ef(e: int, f: int):
    if not all_args_are_int_or_float(e, f):
        return None
    return e + f


def f_from_ge(g: int, e: int):
    if not all_args_are_int_or_float(g, e):
        return None
    return g - e
