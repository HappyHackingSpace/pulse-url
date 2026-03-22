from datetime import timedelta
from unittest.mock import patch

import click
import httpx
import pytest
from click.testing import CliRunner

from pulse_url.cli import main, parse_duration


class TestParseDuration:
    def test_seconds(self):
        assert parse_duration("10s") == 10

    def test_minutes(self):
        assert parse_duration("2m") == 120

    def test_hours(self):
        assert parse_duration("1h") == 3600

    def test_invalid_format_raises(self):
        with pytest.raises(click.BadParameter, match="Invalid duration format"):
            parse_duration("10x")

    def test_missing_unit_raises(self):
        with pytest.raises(click.BadParameter):
            parse_duration("10")

    def test_empty_raises(self):
        with pytest.raises(click.BadParameter):
            parse_duration("")


def _make_response(status_code: int, elapsed_s: float = 0.1):
    resp = httpx.Response(
        status_code=status_code, request=httpx.Request("GET", "https://example.com")
    )
    resp.elapsed = timedelta(seconds=elapsed_s)
    return resp


class TestCheckCommand:
    @patch("pulse_url.url_reader.sys.stdin")
    @patch("pulse_url.cli.check_url")
    def test_single_url_ok(self, mock_check, mock_stdin):
        mock_stdin.isatty.return_value = True
        from pulse_url.checker import CheckResult, Status

        mock_check.return_value = CheckResult(Status.OK, 200, "OK", 100)

        runner = CliRunner()
        result = runner.invoke(main, ["check", "https://example.com"])

        assert result.exit_code == 0
        assert "[OK]" in result.output

    @patch("pulse_url.url_reader.sys.stdin")
    @patch("pulse_url.cli.check_url")
    def test_single_url_fail_exits_1(self, mock_check, mock_stdin):
        mock_stdin.isatty.return_value = True
        from pulse_url.checker import CheckResult, Status

        mock_check.return_value = CheckResult(
            Status.PROBLEM, 500, "Internal Server Error", 50
        )

        runner = CliRunner()
        result = runner.invoke(main, ["check", "https://example.com"])

        assert result.exit_code == 1
        assert "[FAIL]" in result.output

    @patch("pulse_url.url_reader.sys.stdin")
    @patch("pulse_url.cli.check_url")
    def test_multiple_urls(self, mock_check, mock_stdin):
        mock_stdin.isatty.return_value = True
        from pulse_url.checker import CheckResult, Status

        mock_check.return_value = CheckResult(Status.OK, 200, "OK", 100)

        runner = CliRunner()
        result = runner.invoke(main, ["check", "https://a.com", "https://b.com"])

        assert result.exit_code == 0
        assert mock_check.call_count == 2

    @patch("pulse_url.url_reader.sys.stdin")
    @patch("pulse_url.cli.check_url")
    def test_mixed_results_exits_1(self, mock_check, mock_stdin):
        mock_stdin.isatty.return_value = True
        from pulse_url.checker import CheckResult, Status

        mock_check.side_effect = [
            CheckResult(Status.OK, 200, "OK", 100),
            CheckResult(Status.PROBLEM, 404, "Not Found", 50),
        ]

        runner = CliRunner()
        result = runner.invoke(main, ["check", "https://a.com", "https://b.com"])

        assert result.exit_code == 1

    def test_version_flag(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help_flag(self):
        runner = CliRunner()
        result = runner.invoke(main, ["check", "--help"])

        assert result.exit_code == 0
        assert "Check if one or more URLs are alive" in result.output

    @patch("pulse_url.url_reader.sys.stdin")
    def test_no_urls_shows_error(self, mock_stdin):
        mock_stdin.isatty.return_value = True
        runner = CliRunner()
        result = runner.invoke(main, ["check"])

        assert result.exit_code != 0
        assert "No URLs provided" in result.output
