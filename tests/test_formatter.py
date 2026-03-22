from unittest.mock import patch

from pulse_url.checker import CheckResult, Status
from pulse_url.formatter import format_single, format_watch_line


class TestFormatSingle:
    def test_ok_status(self):
        result = CheckResult(Status.OK, 200, "OK", 143)
        output = format_single("https://example.com", result)

        assert "[OK]" in output
        assert "https://example.com" in output
        assert "200 OK" in output
        assert "143ms" in output

    def test_problem_status(self):
        result = CheckResult(Status.PROBLEM, 404, "Not Found", 200)
        output = format_single("https://example.com", result)

        assert "[FAIL]" in output
        assert "404 Not Found" in output

    def test_unreachable_status(self):
        result = CheckResult(Status.UNREACHABLE, None, "UNREACHABLE", 0)
        output = format_single("https://example.com", result)

        assert "[FAIL]" in output
        assert "UNREACHABLE" in output


class TestFormatWatchLine:
    @patch("pulse_url.formatter.datetime")
    def test_ok_watch_line(self, mock_dt):
        mock_dt.now.return_value.strftime.return_value = "19:00:00"
        result = CheckResult(Status.OK, 200, "OK", 143)
        output = format_watch_line("https://example.com", result)

        assert "[19:00:00]" in output
        assert "[OK]" in output
        assert "https://example.com" in output
        assert "200 OK" in output
        assert "143ms" in output

    @patch("pulse_url.formatter.datetime")
    def test_fail_watch_line(self, mock_dt):
        mock_dt.now.return_value.strftime.return_value = "19:01:00"
        result = CheckResult(Status.UNREACHABLE, None, "TIMEOUT", 5000)
        output = format_watch_line("https://example.com", result)

        assert "[19:01:00]" in output
        assert "[FAIL]" in output
        assert "TIMEOUT" in output
        assert "5000ms" in output

    @patch("pulse_url.formatter.datetime")
    def test_problem_watch_line(self, mock_dt):
        mock_dt.now.return_value.strftime.return_value = "12:00:00"
        result = CheckResult(Status.PROBLEM, 503, "Service Unavailable", 300)
        output = format_watch_line("https://example.com", result)

        assert "[FAIL]" in output
        assert "503 Service Unavailable" in output
