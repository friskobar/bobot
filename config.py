from enum import Enum, auto


class Channels:
    log = [1558318108396224592] # append to this list, every channel in the list will get a log

class Action(Enum):
    KICK = auto()
    TIMEOUT = auto()
    UNTIMEOUT = auto()
