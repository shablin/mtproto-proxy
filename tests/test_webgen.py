import pytest

from src.generator import generate_webpage
from src.models import ProxyMetrics, ProxyInfo

def test_webpage_generator():
    proxy = ProxyInfo(
        host="server1.tg.org",
        alive=True,
        latency_ms=1337,
        port=25565,
        secret="secret1",
        url="tg://"
    )

    proxy_two = ProxyInfo(
        host="server2.tg.org",
        alive=True,
        latency_ms=512,
        port=443,
        secret="sas2",
        url="tg://"
    )

    stats = ProxyMetrics(
        alive_count=2000,
        avg_latency=20,
        dead_count=1,
        rate=100,
        total=200,
        valid=[proxy,proxy_two]
    )

    generate_webpage(stats)