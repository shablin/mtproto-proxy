import logging
import os
from pathlib import Path
from src.exceptions import MissingEnvVarError, InvalidConfigValueError


logger = logging.getLogger("Config")


BASE_DIR = Path(__file__).resolve().parent.parent


DATA_DIR = BASE_DIR / "data"
RAW_PROXY_PATH = DATA_DIR / "raw_proxy.txt"
VALID_PROXY_JSON_PATH = DATA_DIR / "valid_proxy.json"
VALID_PROXY_TXT_PATH = DATA_DIR / "valid_proxy.txt"
README_PATH = BASE_DIR / "README.md"
PROVIDERS_PATH = DATA_DIR / "providers.txt"


GH_PAGES_PUBLIC = BASE_DIR / "public"
JINJA2_TEMPLATES_DIR = BASE_DIR / "src" / "templates"


PROBE_TIMEOUT = 5.0
CONCURRENCY = 100


TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_OWNER_ID = os.environ.get("TELEGRAM_BOT_OWNER_ID")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


try:
    TELEGRAM_CHAT_ID = [
        chat.strip()
        for chat in TELEGRAM_CHAT_ID.split(',')
        if chat.strip()
    ]
except Exception as e:
    raise InvalidConfigValueError(
        var_name="TELEGRAM_CHAT_ID",
        value=TELEGRAM_CHAT_ID,
        reason=str(e),
    ) from e


if not TELEGRAM_BOT_TOKEN:
    raise MissingEnvVarError("TELEGRAM_BOT_TOKEN")
elif not TELEGRAM_BOT_OWNER_ID:
    raise MissingEnvVarError("TELEGRAM_BOT_OWNER_ID")
elif not TELEGRAM_CHAT_ID:
    raise MissingEnvVarError("TELEGRAM_CHAT_ID")