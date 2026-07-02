import logging

from src.models import ProxyMetrics
from src.render import MarkdownReadmeBuilder, TelegramMessageBuilder, WebPageBuilder
from src import config
from src.telegram_client import TelegramClient
from src.utils import evaluate_proxy_rate, ProxyRateEvaluation


logger = logging.getLogger("Generator")


def calculate_metrics(raw_count: int, valid_data: list[dict]) -> ProxyMetrics:
    logger.info("calculating metrics...")

    alive_count = len(valid_data)
    dead_count = raw_count - alive_count

    avg_latency = (
        round(
            sum(
                p["latency_ms"]
                for p in valid_data
            ) / alive_count, 2
        )
        if alive_count
        else 0
    )

    rate = (
        round((alive_count / raw_count * 100), 1)
        if raw_count
        else 0.0
    )

    return ProxyMetrics(
        total=raw_count,
        valid=valid_data,
        alive_count=alive_count,
        dead_count=dead_count,
        avg_latency=avg_latency,
        rate=rate
    )


def send_telegram_notification(stats: ProxyMetrics):
    telegram = TelegramClient(token=config.TELEGRAM_BOT_TOKEN)
    message, keyboard = (
        TelegramMessageBuilder()
        .add_title()
        .add_stats(stats)
        #.add_top_links(stats.valid, limit=20)
        .add_footer()
        .add_proxy_keyboard(stats.valid, max_rows=5, cols=4)
        .build()
    )

    telegram.broadcast(
        chat_ids=config.TELEGRAM_CHAT_ID,
        text=message,
        reply_markup=keyboard
    )

    evaluation = evaluate_proxy_rate(stats)
    if evaluation == ProxyRateEvaluation.BAD:
        logger.warning(f"low proxy rate detected: {stats.rate}% — {evaluation.value}")
        logger.info(f"low proxy rate message will be sent to {config.TELEGRAM_BOT_OWNER_ID}")

        telegram.send_message(
            chat_id=config.TELEGRAM_BOT_OWNER_ID,
            text=(
                f"⚠ *Attention*\n"
                f"The proxy rate is low at `{stats.rate}%` _({evaluation.value})_. "
                "Please update the proxy list immediately!"
            )
        )

    telegram.close()


def generate_readme(stats: ProxyMetrics):
    logger.info("generating README...")

    readme = (
        MarkdownReadmeBuilder()
            .add_header()
            .add_downloads_block()
            .add_stats_table(stats)
            .add_top_proxies(stats.valid, limit=20)
            .build()
    )

    with open(config.README_PATH, "w", encoding="utf-8") as file:
        file.write(readme)


def generate_webpage(stats: ProxyMetrics):
    logger.info("generating static page for GitHub Pages...")

    html = WebPageBuilder(stats=stats).build()
    (config.GH_PAGES_PUBLIC / "index.html").write_text(html, encoding="utf-8")