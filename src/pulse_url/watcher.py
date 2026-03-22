import time

import click

from pulse_url.checker import check_url
from pulse_url.formatter import format_watch_line


def watch_urls(
    urls: list[str],
    interval: float,
    timeout: float,
    token: str | None,
) -> None:
    label = ", ".join(urls)
    click.echo(f"Watching {label} every {int(interval)}s -- Ctrl+C to stop\n")

    try:
        while True:
            for url in urls:
                result = check_url(url, timeout=timeout, token=token)
                click.echo(format_watch_line(url, result))
            if len(urls) > 1:
                click.echo("")
            time.sleep(interval)
    except KeyboardInterrupt:
        click.echo("\nStopped.")
