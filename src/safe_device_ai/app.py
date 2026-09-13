from .memory import LocalMemory


class AibiApp:
    """Application conversationnelle locale, volontairement simple et transparente."""

    def __init__(self, memory: LocalMemory | None = None) -> None:
        self.memory = memory or LocalMemory()

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
        if not message:
            return "Écrivez un message ou utilisez /apprendre sujet = information."
        return self.memory.answer(message)


def run_chat() -> None:
    app = AibiApp()
    print("AIBI — application locale débutante")
    print("Tapez /apprendre sujet = information, /memoire ou /quitter.")
    while True:
        try:
            message = input("Vous : ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if message.strip() == "/quitter":
            break
        try:
            print(f"AIBI : {app.respond(message)}")
        except (OSError, ValueError) as error:
            print(f"AIBI : Impossible de modifier la mémoire : {error}")
