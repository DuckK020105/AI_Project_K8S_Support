"""src/ui/styles.py — Blue-black terminal theme."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Inter:wght@300;400;500&display=swap');

.stApp {
    background: #020d18 !important;
    font-family: 'Inter', sans-serif;
}
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg, transparent, transparent 2px,
        rgba(0,255,170,0.012) 2px, rgba(0,255,170,0.012) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

[data-testid="stSidebar"] {
    background: #010b14 !important;
    border-right: 1px solid #0a3a5a !important;
}
[data-testid="stSidebar"] * { font-family: 'JetBrains Mono', monospace !important; }
[data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }

/* ── Top bar ───────────────────────────────── */
.topbar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #0a2a3a;
}
.topbar-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 0.05em;
    text-shadow: 0 0 16px rgba(0,212,255,0.4);
}
.topbar-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
}

/* ── Welcome screen ────────────────────────── */
.welcome-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 55vh;
    text-align: center;
}
.welcome-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #00d4ff;
    text-shadow: 0 0 24px rgba(0,212,255,0.4);
    margin-bottom: 10px;
    letter-spacing: 0.04em;
}
.welcome-sub {
    font-size: 0.95rem;
    color: #1a5a7a;
    margin-bottom: 16px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.06em;
}
.welcome-hint {
    font-size: 0.72rem;
    color: #0a3a4a;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.08em;
}

/* ── Chat bubbles ───────────────────────────── */
.chat-user {
    background: linear-gradient(135deg, #051a2e 0%, #071f38 100%);
    border: 1px solid #0a4a7a;
    border-left: 3px solid #00d4ff;
    padding: 14px 18px;
    border-radius: 0 10px 10px 10px;
    margin: 12px 0 4px 0;
    color: #c8e8f8;
    font-size: 0.9rem;
    box-shadow: 0 4px 20px rgba(0,212,255,0.08);
}
.chat-user::before {
    content: '> USER';
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; color: #00d4ff; font-weight: 700;
    letter-spacing: 0.15em; display: block; margin-bottom: 8px;
}
.chat-assistant {
    background: linear-gradient(135deg, #030f1a 0%, #051628 100%);
    border: 1px solid #0a3a5a;
    border-left: 3px solid #00ff9d;
    padding: 14px 18px;
    border-radius: 0 10px 10px 10px;
    margin: 4px 0 12px 0;
    color: #b8d8e8;
    font-size: 0.9rem;
    box-shadow: 0 4px 20px rgba(0,255,157,0.06);
}
.chat-assistant::before {
    content: '⎈ K8s Tech Support';
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; color: #00ff9d; font-weight: 700;
    letter-spacing: 0.15em; display: block; margin-bottom: 8px;
}

.doc-chips { margin-top: 10px; padding-top: 8px; border-top: 1px solid #0a2a3a; }
.doc-chip {
    display: inline-block; background: #041020;
    border: 1px solid #0a3a5a; color: #1a7aaa;
    font-size: 0.67rem; padding: 2px 8px; border-radius: 3px;
    margin: 2px 3px 2px 0; font-family: 'JetBrains Mono', monospace;
}
.meta-row {
    font-size: 0.67rem; color: #0a4a6a; margin-top: 6px;
    font-family: 'JetBrains Mono', monospace; letter-spacing: 0.05em;
}

/* ── Status badges ─────────────────────────── */
.status-badge {
    display: inline-block; padding: 4px 14px; border-radius: 3px;
    font-size: 0.68rem; font-weight: 700;
    font-family: 'JetBrains Mono', monospace; letter-spacing: 0.1em;
}
.badge-ready   { background:#031a0f; color:#00ff9d; border:1px solid #00ff9d44; }
.badge-loading { background:#1a1200; color:#ffcc00; border:1px solid #ffcc0044; }
.badge-error   { background:#1a0505; color:#ff4444; border:1px solid #ff444444; }
.badge-idle    { background:#0a1520; color:#1a5a7a; border:1px solid #0a3a5a;  }

/* ── Streamlit overrides ───────────────────── */
.stTextInput input {
    background: #041020 !important; border: 1px solid #0a3a5a !important;
    border-radius: 4px !important; color: #c8e8f8 !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 0.85rem !important;
}
.stTextInput input:focus { border-color: #00d4ff !important; box-shadow: 0 0 0 1px #00d4ff44 !important; }
.stButton button {
    background: #041020 !important; border: 1px solid #0a4a7a !important;
    color: #00d4ff !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important; font-weight: 600 !important;
    letter-spacing: 0.08em !important; border-radius: 4px !important;
    transition: all 0.15s ease !important;
}
.stButton button:hover { background: #051a35 !important; border-color: #00d4ff !important; box-shadow: 0 0 12px rgba(0,212,255,0.2) !important; }
[data-testid="stFormSubmitButton"] button { background: #00d4ff22 !important; border: 1px solid #00d4ff !important; color: #00d4ff !important; }
.stSelectbox [data-baseweb="select"] div { background: #041020 !important; border-color: #0a3a5a !important; color: #c8e8f8 !important; font-family: 'JetBrains Mono', monospace !important; }
hr { border-color: #0a2a3a !important; }
.stCaption, small { color: #1a5a7a !important; font-family: 'JetBrains Mono', monospace !important; }
.stSpinner p { color: #00d4ff !important; font-family: 'JetBrains Mono', monospace !important; }
.stAlert { background: #041020 !important; border: 1px solid #0a3a5a !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #010b14; }
::-webkit-scrollbar-thumb { background: #0a3a5a; border-radius: 2px; }
</style>
"""

STATUS_HTML = {
    "ready":      '<span class="status-badge badge-ready">● READY</span>',
    "loading":    '<span class="status-badge badge-loading">● LOADING</span>',
    "error":      '<span class="status-badge badge-error">● ERROR</span>',
    "not_loaded": '<span class="status-badge badge-idle">● IDLE</span>',
}
