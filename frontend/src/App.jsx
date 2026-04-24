import { useEffect, useRef, useState } from 'react';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const INITIAL_HEALTH = {
  status: 'checking',
  openaiConfigured: false,
  speechConfigured: false,
  model: '',
};

function apiUrl(path) {
  return API_BASE_URL ? `${API_BASE_URL}${path}` : path;
}

function App() {
  const [prompt, setPrompt] = useState(null);
  const [history, setHistory] = useState([]);
  const [loadingPrompt, setLoadingPrompt] = useState(false);
  const [speakingPrompt, setSpeakingPrompt] = useState(false);
  const [error, setError] = useState('');
  const [health, setHealth] = useState(INITIAL_HEALTH);
  const audioRef = useRef(null);
  const audioUrlRef = useRef('');

  useEffect(() => {
    let cancelled = false;

    async function loadHealth() {
      try {
        const response = await fetch(apiUrl('/health'));
        const data = await response.json();
        if (!cancelled) {
          setHealth(data);
        }
      } catch {
        if (!cancelled) {
          setHealth({ ...INITIAL_HEALTH, status: 'offline' });
        }
      }
    }

    loadHealth();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => () => {
    stopActiveAudio();
  }, []);

  function stopActiveAudio() {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = '';
    }

    setSpeakingPrompt(false);
  }

  async function playPromptAudio(text) {
    if (!text || !health.speechConfigured) {
      return;
    }

    const response = await fetch(apiUrl('/api/speech'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const contentType = response.headers.get('content-type') || '';
      const detail = contentType.includes('application/json')
        ? (await response.json()).detail
        : 'Unable to play the announcer voice right now.';
      throw new Error(detail || 'Unable to play the announcer voice right now.');
    }

    const audioBlob = await response.blob();
    stopActiveAudio();

    const objectUrl = URL.createObjectURL(audioBlob);
    audioUrlRef.current = objectUrl;

    const audio = new Audio(objectUrl);
    audioRef.current = audio;
    audio.onended = () => {
      setSpeakingPrompt(false);
    };
    audio.onerror = () => {
      setSpeakingPrompt(false);
      setError('Prompt ready, but audio playback failed. Click Replay Announcer to try again.');
    };

    setSpeakingPrompt(true);
    try {
      await audio.play();
    } catch {
      setSpeakingPrompt(false);
      throw new Error('Prompt ready, but your browser blocked autoplay. Click Replay Announcer.');
    }
  }

  async function generatePrompt() {
    setLoadingPrompt(true);
    setError('');
    try {
      const response = await fetch(apiUrl('/api/prompts'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recent_prompts: history.slice(-12).map((entry) => entry.fullPrompt || ''),
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Unable to generate a prompt right now.');
      }

      setPrompt(data);
      setHistory((current) => [data, ...current].slice(0, 20));
      setError('');
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoadingPrompt(false);
    }
  }

  async function replayPrompt() {
    if (!prompt?.fullPrompt || !health.speechConfigured) {
      return;
    }

    setError('');
    try {
      await playPromptAudio(prompt.fullPrompt);
    } catch (voiceError) {
      setError(voiceError.message);
    }
  }

  return (
    <div className="page-shell">
      <div className="backdrop backdrop-one" />
      <div className="backdrop backdrop-two" />
      <main className="app-frame">
        <section className="hero-panel panel">
          <div>
            <p className="eyebrow">Live LLM-generated game prompts</p>
            <h1>You Know ____ Is a Lot Like ____</h1>
          </div>
          <div className="hero-meta">
            <div className="meta-pill">
              <span className={`status-dot ${health.openaiConfigured ? 'online' : 'offline'}`} />
              {health.openaiConfigured ? `Model: ${health.model || 'ready'}` : 'Model offline'}
            </div>
            <div className="meta-pill">
              <span className={`status-dot ${health.speechConfigured ? 'online' : 'offline'}`} />
              {health.speechConfigured ? 'Voice ready' : 'Voice offline'}
            </div>
          </div>
        </section>

        <section className="prompt-grid">
          <article className="panel prompt-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Prompt Stage</p>
              </div>
              <div className="header-buttons">
                <button className="primary-button" onClick={generatePrompt} disabled={loadingPrompt}>
                  {loadingPrompt ? 'Spinning...' : 'Spin Pair'}
                </button>
                <button
                  className="secondary-button"
                  onClick={replayPrompt}
                  disabled={!prompt || !health.speechConfigured || speakingPrompt}
                >
                  {speakingPrompt ? 'Playing...' : 'Say It'}
                </button>
              </div>
            </div>

            <div className="prompt-cards" key={prompt?.fullPrompt || 'empty'}>
              <div className="prompt-card tech-card">
                <span className="card-label">CSA Tech</span>
                <strong>{prompt?.technicalThing || 'landing a live technical task'}</strong>
              </div>
              <div className="prompt-connector">is a lot like</div>
              <div className="prompt-card life-card">
                <span className="card-label">Everyday Chaos</span>
                <strong>{prompt?.everydayThing || 'an unexpectedly normal life situation'}</strong>
              </div>
            </div>

            <div className="prompt-output">
              <p className="full-prompt">{prompt?.fullPrompt || 'Generate a pair to start the round.'}</p>
              <p className="hint-line">{prompt?.rationaleHint || 'The app will also give a one-line angle to help the player frame the analogy.'}</p>
            </div>

            {error ? <p className="error-banner">{error}</p> : null}
          </article>
        </section>
      </main>
    </div>
  );
}

export default App;
