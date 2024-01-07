from enum import Enum

colors = {
    "PINK": (289, 38, 98, 77),
    # "TEAL": (169, 62, 97, 22),
    "BLUE": (217, 83, 59, 22),
    "BROWN": (4, 28, 38, 52),
    "BLACK": (0, 0, 0, 0),
    "RED": (356, 86, 58, 46),
    "KHAKI": (90, 15, 53, 90),
    "GREEN": (104, 79, 82, 94),
    "ORANGE": (23, 68, 63, 5),
}


class Action(Enum):
    DONOTHING = 1
    DESTROY = 2
    CREATE = 3


def avg(lst):
    return sum(lst) / len(lst)

