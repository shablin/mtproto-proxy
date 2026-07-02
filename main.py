import asyncio
import argparse
from src import storage, checker, generator, providers, logger
import logging
from src.exceptions import (
    BaseError,
    ConfigError,
    StorageError,
    TelegramError,
)


logger.setup_logger()
logger_ = logging.getLogger("System")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "MTProto Proxy Aggregation Tool. "
            "This tool allows you to fetch, "
            "check and validate proxies"
        ),
        epilog=(
            "Notes on write modes: "
            "--append (-p) can cause the raw proxy file to grow without bound over time. "
            "Duplicates across different runs are possible in append mode. "
            "Run with --overwrite (-o) once to reset/truncate the file if it becomes too large"
        )
    )

    providers_group = parser.add_mutually_exclusive_group(required=True)
    
    providers_group.add_argument(
        "-a", "--auto", action="store_true",
        help="Automatic mode fetches fresh proxies from providers and put it into raw proxy file"
    )

    providers_group.add_argument(
        "-m", "--manual", action="store_true",
        help="Manual mode works with existing raw proxy file that prepared by you"
    )

    
    write_mode_group = parser.add_mutually_exclusive_group(required=False)
    
    write_mode_group.add_argument(
        "-o", "--overwrite", action="store_true",
        help="Overwrite mode (default) truncates raw proxy file and write fresh entries from scratch"
    )

    write_mode_group.add_argument(
        "-p", "--append", action="store_true",
        help="Append mode preserves file content and append new entries to the end"
    )

    return parser.parse_args()


async def main():
    try:
        args = parse_arguments()
        write_mode = "append" if args.append else "overwrite"

        if args.auto:
            logger_.info(f"Running in automatic mode... (write_mode: {write_mode})")
            await providers.aggregate_proxies(write_mode=write_mode)
        elif args.manual:
            logger_.info(f"Running in manual mode... (write_mode: {write_mode})")

            if args.append:
                logger_.warning("Append writing mode combined with Manual mode has no effect")
        
        raw_proxies = storage.load_raw_proxies()
        if not raw_proxies:
            print("no raw proxies found")
            return
        
        alive_proxies = await checker.run_checker(raw_proxies)

        storage.save_results(alive_proxies)

        valid_data = storage.load_valid_json()
        stats = generator.calculate_metrics(len(raw_proxies), valid_data)

        generator.generate_readme(stats)
        generator.send_telegram_notification(stats)
        generator.generate_webpage(stats)
    except ConfigError as e:
        logger_.critical(f"configuration error: {e}")
        exit(2)
    except StorageError as e:
        logger_.critical(f"storage error: {e}")
        exit(3)
    except TelegramError as e:
        logger_.error(f"telegram error: {e}")
    except BaseError as e:
        logger_.exception(f"unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())