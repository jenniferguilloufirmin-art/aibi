from dataclasses import dataclass, field

from .audit import AuditLog
from .models import Action, ActionRisk, Permission


@dataclass
class PolicyEngine:
    """Autorise uniquement des capacités connues et explicitement activées."""

    audit: AuditLog = field(default_factory=AuditLog)
    permissions: set[Permission] = field(default_factory=set)
    emergency_stop: bool = False

    _actions = {
        "device_info": Action(
            "device_info", Permission.DEVICE_INFO, ActionRisk.LOW,
            "Lire les informations non sensibles de la plateforme."
        ),
        "list_home": Action(
            "list_home", Permission.READ_FILES, ActionRisk.MEDIUM,
            "Lister le dossier personnel, sans lire le contenu des fichiers."
        ),
        "fetch_url": Action(
            "fetch_url", Permission.NETWORK, ActionRisk.MEDIUM,
            "Accéder à une URL explicitement fournie."
        ),
        "move_robot": Action(
            "move_robot", Permission.ROBOT_CONTROL, ActionRisk.HIGH,
            "Envoyer un déplacement à un robot.", requires_confirmation=True
        ),
        "shell": Action(
            "shell", Permission.DEVICE_INFO, ActionRisk.BLOCKED,
            "Exécuter une commande système arbitraire."
        ),
    }

    def action(self, name: str) -> Action:
        return self._actions.get(
            name,
            Action(name, Permission.DEVICE_INFO, ActionRisk.BLOCKED, "Action inconnue."),
        )

    def grant(self, permission: Permission) -> None:
        self.permissions.add(permission)
        self.audit.record("permission_granted", permission=permission.value)

    def revoke(self, permission: Permission) -> None:
        self.permissions.discard(permission)
        self.audit.record("permission_revoked", permission=permission.value)

    def stop(self) -> None:
        self.emergency_stop = True
        self.audit.record("emergency_stop", enabled=True)

    def resume(self) -> None:
        self.emergency_stop = False
        self.audit.record("emergency_stop", enabled=False)

    def authorize(self, name: str, confirmed: bool = False) -> tuple[bool, str]:
        action = self.action(name)
        if self.emergency_stop:
            reason = "Arrêt d'urgence actif."
        elif action.risk is ActionRisk.BLOCKED:
            reason = "Cette action est bloquée par conception."
        elif action.permission not in self.permissions:
            reason = f"Permission requise : {action.permission.value}."
        elif action.requires_confirmation and not confirmed:
            reason = "Confirmation humaine requise pour cette action."
        else:
            self.audit.record("action_authorized", action=name, risk=action.risk.value)
            return True, "Action autorisée."
        self.audit.record("action_denied", action=name, reason=reason)
        return False, reason
