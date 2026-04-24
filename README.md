# You Know Game

A simple FastAPI + React app for running `You Know ____ Is a Lot Like ____` with fresh LLM-generated prompt pairs.

## What It Does

- Generates unique prompt pairs using the OpenAI API
- Shows a game-show style prompt stage in React
- Includes think and explain timers
- Tracks player order, round scores, leaderboard, and recent history

## Project Layout

- `backend/` - FastAPI API for health checks and prompt generation
- `frontend/` - Vite React client for the game interface
- `you-know-game.md` - original game concept notes

## Backend Setup

1. Create a virtual environment at the workspace root named `.venv`.
2. Install dependencies from `backend/requirements.txt`.
3. Copy `backend/.env.example` to `backend/.env`.
4. Add your Azure OpenAI key to `AZURE_OPENAI_API_KEY`.
5. Make sure your local identity can access Azure AI Speech, for example with `az login`.
5. Start the API from the `backend/` folder:

```bash
uvicorn app.main:app --reload --port 8000
```

## Frontend Setup

1. Install dependencies from the `frontend/` folder:

```bash
npm install
```

2. Start the Vite dev server:

```bash
npm run dev
```

The Vite server proxies `/api` and `/health` to `http://localhost:8000` during local development.

## VS Code Workflow

This workspace now includes VS Code tasks and launch configurations.

### First-Time Setup

1. Make sure the workspace root has `.venv/Scripts/python.exe`.
2. Open the workspace in VS Code.
3. Run the task `Setup: Install All`.
4. Create `backend/.env` from `backend/.env.example` and add `AZURE_OPENAI_API_KEY`.

### Run From VS Code

- Run the task `Run: Full Stack` to start both servers.
- Or press `F5` and choose `App: Full Stack` to debug the backend and start the frontend dev server.
- Use `Frontend: Open In Browser` if you want VS Code to open the app directly in Edge after the servers are up.

### What The VS Code Files Do

- `.vscode/settings.json` selects the workspace `.venv` interpreter and makes the backend import path visible to Python tooling.
- `.vscode/tasks.json` provides setup and run tasks for backend and frontend.
- `.vscode/launch.json` provides debug/run entries for FastAPI and the frontend dev server.
- `.vscode/extensions.json` recommends the Python extensions required for backend debugging.

## Environment Variables

Backend variables in `backend/.env`:

- `AZURE_OPENAI_API_KEY` - required to generate prompts with the Azure OpenAI-compatible Kimi deployment
- `OPENAI_BASE_URL` - required for Azure OpenAI-compatible routing, defaults in the example to `https://maplehack-2-resource.openai.azure.com/openai/v1`
- `OPENAI_MODEL` - optional, defaults to `Kimi-K2.6-1`
- `FRONTEND_ORIGIN` - optional, defaults to `http://localhost:5173`
- `AZURE_SPEECH_ENDPOINT` - used by the in-app announcer endpoint and `backend/synthesize_speech.py`
- `AZURE_RESOURCE_ID` - used by the in-app announcer endpoint and `backend/synthesize_speech.py` with `DefaultAzureCredential`
- `AZURE_SPEECH_VOICE` - optional, defaults to `en-US-Grant:MAI-Voice-1`
- `AZURE_SPEECH_TEXT` - optional default text for speech synthesis
- `AZURE_SPEECH_OUTPUT_FILE` - optional output file path; if unset, audio plays through the default speaker

Optional frontend variable in `frontend/.env.local`:

- `VITE_API_BASE_URL` - set this if you do not want to use the dev proxy

## API Shape

### `GET /health`

Returns API health and whether the Kimi model and Azure Speech announcer are configured.

### `POST /api/prompts`

Request body:

```json
{
  "recent_prompts": [
    "You know designing a landing zone is a lot like planning a wedding."
  ]
}
```

### `POST /api/speech`

Request body:

```json
{
  "text": "You know landing a zero trust review is a lot like organizing a family road trip."
}
```

Response body:

Returns `audio/wav` bytes for the excitable announcer voice.

Response body:

```json
{
  "technicalThing": "running an architecture review",
  "everydayThing": "judging a cooking show",
  "fullPrompt": "You know running an architecture review is a lot like judging a cooking show.",
  "rationaleHint": "Both depend on balancing taste, constraints, and strong opinions without losing the overall standard."
}
```

## Notes

- Prompt uniqueness is handled with both frontend round history and a small backend in-memory cache.
- If `AZURE_OPENAI_API_KEY` is missing, the frontend still loads but prompt generation returns a configuration error.
- The main frontend action now spins a prompt and tries to auto-play the Azure Speech announcer immediately.

## Azure Speech Demo

Install backend dependencies, run `az login` or otherwise configure `DefaultAzureCredential`, and then run:

```bash
.venv\Scripts\python.exe backend\synthesize_speech.py --output-file backend\outputs\speech.wav
```

If you omit `--output-file`, the script sends audio to the default speaker instead.
