from unittest.mock import patch

import click
import pytest

from pulse_url.url_reader import read_urls, _parse_lines


class TestParseLines:
    def test_strips_whitespace(self):
        lines = ["  https://example.com  \n", "https://google.com\n"]
        assert _parse_lines(lines) == ["https://example.com", "https://google.com"]

    def test_skips_empty_lines(self):
        lines = ["https://example.com\n", "\n", "  \n", "https://google.com\n"]
        assert _parse_lines(lines) == ["https://example.com", "https://google.com"]

    def test_skips_comments(self):
        lines = [
            "# This is a comment\n",
            "https://example.com\n",
            "# Another comment\n",
        ]
        assert _parse_lines(lines) == ["https://example.com"]

    def test_empty_input(self):
        assert _parse_lines([]) == []


class TestReadUrls:
    @patch("pulse_url.url_reader.sys.stdin")
    def test_reads_from_args(self, mock_stdin):
        mock_stdin.isatty.return_value = True
        urls = read_urls(("https://a.com", "https://b.com"), file=None)
        assert urls == ["https://a.com", "https://b.com"]

    @patch("pulse_url.url_reader.sys.stdin")
    def test_reads_from_file(self, mock_stdin, tmp_path):
        mock_stdin.isatty.return_value = True
        f = tmp_path / "urls.txt"
        f.write_text("https://a.com\nhttps://b.com\n")

        urls = read_urls((), file=str(f))
        assert urls == ["https://a.com", "https://b.com"]

    @patch("pulse_url.url_reader.sys.stdin")
    def test_reads_from_stdin(self, mock_stdin):
        mock_stdin.isatty.return_value = False
        mock_stdin.__iter__ = lambda self: iter(["https://a.com\n", "https://b.com\n"])

        urls = read_urls((), file=None)
        assert urls == ["https://a.com", "https://b.com"]

    @patch("pulse_url.url_reader.sys.stdin")
    def test_combines_all_sources(self, mock_stdin, tmp_path):
        mock_stdin.isatty.return_value = False
        mock_stdin.__iter__ = lambda self: iter(["https://c.com\n"])
        f = tmp_path / "urls.txt"
        f.write_text("https://b.com\n")

        urls = read_urls(("https://a.com",), file=str(f))
        assert urls == ["https://a.com", "https://b.com", "https://c.com"]

    @patch("pulse_url.url_reader.sys.stdin")
    def test_raises_when_no_urls(self, mock_stdin):
        mock_stdin.isatty.return_value = True
        with pytest.raises(click.UsageError, match="No URLs provided"):
            read_urls((), file=None)

    @patch("pulse_url.url_reader.sys.stdin")
    def test_raises_on_invalid_file(self, mock_stdin):
        mock_stdin.isatty.return_value = True
        with pytest.raises(click.BadParameter, match="Cannot read file"):
            read_urls((), file="/nonexistent/path.txt")

    @patch("pulse_url.url_reader.sys.stdin")
    def test_file_with_comments_and_blanks(self, mock_stdin, tmp_path):
        mock_stdin.isatty.return_value = True
        f = tmp_path / "urls.txt"
        f.write_text("# comment\nhttps://a.com\n\n# another\nhttps://b.com\n")

        urls = read_urls((), file=str(f))
        assert urls == ["https://a.com", "https://b.com"]
