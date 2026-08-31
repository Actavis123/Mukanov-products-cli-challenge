import json
from pathlib import Path


CONFIG_DIR = Path.home() / ".products-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"


def save_config(base_url: str, access_token: str, refresh_token: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "base_url": base_url,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    CONFIG_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8",
    )

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            "Not logged in. Run 'uv run products-cli login' first."
        )

    return json.loads(
        CONFIG_FILE.read_text(encoding="utf-8")
    )