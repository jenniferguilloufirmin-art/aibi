from .memory import LocalMemory
from .speech import SpeechUnavailable, SystemSpeaker


class AibiApp:
    """Application conversationnelle locale, volontairement simple et transparente."""

    def __init__(
        self,
        memory: LocalMemory | None = None,
        speaker: SystemSpeaker | None = None,
        voice_enabled: bool = True,
    ) -> None:
        self.memory = memory or LocalMemory()
        self.speaker = speaker or SystemSpeaker()
        self.voice_enabled = voice_enabled

    def respond(self, message: str) -> str:
        message = message.strip()
        if message.startswith("/apprendre "):
            payload = message.removeprefix("/apprendre ")
            if "=" not in payload:
                return "Format attendu : /apprendre sujet = information"
            topic, information = payload.split("=", 1)
            self.memory.teach(topic, information)
            return f"Merci, j'ai mémorisé « {topic.strip()} »."
        if message == "/memoire":
            return f"Je connais {len(self.memory.entries)} information(s) que vous m'avez apprise(s)."
        if message == "/voix on":
            self.voice_enabled = True
            return "La voix est activée."
        if message == "/voix off":
            self.voice_enabled = False
            return "La voix est désactivée."
        if not message:
            return "Écrivez un message ou utilisez /apprendre sujet = information."
        return self.memory.answer(message)

    def speak_response(self, response: str) -> None:
        if not self.voice_enabled:
            return
        try:
            self.speaker.speak(response)
        except SpeechUnavailable:
            # Le texte reste disponible si le système n'a pas de synthèse vocale.
            self.voice_enabled = False


def run_chat(*, voice_enabled: bool = True) -> None:
    app = AibiApp(voice_enabled=voice_enabled)
    print("AIBI 2.0 — application locale débutante avec voix")
    print("Tapez /apprendre sujet = information, /voix on, /voix off ou /quitter.")
    while True:
        try:
            message = input("Vous : ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if message.strip() == "/quitter":
            break
        try:
            response = app.respond(message)
            print(f"AIBI : {response}")
            if message not in {"/voix on", "/voix off"}:
                app.speak_response(response)
        except (OSError, ValueError) as error:
            print(f"AIBI : Impossible de modifier la mémoire : {error}")
