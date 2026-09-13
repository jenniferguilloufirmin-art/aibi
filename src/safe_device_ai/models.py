from dataclasses import dataclass
from enum import Enum


class Permission(str, Enum):
    DEVICE_INFO = "device_info"
    READ_FILES = "read_files"
    NETWORK = "network"
    ROBOT_CONTROL = "robot_control"


class ActionRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Action:
    name: str
    permission: Permission
    risk: ActionRisk
    description: str
    requires_confirmation: bool = False
