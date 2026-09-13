import json
import re
from pathlib import Path


class LocalMemory:
    """Petite mémoire explicite : rien n'est appris sans une action de l'utilisateur."""

    def __init__(self, path: str | Path = "~/.aibi/memory.json") -> None:
        self.path = Path(path).expanduser()
        self.entries: dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open(encoding="utf-8") as stream:
            data = json.load(stream)
        if not isinstance(data, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in data.items()
        ):
            raise ValueError("La mémoire doit contenir des paires texte question/réponse.")
        self.entries = data

    def teach(self, topic: str, information: str) -> None:
        topic = topic.strip()
        information = information.strip()
        if not topic or not information:
            raise ValueError("Le sujet et l'information sont obligatoires.")
        self.entries[self._key(topic)] = information
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as stream:
            json.dump(self.entries, stream, ensure_ascii=False, indent=2)

    def answer(self, question: str) -> str:
        key = self._key(question)
        if key.startswith("aibi :"):
            key = key.removeprefix("aibi :").strip()
        if key.startswith("je ne sais pas encore répondre à cela"):
            return "Je viens déjà de vous indiquer que je ne connais pas encore cette réponse."
        if key in self.entries:
            return self.entries[key]
        words = set(key.split())
        for stored_key, answer in self.entries.items():
            if words and words.intersection(stored_key.split()):
                return answer
        return (
            "Je ne sais pas encore répondre à cela. "
            "Vous pouvez m'apprendre avec : /apprendre sujet = information"
        )

    @staticmethod
    def _key(value: str) -> str:
        return re.sub(r"\s+", " ", value.casefold()).strip()
