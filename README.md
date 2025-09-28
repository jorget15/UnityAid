# UnityAid — Local Development README

Small FastAPI demo for disaster report ingestion, background matching, and a live dashboard (SSE).

This README explains how to run the app locally, the main endpoints, a short SSE example, and troubleshooting tips.

## Requirements

- Python 3.11+ (3.12/3.13 should work)
- A virtual environment (recommended)

Dependencies are listed in `requirements.txt`.

## Quick start (macOS / zsh)

1. Create and activate a virtual environment (from project root):

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app with uvicorn:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

4. Open the dashboard in your browser:

- Dashboard: http://127.0.0.1:8000/ui/dashboard
- Submit form: http://127.0.0.1:8000/ui/form

## API endpoints

All endpoints are available under `/api/*` (legacy non-`/api` paths still work):

- GET /api/health — server health
- GET /api/reports — list reports
- POST /api/report — create a report (JSON)
- GET /api/resources — list resources and capacities
- GET /agent/events — recent in-memory agent events (debug)

Example POST body for `/api/report`:

```json
{
  "lat": 25.77,
  "lon": -80.19,

## Quick curl examples

Post a report (zsh-friendly):

```bash
printf '%s' '{"description":"Quick test","lat":25.77,"lon":-80.19,"urgency":5}' > /tmp/test_report.json
curl -v -H 'Content-Type: application/json' -d @/tmp/test_report.json http://127.0.0.1:8000/api/report
```

Fetch reports:

```bash
curl http://127.0.0.1:8000/api/reports
```

Connect with a simple SSE client (Node/browser compatible):

const es = new EventSource('/api/stream');
es.onmessage = e => console.log('event', JSON.parse(e.data));
es.onerror = e => console.error(e);

Command-line (curl) will show SSE stream headers; it isn't ideal for long runs but works for quick debugging:

```bash
```

## How the app works (short)

- Reports posted to `/api/report` are queued. A background `loop_agent` coroutine dequeues reports, categorizes them, and matches them to the nearest resource with capacity.
- Matches decrement the resource capacity in memory. Events are broadcast to connected SSE clients.

## Agent-to-Agent (A2A) message bus


Included example agents and message flow:
1. When a report is created the backend publishes a `ReportCreated` A2A message.
2. `categorizer_agent.py` subscribes to `/a2a/subscribe`, listens for `ReportCreated`, and posts `ReportCategorized` messages.
3. `matcher_agent.py` subscribes to `/a2a/subscribe`, listens for `ReportCategorized`, selects a resource, and posts `ResourceMatched` messages.

Running the example agents locally

1. Start the backend (single-process is recommended for this demo):

source venv/bin/activate
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
2. In two separate terminals start the agents:

```

```


Notes and production guidance

- Agents use HTTP streaming (`httpx.stream`) with minimal reconnect logic. In production agents should implement robust backoff, health checks, and idempotent handling.

```yaml
version: '3.8'
    ports:
      - '6379:6379'
  backend:
    build: .
    command: python -m uvicorn app:app --host 0.0.0.0 --port 8000
    ports:
      - '8000:8000'
    depends_on:
      - redis
  categorizer:
    build: .
    command: python categorizer_agent.py
    depends_on:
      - backend
      - redis
  matcher:
    build: .
    command: python matcher_agent.py
    depends_on:
      - backend
      - redis
```

You can adapt the backend to use Redis pub/sub and bridge A2A via Redis; if you want I can scaffold that bridge so the backend uses Redis and the SSE relays messages from Redis to clients.

## Logs

The app writes rotating logs to `logs/unityaid.log`. If you don't see logs, ensure the `logs/` directory exists and the process user can write to it.

## Troubleshooting

- Port already in use: stop other uvicorn processes or change `--port`.
- SSE not receiving events: SSE is in-memory and per-process; ensure you're connected to the same process that runs the background agent (don't use multiple uvicorn workers with `--workers > 1` unless you switch to an external pub/sub).
- If endpoints return 404, ensure the server is running and you are using the correct host/port.

## Next steps / optional

- Wire persistent storage for reports/resources
- Replace in-memory pub/sub with Redis pub/sub for multi-worker SSE
- Add tests that validate enqueue -> agent matching -> event emission


