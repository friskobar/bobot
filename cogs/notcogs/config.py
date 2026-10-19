from enum import Enum, auto

servers = [1558314633046134838, 1514450228361695292]
frisk = 507971620950900746
poly = 1191924513466757191
bob = 821021638983680020
log_notif = [poly, frisk, bob]

ticket_perms = 1556828076975849584

class Channels:
    log = [1558318108396224592] # append to this list, every channel in the list will get a log


class Action(Enum):
    KICK = auto()
    TIMEOUT = auto()
    UNTIMEOUT = auto()
    CLEAN = auto()
    WARN = auto()
    UNWARN = auto()
    OPEN_TICKET = auto()
    CLOSE_TICKET = auto()
