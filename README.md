# Film AI Platform

AI-powered script breakdown tool for film/TV production. Upload a screenplay,
get a structured production breakdown (characters, props, locations,
costumes, departments) with role-specific views for AD, DOP, Gaffer, and
Producer.

## Architecture

- `frontend/` — React + Tailwind (Vite)
- `backend/` — Flask API + PostgreSQL + Celery (async AI processing)

## Local development

You'll need three things running at once: Redis (the job broker), the Flask
API, and a Celery worker (which does the actual AI analysis in the
background).

### 1. Redis

```bash
# macOS
brew install redis && brew services start redis

# Ubuntu/Debian
sudo apt install redis-server && sudo systemctl start redis-server

# Windows, if you have Docker Desktop
docker run --name film-ai-redis -p 6379:6379 -d redis:7
```

For local development without Redis or a Celery worker, set
`CELERY_TASK_ALWAYS_EAGER=true` in `backend/.env`. The API will run analysis
inside the web request. This is simpler for quick testing, but the request
will wait for the AI call to finish.

### 2. Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env: set a real DATABASE_URL (Postgres), and AI_API_KEY once you
# have a Google Gemini API key.
AI_PROVIDER=gemini
GEMINI_MODEL=gemini-3.6-flash
AI_API_KEY=your_google_gemini_api_key

flask db init && flask db migrate -m "init" && flask db upgrade

# Terminal 1: the API server
python run.py

# Terminal 2: the background worker (required for script analysis to work)
celery -A celery_worker.celery worker --loglevel=INFO

# Windows worker
.\venv\Scripts\celery.exe -A celery_worker.celery worker --loglevel=INFO --pool=solo
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173.

## Testing

```bash
cd backend
TEST_DATABASE_URL="sqlite:////tmp/test.db" python3 -m pytest tests/ -v
```

Note: Celery tasks run in "eager" mode during tests (`CELERY_TASK_ALWAYS_EAGER=True`
in the testing config), so `.delay()` calls execute inline without needing a
real Redis broker or worker process.

## Deployment (Render)

The included `backend/Procfile` defines two process types:

- `web` — the Flask API (via gunicorn)
- `worker` — the Celery worker that processes script analysis jobs

Both need to be deployed as separate Render services, sharing the same
`DATABASE_URL`, `CELERY_BROKER_URL`, and `CELERY_RESULT_BACKEND` (a Render
Redis instance). Without the worker service running, uploads and parsing
still work, but clicking "Analyze" will leave scripts stuck in
`processing` forever — the worker is what actually picks up and runs the job.

- Frontend → Netlify (or any static host — `npm run build` outputs to `dist/`)
- Backend (web + worker) → Render
- DB → Render Postgres or Supabase
- Broker → Render Redis (or Upstash)
- AI → Google Gemini API (set `AI_PROVIDER=gemini` and `AI_API_KEY`)

## Exporting a breakdown

Once a script's breakdown is complete, it can be exported as a PDF (formatted
scene-by-scene report) or CSV (spreadsheet-friendly, one row per scene) from
the breakdown view in the UI, or directly via the API:

```
GET /api/breakdowns/<script_id>/export?format=pdf
GET /api/breakdowns/<script_id>/export?format=csv
```

## Deployment (Render + Netlify)

This repo includes ready-to-use deployment configs:

- `render.yaml` — a Render Blueprint defining the API web service, the
  Celery worker service, a Redis instance, and a Postgres database. Point
  Render at this repo and it will provision all four. You'll still need to
  manually set `AI_API_KEY`, `GOOGLE_CLIENT_ID`, and `CORS_ORIGINS` (they're
  marked `sync: false` so they aren't auto-generated or committed).
- `netlify.toml` — builds the frontend from `frontend/` and serves it with
  SPA-style redirects (so client-side routing works on refresh/deep links).

The `backend/Procfile` also defines the same two process types (`web`,
`worker`) if you'd rather deploy manually instead of via the Blueprint.

**Important:** the worker is a separate deployed process from the web API.
Without it running, uploads and parsing still work, but clicking "Analyze"
will leave scripts stuck in `processing` forever — the worker is what
actually picks up and runs the AI analysis job.

- Frontend → Netlify
- Backend (web + worker) → Render
- DB → Render Postgres (or Supabase)
- Broker → Render Redis (or Upstash)
- AI → Google Gemini API (set `AI_PROVIDER=gemini` and `AI_API_KEY`)

## Production safety

The app refuses to start with `FLASK_ENV=production` if `SECRET_KEY` or
`JWT_SECRET_KEY` are still set to their insecure development defaults —
better to fail loudly at startup than run with a known secret key. Render's
Blueprint auto-generates real values for these; if deploying manually, set
your own.

## Build phases

1. **Core skeleton** — auth (local + Google), models, project CRUD
2. **Script upload & parsing** — PDF/Word text extraction
3. **AI breakdown engine** — schema-validated LLM analysis, role-based view structuring
4. **Displaying the breakdown** — Scenes/AD/DOP/Gaffer/Producer tabs in the UI
5. **Async processing & reliability** — Celery background jobs, retry handling, polling UI
6. **Polish, export, deploy** — PDF/CSV export, production safety checks, Render/Netlify deployment configs

All six phases are implemented and tested (34 backend tests, `pytest tests/`).
The one thing not yet verified against a real API key: how well Gemini's
actual output on a real screenplay matches the breakdown schema in practice.
Worth testing first thing once `AI_API_KEY` is set.
