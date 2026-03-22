import re
import sys

import click

from pulse_url.checker import check_url
from pulse_url.formatter import format_single
from pulse_url.url_reader import read_urls
from pulse_url.watcher import watch_urls


def parse_duration(value: str) -> float:
    match = re.fullmatch(r"(\d+)(s|m|h)", value)
    if not match:
        raise click.BadParameter(
            f"Invalid duration format: '{value}'. Use e.g. 10s, 2m, 1h"
        )
    amount = int(match.group(1))
    unit = match.group(2)
    multipliers = {"s": 1, "m": 60, "h": 3600}
    return amount * multipliers[unit]


@click.group()
@click.version_option("0.1.0", prog_name="pulse_url")
def main() -> None:
    """pulse_url - CLI tool to check if URLs are alive."""


@main.command()
@click.argument("urls", nargs=-1)
@click.option(
    "--file", "-f", default=None, help="Read URLs from a file (one per line)."
)
@click.option("--watch", "-w", is_flag=True, help="Enable continuous monitoring mode.")
@click.option(
    "--interval",
    "-i",
    default="30s",
    show_default=True,
    help="Watch interval (e.g. 10s, 2m, 1h).",
)
@click.option(
    "--token", "-t", default=None, help="Sent as Authorization: Bearer header."
)
@click.option(
    "--timeout",
    default="5s",
    show_default=True,
    help="HTTP request timeout (e.g. 5s, 1m).",
)
def check(
    urls: tuple[str, ...],
    file: str | None,
    watch: bool,
    interval: str,
    token: str | None,
    timeout: str,
) -> None:
    """Check if one or more URLs are alive.

    URLs can be passed as arguments, read from a file (--file), or piped via stdin.

    \b
    Status logic:
      2xx         -> [OK]   alive
      3xx/4xx/5xx -> [FAIL] problem (HTTP code is shown)
      timeout     -> [FAIL] unreachable

    \b
    Examples:
      pulse_url check https://example.com
      pulse_url check https://a.com https://b.com --timeout 10s
      pulse_url check --file urls.txt --watch --interval 10s
      cat urls.txt | pulse_url check
    """
    all_urls = read_urls(urls, file)
    timeout_sec = parse_duration(timeout)

    if watch:
        interval_sec = parse_duration(interval)
        watch_urls(all_urls, interval_sec, timeout_sec, token)
    else:
        has_failure = False
        for url in all_urls:
            result = check_url(url, timeout=timeout_sec, token=token)
            click.echo(format_single(url, result))
            if result.status_code is None or result.status_code >= 300:
                has_failure = True
        if has_failure:
            sys.exit(1)
