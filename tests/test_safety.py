import pytest

from safe_device_ai import Permission, PolicyEngine, SafeDeviceAgent
from safe_device_ai.robot import SafeRobotController
from safe_device_ai.app import AibiApp
from safe_device_ai.memory import LocalMemory
from safe_device_ai.speech import SpeechUnavailable


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


def test_app_speaks_responses_and_can_be_silenced(tmp_path):
    class Speaker:
        def __init__(self):
            self.messages = []

        def speak(self, text):
            self.messages.append(text)

    speaker = Speaker()
    app = AibiApp(LocalMemory(tmp_path / "memory.json"), speaker=speaker)
    response = app.respond("Bonjour")
    app.speak_response(response)
    assert speaker.messages == [response]
    app.respond("/voix off")
    app.speak_response("Silence")
    assert speaker.messages == [response]


def test_missing_speech_engine_falls_back_to_text(tmp_path):
    class MissingSpeaker:
        def speak(self, text):
            raise SpeechUnavailable("absent")

    app = AibiApp(LocalMemory(tmp_path / "memory.json"), speaker=MissingSpeaker())
    app.speak_response("Réponse")
    assert app.voice_enabled is False


def test_repeated_unknown_response_does_not_echo_forever(tmp_path):
    app = AibiApp(LocalMemory(tmp_path / "memory.json"), voice_enabled=False)
    first = app.respond("Une question inconnue")
    repeated = app.respond(f"AIBI : {first}")
    assert repeated == "Je viens déjà de vous indiquer que je ne connais pas encore cette réponse."
