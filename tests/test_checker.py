from datetime import timedelta
from unittest.mock import patch

import httpx

from pulse_url.checker import Status, check_url


def _make_response(status_code: int, reason: str = "OK", elapsed_s: float = 0.15):
    resp = httpx.Response(
        status_code=status_code, request=httpx.Request("GET", "https://example.com")
    )
    resp.headers = {}
    resp.elapsed = timedelta(seconds=elapsed_s)
    return resp


class TestCheckUrl:
    @patch("pulse_url.checker.httpx.get")
    def test_returns_ok_for_2xx(self, mock_get):
        mock_get.return_value = _make_response(200, "OK")
        result = check_url("https://example.com")

        assert result.status == Status.OK
        assert result.status_code == 200
        assert result.elapsed_ms == 150

    @patch("pulse_url.checker.httpx.get")
    def test_returns_ok_for_204(self, mock_get):
        mock_get.return_value = _make_response(204, "No Content")
        result = check_url("https://example.com")

        assert result.status == Status.OK
        assert result.status_code == 204

    @patch("pulse_url.checker.httpx.get")
    def test_returns_problem_for_404(self, mock_get):
        mock_get.return_value = _make_response(404, "Not Found")
        result = check_url("https://example.com")

        assert result.status == Status.PROBLEM
        assert result.status_code == 404

    @patch("pulse_url.checker.httpx.get")
    def test_returns_problem_for_500(self, mock_get):
        mock_get.return_value = _make_response(500, "Internal Server Error")
        result = check_url("https://example.com")

        assert result.status == Status.PROBLEM
        assert result.status_code == 500

    @patch("pulse_url.checker.httpx.get")
    def test_returns_problem_for_301(self, mock_get):
        mock_get.return_value = _make_response(301, "Moved Permanently")
        result = check_url("https://example.com")

        assert result.status == Status.PROBLEM
        assert result.status_code == 301

    @patch("pulse_url.checker.httpx.get")
    def test_returns_unreachable_on_timeout(self, mock_get):
        mock_get.side_effect = httpx.ReadTimeout("timed out")
        result = check_url("https://example.com", timeout=5.0)

        assert result.status == Status.UNREACHABLE
        assert result.status_code is None
        assert "TIMEOUT" in result.reason
        assert result.elapsed_ms == 5000

    @patch("pulse_url.checker.httpx.get")
    def test_returns_unreachable_on_connection_error(self, mock_get):
        mock_get.side_effect = httpx.ConnectError("connection refused")
        result = check_url("https://example.com")

        assert result.status == Status.UNREACHABLE
        assert result.status_code is None
        assert result.reason == "UNREACHABLE"

    @patch("pulse_url.checker.httpx.get")
    def test_sends_bearer_token(self, mock_get):
        mock_get.return_value = _make_response(200)
        check_url("https://example.com", token="my-secret")

        _, kwargs = mock_get.call_args
        assert kwargs["headers"]["Authorization"] == "Bearer my-secret"

    @patch("pulse_url.checker.httpx.get")
    def test_no_auth_header_without_token(self, mock_get):
        mock_get.return_value = _make_response(200)
        check_url("https://example.com")

        _, kwargs = mock_get.call_args
        assert "Authorization" not in kwargs["headers"]

    @patch("pulse_url.checker.httpx.get")
    def test_passes_timeout_to_httpx(self, mock_get):
        mock_get.return_value = _make_response(200)
        check_url("https://example.com", timeout=10.0)

        _, kwargs = mock_get.call_args
        assert kwargs["timeout"] == 10.0

    @patch("pulse_url.checker.httpx.get")
    def test_follow_redirects_disabled(self, mock_get):
        mock_get.return_value = _make_response(200)
        check_url("https://example.com")

        _, kwargs = mock_get.call_args
        assert kwargs["follow_redirects"] is False
