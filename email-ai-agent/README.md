# Email AI Agent

A personal tool that reads your Gmail inbox over IMAP, uses Google Gemini to flag
subscription-related emails (streaming, SaaS, hosting, domains, telecom, gym,
paid newsletters, renewals, invoices, etc.), and shows the results in a small
React dashboard for reviewing, tagging, and exporting.

## Setup

### 1. Gmail App Password

IMAP login needs a Google **App Password**, not your normal Gmail password.

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security) and turn on
   **2-Step Verification** if it isn't already on (App Passwords require it).
2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
3. Create a new app password (name it anything, e.g. "email-ai-agent").
4. Copy the 16-character password shown — you'll paste this into `.env` below.

### 2. Gemini API key

1. Get a key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
2. **Quota note:** `gemini-2.5-flash`'s free tier caps at ~20 classification
   requests/day, and that cap is scoped **per Google Cloud project**, not per
   API key. A new key created through AI Studio's default flow lands in the
   same default project as any other key you've made there, so it won't get
   its own quota. To get an independent 20/day allowance, explicitly create
   the key under a new Google Cloud project in AI Studio.

### 3. Configure the backend

```
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and fill in `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD` (from step 1),
and `GOOGLE_API_KEY` (from step 2). `SYNC_MAX_EMAILS` defaults to 15 — keep it
well under 20 while developing/testing so a single sync doesn't exhaust the
daily quota; raise it once syncs are only picking up new mail rather than a
full backlog.

### 4. Run the backend

```
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` to confirm it's up.

### 5. Run the frontend

```
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` and click **Sync** to pull in your recent inbox.

## API endpoints

| Method | Path                | Description                                   |
|--------|---------------------|------------------------------------------------|
| POST   | `/api/sync`          | Fetch new mail, classify, store               |
| GET    | `/api/emails`        | List emails (filters: `subscription_only`, `category`, `reviewed`, `search`, `sort`, `limit`, `offset`) |
| GET    | `/api/emails/{id}`   | Single email with live-fetched full body       |
| PATCH  | `/api/emails/{id}`   | Update `reviewed` and/or `tag`                 |
| GET    | `/api/export`        | CSV export (same filters as list, no paging)   |
| GET    | `/api/stats`         | Totals, per-category counts, last sync summary |

## Known v1 limitations

- Each sync fetches only the `SYNC_MAX_EMAILS` most recent inbox messages —
  there's no incremental "since last sync" cursor yet, so very old mail
  outside that window is never picked up.
- Classification failures (network errors, malformed LLM output, quota
  exhaustion) fall back silently to `is_subscription: false` /
  `category: not_subscription` / `summary: "classification failed"` rather
  than blocking the sync — check `/api/stats` (`last_sync.error`) or look for
  that summary text if classifications look sparse.
- No authentication — this is a single-user local tool.
