import shutil
import subprocess
from dataclasses import dataclass


class SpeechUnavailable(RuntimeError):
    """Le système ne propose pas de moteur vocal utilisable."""


@dataclass
class SystemSpeaker:
    """Synthèse vocale locale sans shell et sans envoi audio vers un service."""

    executable: str | None = None
    voice: str | None = None

    def __post_init__(self) -> None:
        if self.executable is None:
            self.executable = shutil.which("say") or shutil.which("espeak")

    @property
    def available(self) -> bool:
        return self.executable is not None

    def speak(self, text: str) -> None:
        if not self.executable:
            raise SpeechUnavailable(
                "Aucun moteur vocal local n'est disponible (essayez macOS 'say' ou 'espeak')."
            )
        command = [self.executable]
        if self.executable.endswith("say") and self.voice:
            command.extend(["-v", self.voice])
        command.append(text)
        try:
            subprocess.run(command, check=True, stdin=subprocess.DEVNULL)
        except OSError as error:
            raise SpeechUnavailable(f"Impossible de lancer le moteur vocal : {error}") from error
        except subprocess.CalledProcessError as error:
            raise SpeechUnavailable(f"Le moteur vocal a échoué (code {error.returncode}).") from error
