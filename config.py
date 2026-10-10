from enum import Enum, auto

servers = [1558314633046134838, 1514450228361695292]
log_notif = [1191924513466757191, 821021638983680020]

class Channels:
    log = [1558318108396224592] # append to this list, every channel in the list will get a log


class Action(Enum):
    KICK = auto()
    TIMEOUT = auto()
    UNTIMEOUT = auto()
    CLEAN = auto()
