import pytest

from safe_device_ai import Permission, PolicyEngine, SafeDeviceAgent
from safe_device_ai.robot import SafeRobotController
from safe_device_ai.app import AibiApp
from safe_device_ai.memory import LocalMemory


def test_unknown_and_shell_actions_are_blocked(tmp_path):
    policy = PolicyEngine()
    agent = SafeDeviceAgent(policy)
    with pytest.raises(PermissionError, match="bloquée"):
        agent.run("shell")
    with pytest.raises(PermissionError, match="bloquée"):
        agent.run("delete_everything")


def test_permissions_are_required_and_revocable(tmp_path):
    policy = PolicyEngine()
    policy.audit.path = tmp_path / "audit.jsonl"
    agent = SafeDeviceAgent(policy)
    with pytest.raises(PermissionError, match="Permission requise"):
        agent.run("device_info")
    policy.grant(Permission.DEVICE_INFO)
    assert "system" in agent.run("device_info")
    policy.revoke(Permission.DEVICE_INFO)
    with pytest.raises(PermissionError):
        agent.run("device_info")


def test_emergency_stop_overrides_everything(tmp_path):
    policy = PolicyEngine()
    policy.audit.path = tmp_path / "audit.jsonl"
    policy.grant(Permission.DEVICE_INFO)
    policy.stop()
    with pytest.raises(PermissionError, match="Arrêt d'urgence"):
        SafeDeviceAgent(policy).run("device_info")


def test_robot_requires_confirmation():
    policy = PolicyEngine()
    policy.grant(Permission.ROBOT_CONTROL)
    allowed, reason = policy.authorize("move_robot")
    assert not allowed
    assert "Confirmation" in reason


def test_robot_driver_receives_only_confirmed_safe_move():
    class Driver:
        def __init__(self):
            self.calls = []

        def move(self, direction, distance_m):
            self.calls.append((direction, distance_m))

    policy = PolicyEngine()
    policy.grant(Permission.ROBOT_CONTROL)
    driver = Driver()
    controller = SafeRobotController(SafeDeviceAgent(policy), driver)
    controller.move("forward", 1.5, confirmed=True)
    assert driver.calls == [("forward", 1.5)]


def test_app_can_be_taught_and_remembers_only_explicit_facts(tmp_path):
    app = AibiApp(LocalMemory(tmp_path / "memory.json"))
    assert "ne sais pas" in app.respond("Quel est mon animal ?")
    assert "mémorisé" in app.respond("/apprendre animal = chat")
    assert app.respond("Quel est mon animal ?") == "chat"
    assert "1 information" in app.respond("/memoire")
