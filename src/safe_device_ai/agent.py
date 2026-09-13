import platform
from pathlib import Path
from typing import Any

from .policy import PolicyEngine


class SafeDeviceAgent:
    """Façade d'exécution : aucune commande arbitraire n'est acceptée."""

    def __init__(self, policy: PolicyEngine | None = None) -> None:
        self.policy = policy or PolicyEngine()

    def run(self, action: str, *, confirmed: bool = False, **arguments: Any) -> Any:
        allowed, reason = self.policy.authorize(action, confirmed=confirmed)
        if not allowed:
            raise PermissionError(reason)

        if action == "device_info":
            return {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python": platform.python_version(),
            }
        if action == "list_home":
            return sorted(item.name for item in Path.home().iterdir())
        if action == "fetch_url":
            raise NotImplementedError(
                "Le connecteur réseau doit être injecté par l'application cliente."
            )
        if action == "move_robot":
            # Le driver est volontairement externe : l'agent valide la demande,
            # puis le contrôleur robot la transmet à son matériel.
            return {
                "direction": arguments["direction"],
                "distance_m": arguments["distance_m"],
            }
        raise RuntimeError(f"Action autorisée mais non implémentée : {action}")
