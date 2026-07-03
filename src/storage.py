import json
import logging
from src import config
from src.exceptions import FileReadError, FileWriteError, InvalidStorageDataError


logger = logging.getLogger("Storage")


def load_raw_proxies() -> set[str]:
    try:
        with open(config.RAW_PROXY_PATH, "r", encoding="utf-8") as file:
            logger.info("loaded raw proxy list")
            return {line.strip() for line in file if line.strip()}
    except FileNotFoundError as e:
        raise FileReadError(config.RAW_PROXY_PATH, "file not found") from e
    except OSError as e:
        raise FileReadError(config.RAW_PROXY_PATH, str(e)) from e


def load_valid_json() -> list[dict]:
    try:
        with open(config.VALID_PROXY_JSON_PATH, "r", encoding="utf-8") as file:
            logger.info("loaded valid proxy list (JSON)")
            return json.load(file)
    except FileNotFoundError as e:
        raise FileReadError(config.VALID_PROXY_JSON_PATH, "file not found") from e
    except json.JSONDecodeError as e:
        raise InvalidStorageDataError(config.VALID_PROXY_JSON_PATH, f"JSON decode: {e}") from e


def save_results(alive_proxies: list):
    config.DATA_DIR.mkdir(exist_ok=True)

    output_json = [
        {
            "url": p.url,
            "host": p.host,
            "port": p.port,
            "secret": p.secret,
            "latency_ms": p.latency_ms,
            "alive": p.alive,
        }
        for p in alive_proxies
    ]

    with open(config.VALID_PROXY_JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(output_json, file, indent=2, ensure_ascii=False)
        logger.info("saved valid proxy list (JSON)")

    with open(config.VALID_PROXY_TXT_PATH, "w", encoding="utf-8") as file:
        for p in alive_proxies:
            file.write(p.url + "\n")
            
        logger.info("saved valid proxy list (TXT)")