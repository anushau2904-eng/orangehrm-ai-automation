import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def get_orangehrm_credentials() -> tuple[str, str]:
    username = os.getenv("ORANGEHRM_USERNAME", "")
    password = os.getenv("ORANGEHRM_PASSWORD", "")
    missing = [
        name
        for name, value in (
            ("ORANGEHRM_USERNAME", username),
            ("ORANGEHRM_PASSWORD", password),
        )
        if not value.strip() or value.casefold() == "replace_me"
    ]
    if missing:
        missing_names = ", ".join(missing)
        raise RuntimeError(
            f"Missing or placeholder OrangeHRM credential(s): {missing_names}. "
            "Set them in the project .env file (copy .env.example and replace "
            "the placeholders) or define these environment variables."
        )

    return username, password
