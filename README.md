# You Know Game

A FastAPI + React app for the live game **"You Know ____ Is a Lot Like ____"**. Spins Data & AI CSA-flavored analogy prompts with Azure OpenAI and reads them aloud with an excitable Azure AI Speech announcer voice.

## What It Does

- Generates unique Data & AI prompt pairs using Azure OpenAI (gpt-5.4-nano-1) via `DefaultAzureCredential` — no API key required if you `az login`
- Shows a clean prompt stage in React with two buttons: **Spin Pair** and **Say It**
- Speaks the prompt aloud using Azure AI Speech with an excited MAI voice (SSML `excitement` style)

## Project Layout

- `backend/` — FastAPI API for prompt generation (`/api/prompts`) and speech synthesis (`/api/speech`)
- `frontend/` — Vite React client with the prompt stage UI
- `you-know-game.md` — original game concept notes

## Quick Start

1. **Clone and set up Python:**

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r backend/requirements.txt
```

2. **Install frontend deps:**

```bash
cd frontend && npm install && cd ..
```

3. **Configure:**

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` — if you use `az login`, you only need `OPENAI_BASE_URL` and the Speech settings. No API key required.

4. **Log in to Azure and run:**

```bash
az login
```

Then start both servers (from the repo root):

```bash
# Terminal 1 — backend
cd backend && ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev
```

Open `http://localhost:5173`.

## Environment Variables

Backend variables in `backend/.env`:

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `OPENAI_BASE_URL` | Yes | — | Azure OpenAI endpoint (e.g. `https://your-resource.openai.azure.com/openai/v1`) |
| `AZURE_OPENAI_API_KEY` | No | — | If set, uses key auth; otherwise uses `DefaultAzureCredential` (`az login`) |
| `OPENAI_MODEL` | No | `gpt-5.4-nano-1` | Model deployment name |
| `AZURE_SPEECH_ENDPOINT` | Yes | — | Azure AI Speech endpoint |
| `AZURE_RESOURCE_ID` | Yes | — | ARM resource ID for the Speech resource (used for AAD token auth) |
| `AZURE_SPEECH_VOICE` | No | `en-US-Grant:MAI-Voice-1` | Voice name for speech synthesis |
| `FRONTEND_ORIGIN` | No | `http://localhost:5173` | CORS origin for the frontend |

## API Endpoints

### `GET /health`

Returns service status and whether the model and speech services are configured.

### `POST /api/prompts`

Generates a new prompt pair. Request body:

```json
{ "recent_prompts": [] }
```

Response:

```json
{
  "technicalThing": "monitoring embedding drift in a production RAG pipeline",
  "everydayThing": "finding out your favorite diner got a new head chef",
  "fullPrompt": "You know monitoring embedding drift in a production RAG pipeline is a lot like finding out your favorite diner got a new head chef.",
  "rationaleHint": "The menu looks identical, but the meaning behind every dish has shifted just enough that your usual order no longer returns what you expected."
}
```

### `POST /api/speech`

Synthesizes speech for the given text using an excited announcer voice. Returns `audio/wav` bytes.

```json
{ "text": "You know vector search is a lot like speed dating." }
```

## Notes

- Auth uses `DefaultAzureCredential` — runs with `az login` locally, managed identity in Azure.
- Prompt uniqueness is enforced by frontend history and a backend in-memory cache.
- Speech uses SSML with `mstts:express-as style='excitement'` for game-show energy.
