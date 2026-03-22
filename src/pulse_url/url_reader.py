import sys

import click


def read_urls(
    urls: tuple[str, ...],
    file: str | None,
) -> list[str]:
    """Collect URLs from arguments, file, and stdin."""
    collected: list[str] = []

    collected.extend(urls)

    if file:
        try:
            with open(file, encoding="utf-8") as f:
                collected.extend(_parse_lines(f))
        except OSError as e:
            raise click.BadParameter(f"Cannot read file: {e}") from e

    if not sys.stdin.isatty():
        collected.extend(_parse_lines(sys.stdin))

    if not collected:
        raise click.UsageError(
            "No URLs provided. Pass URLs as arguments, via --file, or pipe through stdin."
        )

    return collected


def _parse_lines(lines) -> list[str]:
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            result.append(stripped)
    return result
