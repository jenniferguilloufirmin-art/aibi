from dataclasses import dataclass
from typing import Protocol

from .agent import SafeDeviceAgent


class RobotDriver(Protocol):
    def move(self, direction: str, distance_m: float) -> None: ...


@dataclass
class SafeRobotController:
    """Pont robot : il ne peut agir qu'après permissions et confirmation."""

    agent: SafeDeviceAgent
    driver: RobotDriver

    def move(self, direction: str, distance_m: float, *, confirmed: bool = False) -> None:
        if direction not in {"forward", "backward", "left", "right"}:
            raise ValueError("Direction non reconnue.")
        if not 0 < distance_m <= 2:
            raise ValueError("La distance doit être comprise entre 0 et 2 mètres.")
        self.agent.policy.authorize("move_robot", confirmed=confirmed)
        self.agent.run(
            "move_robot",
            confirmed=confirmed,
            direction=direction,
            distance_m=distance_m,
        )
        self.driver.move(direction, distance_m)
