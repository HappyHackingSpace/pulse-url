# Pulse URL

CLI tool to check if URLs are alive.

## Quick Start

```bash
pip install -e .

pulse_url check https://example.com
```

## Usage

```bash
# Single or multiple URL check
pulse_url check https://example.com
pulse_url check https://a.com https://b.com

# Read from file
pulse_url check --file urls.txt

# Read from stdin
cat urls.txt | pulse_url check

# Continuous monitoring
pulse_url check https://example.com --watch
pulse_url check https://example.com --watch --interval 10s

# Authentication with Bearer token
pulse_url check https://example.com --token <TOKEN>
```

## Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--file` | `-f` | Read URLs from a file (one per line) | -- |
| `--watch` | `-w` | Enable continuous monitoring mode | off |
| `--interval` | `-i` | Watch interval (`10s`, `2m`, `1h`) | `30s` |
| `--token` | `-t` | Sent as `Authorization: Bearer` header | -- |
| `--timeout` | | HTTP request timeout | `5s` |

## Output

```
[OK]   https://example.com -- 200 OK (143ms)
[FAIL] https://bad.example  -- UNREACHABLE (timeout after 5s)
```

## Status Codes

| HTTP Response | Result |
|---|---|
| `2xx` | `[OK]` — alive |
| `3xx` / `4xx` / `5xx` | `[FAIL]` — HTTP code is shown |
| Connection error / timeout | `[FAIL]` — unreachable |

Exits with code `1` if any URL fails.

## Docker

```bash
# Build image
docker build -t pulse_url .

# Single check
docker run --rm pulse_url check https://example.com

# With file mount
docker run --rm -v ./urls.txt:/app/urls.txt pulse_url check --file /app/urls.txt

# Continuous monitoring
docker run --rm pulse_url check https://example.com --watch --interval 10s
```
