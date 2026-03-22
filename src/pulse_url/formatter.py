from datetime import datetime

from pulse_url.checker import CheckResult, Status

_GREEN = "\033[32m"
_RED = "\033[31m"
_RESET = "\033[0m"


def _colorize(text: str, color: str) -> str:
    return f"{color}{text}{_RESET}"


def format_single(url: str, result: CheckResult) -> str:
    if result.status == Status.OK:
        tag = _colorize("[OK]  ", _GREEN)
        detail = f"{result.status_code} {result.reason}"
    elif result.status == Status.PROBLEM:
        tag = _colorize("[FAIL]", _RED)
        detail = f"{result.status_code} {result.reason}"
    else:
        tag = _colorize("[FAIL]", _RED)
        detail = result.reason

    return f"{tag} {url} -- {detail} ({result.elapsed_ms}ms)"


def format_watch_line(url: str, result: CheckResult) -> str:
    now = datetime.now().strftime("%H:%M:%S")

    if result.status == Status.OK:
        tag = _colorize("[OK]  ", _GREEN)
        detail = f"{result.status_code} {result.reason}"
    elif result.status == Status.PROBLEM:
        tag = _colorize("[FAIL]", _RED)
        detail = f"{result.status_code} {result.reason}"
    else:
        tag = _colorize("[FAIL]", _RED)
        detail = result.reason

    return f"[{now}] {tag} {url} -- {detail:<16} {result.elapsed_ms}ms"
