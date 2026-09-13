import argparse
import json

from .app import run_chat
from .agent import SafeDeviceAgent
from .models import Permission


def main() -> None:
    parser = argparse.ArgumentParser(description="Application AIBI à permissions explicites.")
    parser.add_argument("action", choices=["chat", "device_info", "list_home", "shell"])
    parser.add_argument("--silent", action="store_true", help="Ne pas lire les réponses à voix haute.")
    parser.add_argument("--allow-device-info", action="store_true")
    parser.add_argument("--allow-read-files", action="store_true")
    args = parser.parse_args()

    if args.action == "chat":
        run_chat(voice_enabled=not args.silent)
        return

    agent = SafeDeviceAgent()
    if args.allow_device_info:
        agent.policy.grant(Permission.DEVICE_INFO)
    if args.allow_read_files:
        agent.policy.grant(Permission.READ_FILES)
    try:
        print(json.dumps(agent.run(args.action), ensure_ascii=False, indent=2))
    except (PermissionError, RuntimeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
