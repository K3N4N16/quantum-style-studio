"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  K3N4N HYBRID v28.0 — RADYO YAYIN SİSTEMİ (Hafifletilmiş)                  ║
║  Groq LLM · EdgeTTS · Google TTS · Piper ONNX · Açık Tema                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ─── IMPORTS ──────────────────────────────────────────────────────────────────
import streamlit as st
import os, re, json, time, asyncio, shutil, hashlib, tempfile
import wave, subprocess, socket, zipfile, logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from io import BytesIO

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("K3N4N")

# ─── BAĞIMLILIK KONTROL (HATA VERMEZ) ──────────────────────────────────────
try:
    from huggingface_hub import hf_hub_download, snapshot_download
    HF_OK = True
except ImportError:
    HF_OK = False

try:
    from edge_tts import Communicate
    TTS_OK = True
except ImportError:
    TTS_OK = False

try:
    from groq import Groq
    GROQ_OK = True
except ImportError:
    GROQ_OK = False

try:
    from pydub import AudioSegment, effects as pydub_fx
    from pydub.generators import Sine, Square, Sawtooth
    PYDUB_OK = True
except ImportError:
    PYDUB_OK = False

try:
    from streamlit_mic_recorder import mic_recorder
    MIC_OK = True
except ImportError:
    MIC_OK = False

try:
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    NP_OK = True
except ImportError:
    NP_OK = False

try:
    from mutagen import File as MutagenFile
    MUTAGEN_OK = True
except ImportError:
    MUTAGEN_OK = False

try:
    import onnxruntime as ort
    ONNX_OK = True
except ImportError:
    ONNX_OK = False

try:
    import requests as _requests
    REQ_OK = True
except ImportError:
    REQ_OK = False

# ─── RVC (OPSİYONEL) ──────────────────────────────────────────────────────────
try:
    from rvc_python.infer import RVCInference
    RVC_OK = True
except ImportError:
    RVC_OK = False

# ─── GOOGLE TTS (OPSİYONEL) ─────────────────────────────────────────────────
try:
    from google.cloud import texttospeech
    GOOGLE_TTS_OK = True
except ImportError:
    GOOGLE_TTS_OK = False

# ─── DİZİNLER ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.abspath("/app")
OUT_DIR = os.path.join(BASE_DIR, "broadcast_output")
PLAYLIST_DIR = os.path.join(BASE_DIR, "playlist")
UVOICE_DIR = os.path.join(BASE_DIR, "user_voices")
REQUEST_DIR = os.path.join(BASE_DIR, "requests")
JINGLE_DIR = os.path.join(BASE_DIR, "jingles")
EFFECT_DIR = os.path.join(BASE_DIR, "effects")
FON_DIR = os.path.join(BASE_DIR, "fon")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
META_DIR = os.path.join(BASE_DIR, "metadata")
SCHEDULE_DIR = os.path.join(BASE_DIR, "schedules")
NEWS_DIR = os.path.join(BASE_DIR, "news_bulletins")
MEMORY_DIR = os.path.join(BASE_DIR, "anons_memory")
ANALYTICS_DIR = os.path.join(BASE_DIR, "analytics")
HISTORY_DIR = os.path.join(BASE_DIR, "voice_history")
PIPER_DIR = os.path.join(BASE_DIR, "piper_models")
SOURCE_DIR = os.path.join(BASE_DIR, "source_voices")
STREAM_DIR = os.path.join(BASE_DIR, "stream")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PODCAST_DIR = os.path.join(BASE_DIR, "podcasts")

for d in [OUT_DIR, PLAYLIST_DIR, UVOICE_DIR, REQUEST_DIR, JINGLE_DIR,
          EFFECT_DIR, FON_DIR, ARCHIVE_DIR, META_DIR, SCHEDULE_DIR,
          NEWS_DIR, MEMORY_DIR, ANALYTICS_DIR, HISTORY_DIR, PIPER_DIR,
          SOURCE_DIR, STREAM_DIR, UPLOAD_DIR, PODCAST_DIR]:
    os.makedirs(d, exist_ok=True)

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="K3N4N HYBRID v28.0",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
  --primary:#2563eb; --primary-d:#1d4ed8; --accent:#7c3aed;
  --bg:#f8fafc; --bg2:#ffffff; --bg3:#f1f5f9; --bg4:#e2e8f0;
  --border:#cbd5e1; --border2:#e2e8f0;
  --text1:#0f172a; --text2:#334155; --text3:#64748b; --text4:#94a3b8;
  --r:10px; --r2:7px;
}
*{box-sizing:border-box;}
.stApp{background:var(--bg)!important;color:var(--text1)!important;font-family:'Inter',sans-serif!important;}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border2)!important;}
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div{
  background:var(--bg2)!important;color:var(--text1)!important;
  border:1.5px solid var(--border)!important;border-radius:var(--r2)!important;}
.stButton>button{
  background:linear-gradient(135deg,var(--primary),var(--accent))!important;
  color:#fff!important;border:none!important;border-radius:var(--r2)!important;
  font-weight:600!important;padding:8px 16px!important;width:100%!important;
  transition:all .2s!important;}
.stButton>button:hover{
  background:linear-gradient(135deg,var(--primary-d),#6d28d9)!important;
  transform:translateY(-1px)!important;}
.audio,audio{width:100%!important;border-radius:var(--r2)!important;margin:4px 0!important;}
.chip{display:inline-flex;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;margin:2px;}
.chip-blue{background:#dbeafe;color:#1e40af;}
.chip-green{background:#dcfce7;color:#15803d;}
.chip-amber{background:#fef3c7;color:#92400e;}
.chip-purple{background:#ede9fe;color:#5b21b6;}
.chip-teal{background:#cffafe;color:#164e63;}
.chip-gray{background:#f1f5f9;color:#475569;}
.chip-red{background:#fee2e2;color:#991b1b;}
.song-row{display:flex;align-items:center;gap:10px;background:var(--bg2);border:1px solid var(--border2);
  border-radius:var(--r2);padding:9px 13px;margin-bottom:7px;}
.song-nm{font-size:13px;font-weight:600;color:var(--text1);flex:1;}
.song-dur{font-size:11px;color:var(--text3);font-family:monospace;}
.mono-box{background:var(--bg3);border:1px solid var(--border2);border-radius:var(--r2);
  padding:10px 14px;font-family:monospace;font-size:12px;color:var(--text2);line-height:1.7;}
.sec-lbl{font-size:11px;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:1px;
  margin:14px 0 8px;padding-bottom:6px;border-bottom:1px solid var(--border2);}
.qbar-bg{background:var(--bg4);border-radius:3px;height:5px;margin:6px 0;overflow:hidden;}
.qbar-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,#dc2626,#d97706,#16a34a);}
.sbox{background:var(--bg2);border:1px solid var(--border2);border-radius:var(--r);
  padding:14px 10px;text-align:center;}
.snum{font-size:26px;font-weight:700;color:var(--primary);line-height:1.1;}
.slbl{font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:1px;margin-top:3px;}
.footer{text-align:center;font-size:11px;color:var(--text4);border-top:1px solid var(--border2);padding:14px 0 6px;margin-top:28px;}
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def sfn(s: str, n: int = 36) -> str:
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', str(s))[:n]

def ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def fmt_dur(sec: float) -> str:
    if sec < 0: sec = 0
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def audio_dur(path: str) -> float:
    if not PYDUB_OK or not os.path.exists(path):
        return 0.0
    try:
        return len(AudioSegment.from_file(path)) / 1000.0
    except Exception:
        return 0.0

def list_audio(d: str) -> list:
    exts = (".mp3", ".wav", ".ogg", ".flac", ".m4a")
    if not os.path.isdir(d):
        return []
    return sorted([f for f in os.listdir(d) if f.lower().endswith(exts)])

def word_count(t: str) -> int:
    return len(t.split()) if t and t.strip() else 0

def est_dur(text: str, spd: int = 100) -> float:
    wpm = 130 * (spd / 100)
    return (word_count(text) / wpm) * 60 if word_count(text) else 0.0

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    text = re.sub(r'`[^`]*`', '', text)
    text = re.sub(r'\[[^\]]*\](?:\([^)]*\))?', '', text)
    text = re.sub(r'[#]{1,6}\s*', '', text)
    text = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def save_uploaded_file(uploaded_file, dest_dir: str, custom_name: str = "") -> Optional[str]:
    if uploaded_file is None:
        return None
    try:
        os.makedirs(dest_dir, exist_ok=True)
        if custom_name:
            fname = custom_name
        elif hasattr(uploaded_file, 'name') and uploaded_file.name:
            fname = uploaded_file.name
        else:
            fname = f"upload_{ts()}.wav"
        fname = sfn(fname, 80)
        if '.' not in fname:
            fname += '.wav'
        dest = os.path.join(dest_dir, fname)
        
        if hasattr(uploaded_file, 'getvalue'):
            raw = uploaded_file.getvalue()
        elif hasattr(uploaded_file, 'read'):
            try:
                uploaded_file.seek(0)
            except Exception:
                pass
            raw = uploaded_file.read()
        else:
            return None
        
        if not raw or len(raw) < 64:
            return None
        
        with open(dest, 'wb') as f:
            f.write(raw)
        
        if PYDUB_OK:
            try:
                seg = AudioSegment.from_file(dest)
                if len(seg) < 50:
                    os.remove(dest)
                    return None
                if not dest.lower().endswith('.wav'):
                    wav = os.path.splitext(dest)[0] + '.wav'
                    seg.export(wav, format='wav')
                    try:
                        os.remove(dest)
                    except Exception:
                        pass
                    return wav
            except Exception:
                pass
        
        return dest if (os.path.exists(dest) and os.path.getsize(dest) > 64) else None
    except Exception as e:
        logger.error(f"Upload: {e}")
        return None

def zip_files(paths: list, name: str = "download") -> Optional[bytes]:
    try:
        buf = BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for p in paths:
                if os.path.exists(p):
                    zf.write(p, os.path.basename(p))
        buf.seek(0)
        return buf.read()
    except Exception:
        return None

def save_meta(key: str, data: dict):
    p = os.path.join(META_DIR, f"{sfn(key)}.json")
    ex = {}
    if os.path.exists(p):
        try:
            with open(p) as f:
                ex = json.load(f)
        except Exception:
            pass
    ex.update(data)
    ex["updated"] = datetime.now().isoformat()
    with open(p, "w", encoding="utf-8") as f:
        json.dump(ex, f, ensure_ascii=False, indent=2)

def load_meta(key: str) -> dict:
    p = os.path.join(META_DIR, f"{sfn(key)}.json")
    if os.path.exists(p):
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def get_id3(path: str) -> dict:
    if not MUTAGEN_OK or not os.path.exists(path):
        return {}
    try:
        a = MutagenFile(path, easy=True)
        if a is None:
            return {}
        return {
            "title": str(a.get("title", [""])[0]),
            "artist": str(a.get("artist", [""])[0]),
            "album": str(a.get("album", [""])[0]),
            "genre": str(a.get("genre", [""])[0]),
        }
    except Exception:
        return {}

def save_history(fname: str, text: str, char: str, song: str = ""):
    p = os.path.join(HISTORY_DIR, "history.json")
    hist = []
    if os.path.exists(p):
        try:
            with open(p) as f:
                hist = json.load(f)
        except Exception:
            pass
    hist.insert(0, {"ts": datetime.now().isoformat(), "file": fname, "char": char,
                    "song": song, "preview": text[:80] + ("…" if len(text) > 80 else "")})
    hist = hist[:30]
    with open(p, "w") as f:
        json.dump(hist, f, ensure_ascii=False)

def load_history() -> list:
    p = os.path.join(HISTORY_DIR, "history.json")
    if os.path.exists(p):
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            pass
    return []

def log_event(event: str, data: dict):
    p = os.path.join(ANALYTICS_DIR, f"log_{datetime.now().strftime('%Y%m%d')}.json")
    logs = []
    if os.path.exists(p):
        try:
            with open(p) as f:
                logs = json.load(f)
        except Exception:
            pass
    logs.append({"ts": datetime.now().isoformat(), "event": event, **data})
    with open(p, "w") as f:
        json.dump(logs, f, ensure_ascii=False)

def chip_html(text: str, color: str = "blue") -> str:
    return f'<span class="chip chip-{color}">{text}</span>'

def qbar(score: int):
    st.markdown(
        f'<div class="qbar-bg"><div class="qbar-fill" style="width:{score}%"></div></div>',
        unsafe_allow_html=True
    )

def quality_score(path: str) -> int:
    if not PYDUB_OK or not os.path.exists(path):
        return 0
    try:
        seg = AudioSegment.from_file(path)
        sc = 55
        if -22 <= seg.dBFS <= -10:
            sc += 20
        elif -30 <= seg.dBFS <= -22:
            sc += 10
        if -5 <= seg.max_dBFS <= -0.5:
            sc += 20
        elif -8 <= seg.max_dBFS <= -5:
            sc += 10
        if seg.frame_rate >= 44100:
            sc += 10
        sc += 5
        return min(100, max(0, sc))
    except Exception:
        return 0

def draw_waveform(path: str, h: float = 2.0):
    if not NP_OK or not os.path.exists(path):
        return
    try:
        with wave.open(path, 'r') as wf:
            frames = wf.readframes(wf.getnframes())
            sr = wf.getframerate()
            sw = wf.getsampwidth()
            ch = wf.getnchannels()
        dt = np.int16 if sw == 2 else np.int8
        s = np.frombuffer(frames, dtype=dt)
        if ch == 2:
            s = s[::2]
        step = max(1, len(s) // 2000)
        ds = s[::step].astype(np.float32)
        mx = np.max(np.abs(ds)) or 1
        ds /= mx
        t = np.linspace(0, len(s) / sr, len(ds))
        fig, ax = plt.subplots(figsize=(10, h), facecolor='#f8fafc')
        ax.set_facecolor('#f8fafc')
        ax.fill_between(t, ds, alpha=.65, color='#2563eb')
        ax.fill_between(t, -np.abs(ds), alpha=.2, color='#7c3aed')
        ax.axhline(0, color='#cbd5e1', lw=.8)
        ax.set_xlim(0, t[-1])
        ax.set_ylim(-1.1, 1.1)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(colors='#94a3b8', labelsize=7)
        ax.set_xlabel("sn", color='#94a3b8', fontsize=7)
        plt.tight_layout(pad=.3)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    except Exception:
        pass

# ─── RVC MODELLERİ TARA ──────────────────────────────────────────────────────
def scan_rvc_models() -> list:
    if not RVC_OK:
        return []
    models = []
    seen = set()
    for root, _, files in os.walk(BASE_DIR):
        for f in files:
            if not f.endswith(".pth"):
                continue
            pth = os.path.join(root, f)
            if pth in seen:
                continue
            seen.add(pth)
            index = None
            for fi in os.listdir(root):
                if fi.endswith(".index"):
                    index = os.path.join(root, fi)
                    break
            models.append({"name": f, "label": os.path.splitext(f)[0],
                           "pth": pth, "index": index, "dir": root})
    return models

# ─── GOOGLE TTS ──────────────────────────────────────────────────────────────
GOOGLE_VOICES = {
    "🇹🇷 Türkçe (Kadın)": {"lang": "tr-TR", "voice": "tr-TR-Standard-A"},
    "🇹🇷 Türkçe (Erkek)": {"lang": "tr-TR", "voice": "tr-TR-Standard-B"},
    "🇬🇧 İngilizce (UK)": {"lang": "en-GB", "voice": "en-GB-Standard-A"},
    "🇺🇸 İngilizce (US)": {"lang": "en-US", "voice": "en-US-Standard-A"},
    "🇫🇷 Fransızca": {"lang": "fr-FR", "voice": "fr-FR-Standard-A"},
    "🇩🇪 Almanca": {"lang": "de-DE", "voice": "de-DE-Standard-A"},
    "🇪🇸 İspanyolca": {"lang": "es-ES", "voice": "es-ES-Standard-A"},
    "🇮🇹 İtalyanca": {"lang": "it-IT", "voice": "it-IT-Standard-A"},
    "🇯🇵 Japonca": {"lang": "ja-JP", "voice": "ja-JP-Standard-A"},
}

def google_tts_synthesize(text: str, voice_id: str, out_path: str,
                          speed: float = 1.0, pitch: float = 0.0) -> bool:
    if not GOOGLE_TTS_OK:
        return False
    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_config = texttospeech.VoiceSelectionParams(
            language_code=voice_id.split('-')[0] + '-' + voice_id.split('-')[1],
            name=voice_id,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=speed,
            pitch=pitch,
        )
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_config,
            audio_config=audio_config
        )
        with open(out_path, "wb") as f:
            f.write(response.audio_content)
        return os.path.exists(out_path) and os.path.getsize(out_path) > 512
    except Exception as e:
        logger.error(f"Google TTS: {e}")
        return False

# ─── PIPER TTS ──────────────────────────────────────────────────────────────────
PIPER_MODELS_TR = {
    "TR Kadın — dfki (medium)": {
        "type": "hf_repo",
        "repo": "speaches-ai/piper-tr_TR-dfki-medium",
        "src_model": "model.onnx",
        "src_config": "config.json",
        "model_file": "tr_TR-dfki-medium.onnx",
        "config_file": "tr_TR-dfki-medium.onnx.json",
        "local_name": "tr_dfki_medium",
    },
    "TR Erkek — fahrettin (medium)": {
        "type": "hf_repo",
        "repo": "speaches-ai/piper-tr_TR-fahrettin-medium",
        "src_model": "model.onnx",
        "src_config": "config.json",
        "model_file": "tr_TR-fahrettin-medium.onnx",
        "config_file": "tr_TR-fahrettin-medium.onnx.json",
        "local_name": "tr_fahrettin_medium",
    },
}

def piper_local_dir(key: str) -> str:
    return os.path.join(PIPER_DIR, PIPER_MODELS_TR.get(key, {}).get("local_name", "unknown"))

def piper_model_path(key: str) -> tuple:
    info = PIPER_MODELS_TR.get(key)
    if not info:
        return None, None
    local = piper_local_dir(key)
    if not os.path.isdir(local):
        return None, None
    for mf, cf in [
        (info.get("model_file", "model.onnx"), info.get("config_file", "config.json")),
        ("model.onnx", "config.json"),
    ]:
        mp = os.path.join(local, mf)
        cp = os.path.join(local, cf)
        if os.path.exists(mp) and os.path.getsize(mp) > 1000 and os.path.exists(cp):
            return mp, cp
    onnx = [f for f in os.listdir(local) if f.endswith(".onnx")]
    jsns = [f for f in os.listdir(local) if f.endswith(".json")]
    if onnx and jsns:
        return os.path.join(local, onnx[0]), os.path.join(local, jsns[0])
    return None, None

def _dl_url(url: str, dest: str) -> bool:
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        if REQ_OK:
            r = _requests.get(url, stream=True, timeout=300, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(65536):
                    if chunk:
                        f.write(chunk)
            return os.path.getsize(dest) > 1000
        else:
            import urllib.request
            urllib.request.urlretrieve(url, dest)
            return os.path.getsize(dest) > 1000
    except Exception:
        return False

def piper_download(key: str) -> Tuple[bool, str]:
    info = PIPER_MODELS_TR.get(key)
    if not info:
        return False, "Model tanımlı değil."
    local = piper_local_dir(key)
    os.makedirs(local, exist_ok=True)

    src_m = info.get("src_model", "model.onnx")
    src_c = info.get("src_config", "config.json")
    out_m = os.path.join(local, info.get("model_file", src_m))
    out_c = os.path.join(local, info.get("config_file", src_c))

    if os.path.exists(out_m) and os.path.getsize(out_m) > 10000 and os.path.exists(out_c):
        return True, local

    if HF_OK:
        try:
            for sn, on in [(src_m, out_m), (src_c, out_c)]:
                hf_hub_download(repo_id=info["repo"], filename=sn,
                               local_dir=local, local_dir_use_symlinks=False)
            return True, local
        except Exception:
            pass

    hf_base = f"https://huggingface.co/{info['repo']}/resolve/main"
    _dl_url(f"{hf_base}/{src_m}", out_m)
    _dl_url(f"{hf_base}/{src_c}", out_c)

    if os.path.exists(out_m) and os.path.getsize(out_m) > 10000 and os.path.exists(out_c):
        return True, local

    return False, "İndirme başarısız."

def piper_synthesize(text: str, model_path: str, config_path: str, out_path: str) -> bool:
    text = clean_text(text)
    if not text:
        return False
    
    # Piper CLI
    for pb in ["piper", "piper-tts"]:
        pb_path = shutil.which(pb)
        if pb_path:
            try:
                subprocess.run([pb_path, "--model", model_path, "--config", config_path,
                               "--output_file", out_path], input=text.encode("utf-8"),
                               capture_output=True, timeout=60)
                if os.path.exists(out_path) and os.path.getsize(out_path) > 512:
                    return True
            except Exception:
                pass
    
    # ONNX Runtime
    if ONNX_OK:
        try:
            sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
            chars = [ord(c) % 64 + 1 if ord(c) < 128 else 1 for c in text[:300]]
            phoneme_ids = np.array([0] + chars + [1], dtype=np.int64)
            input_lengths = np.array([len(phoneme_ids)], dtype=np.int64)
            scales = np.array([0.667, 1.0, 0.8], dtype=np.float32)
            inp_names = [i.name for i in sess.get_inputs()]
            inp_map = {}
            if len(inp_names) >= 1:
                inp_map[inp_names[0]] = phoneme_ids.reshape(1, -1)
            if len(inp_names) >= 2:
                inp_map[inp_names[1]] = input_lengths
            if len(inp_names) >= 3:
                inp_map[inp_names[2]] = scales.reshape(1, -1)
            audio = sess.run(None, inp_map)[0].squeeze()
            audio_int = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
            with wave.open(out_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(22050)
                wf.writeframes(audio_int.tobytes())
            return os.path.exists(out_path) and os.path.getsize(out_path) > 512
        except Exception:
            pass
    return False

# ─── TTS ENGINE ──────────────────────────────────────────────────────────────
async def run_edge_tts(text: str, voice: str, speed: int, out: str) -> bool:
    text = clean_text(text)
    if not text or not TTS_OK:
        return False
    rate = f"{speed - 100:+d}%"
    for attempt in range(2):
        try:
            await Communicate(text, voice, rate=rate).save(out)
            return os.path.exists(out) and os.path.getsize(out) > 512
        except Exception:
            await asyncio.sleep(1)
    return False

def run_rvc(inp: str, out: str, pth: str, index: Optional[str], pitch: int) -> bool:
    if not RVC_OK or not pth or not os.path.exists(pth):
        shutil.copy(inp, out)
        return True
    try:
        r = RVCInference(device="cpu:0")
        if index and os.path.exists(index):
            r.load_model(pth, index_path=index, version="v2")
            r.set_params(f0up_key=int(pitch), index_rate=0.75)
        else:
            r.load_model(pth, version="v2")
            r.set_params(f0up_key=int(pitch), index_rate=0.0)
        r.infer_file(inp, out)
        for _ in range(30):
            if os.path.exists(out) and os.path.getsize(out) > 1024:
                return True
            time.sleep(0.2)
        return False
    except Exception:
        shutil.copy(inp, out)
        return True

async def build_voice(
    text: str, voice: str, speed: int, pitch: int,
    pth: str, index: Optional[str], out_file: str,
    eq: str = "Broadcast Clear", reverb: float = 0.0, norm_db: float = -16.0,
    tts_engine: str = "EdgeTTS", piper_model: str = "TR Kadın — dfki (medium)",
    google_voice: str = "tr-TR-Standard-A", google_speed: float = 1.0,
) -> Tuple[bool, str]:
    if not text or not text.strip():
        return False, ""
    
    stamp = ts()
    tmp_tts = os.path.join(tempfile.gettempdir(), f"tts_{stamp}.wav")
    tmp_rvc = os.path.join(tempfile.gettempdir(), f"rvc_{stamp}.wav")
    dest = os.path.join(OUT_DIR, out_file)
    
    try:
        if tts_engine == "Google TTS" and GOOGLE_TTS_OK:
            ok = google_tts_synthesize(text, google_voice, tmp_tts, speed=google_speed, pitch=pitch/5)
        elif tts_engine == "Piper (ONNX/TR)":
            mp, cp = piper_model_path(piper_model)
            if mp and cp:
                ok = piper_synthesize(text, mp, cp, tmp_tts)
                if not ok:
                    ok = await run_edge_tts(text, voice, speed, tmp_tts)
            else:
                ok = await run_edge_tts(text, voice, speed, tmp_tts)
        else:
            ok = await run_edge_tts(text, voice, speed, tmp_tts)
        
        if not ok:
            return False, ""

        src = tmp_tts
        if pth and os.path.exists(pth) and RVC_OK:
            if run_rvc(tmp_tts, tmp_rvc, pth, index, pitch):
                if os.path.exists(tmp_rvc) and os.path.getsize(tmp_rvc) > 1024:
                    src = tmp_rvc

        if PYDUB_OK:
            seg = AudioSegment.from_file(src)
            if eq and eq != "Ham (Efektsiz)":
                seg = apply_eq(seg, eq)
            if reverb > 0:
                seg = apply_reverb(seg, reverb)
            seg = normalize_seg(seg, norm_db)
            seg.export(dest, format="wav")
        else:
            shutil.copy(src, dest)

        log_event("voice_generated", {"file": out_file, "voice": voice,
                                      "rvc": bool(pth and os.path.exists(pth)),
                                      "words": word_count(text), "eq": eq, "engine": tts_engine})
        return True, dest
    except Exception as e:
        logger.error(f"Pipeline: {e}")
        return False, ""
    finally:
        for fp in [tmp_tts, tmp_rvc]:
            try:
                if os.path.exists(fp):
                    os.remove(fp)
            except Exception:
                pass

# ─── SES İŞLEME ──────────────────────────────────────────────────────────────
def normalize_seg(seg: AudioSegment, target: float = -16.0) -> AudioSegment:
    if not PYDUB_OK:
        return seg
    try:
        return seg.apply_gain(target - seg.dBFS)
    except Exception:
        return seg

def apply_eq(seg: AudioSegment, preset: str) -> AudioSegment:
    if not PYDUB_OK:
        return seg
    tbl = {
        "Broadcast Clear": lambda s: pydub_fx.normalize(pydub_fx.compress_dynamic_range(s, threshold=-18, ratio=3.0)),
        "Radio Warm": lambda s: pydub_fx.normalize(s) + 1,
        "Vintage": lambda s: pydub_fx.normalize(s.low_pass_filter(4500)) - 2,
        "Deep Bass": lambda s: pydub_fx.normalize(s.high_pass_filter(60)) + 1,
        "Crisp HiFi": lambda s: pydub_fx.normalize(s.high_pass_filter(120)),
        "AM Radio": lambda s: (s.low_pass_filter(3000).high_pass_filter(400)) + 3,
        "Podcast Studio": lambda s: pydub_fx.compress_dynamic_range(pydub_fx.normalize(s), threshold=-20, ratio=2.5),
    }
    fn = tbl.get(preset)
    return fn(seg) if fn else seg

def apply_reverb(seg: AudioSegment, lvl: float) -> AudioSegment:
    if not PYDUB_OK or lvl <= 0:
        return seg
    try:
        delay = int(85 * lvl)
        wet = seg - int(13 * lvl)
        return pydub_fx.normalize(seg.overlay(wet, position=delay))
    except Exception:
        return seg

def mix_fon_voice(fon: AudioSegment, voice: AudioSegment,
                  fon_vol: int = -8, duck_db: int = -16,
                  fade_in: int = 800, fade_out: int = 1200) -> AudioSegment:
    if not PYDUB_OK:
        return voice
    try:
        fon = fon + fon_vol
        vl = len(voice)
        fl = len(fon)
        if fl < vl + 2000:
            loops = (vl + 2000) // fl + 1
            fon = fon * loops
        fon = fon[:vl + 2000].fade_in(fade_in)
        fp = fon[:vl]
        fr = fon[vl:]
        fm = min(500, vl // 4)
        ducked = (
            fp[:fm].fade(to_gain=duck_db, start=0, duration=fm) +
            (fp[fm:vl - fm] + duck_db) +
            fp[vl - fm:].fade(from_gain=duck_db, start=0, duration=fm)
        )
        return normalize_seg(ducked.overlay(voice) + fr.fade_out(fade_out))
    except Exception:
        return voice

def generate_jingle(freq: int = 440, dur_ms: int = 2000, style: str = "sine") -> Optional[AudioSegment]:
    if not PYDUB_OK or not NP_OK:
        return None
    try:
        gmap = {"sine": Sine, "square": Square, "sawtooth": Sawtooth}
        g = gmap.get(style, Sine)
        seg = (g(freq).to_audio_segment(duration=dur_ms // 3) +
               g(int(freq * 1.25)).to_audio_segment(duration=dur_ms // 3) +
               g(int(freq * 1.5)).to_audio_segment(duration=dur_ms // 3))
        return seg.fade_in(80).fade_out(180) - 10
    except Exception:
        return None

# ─── GROQ ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def init_groq():
    key = os.getenv("GROQ_API_KEY")
    if not key or not GROQ_OK:
        return None
    try:
        return Groq(api_key=key)
    except Exception:
        return None

groq_client = init_groq()

CHARS = {
    "🎙️ Dilay — Kadın Sunucu": {
        "id": "dilay", "voice": "tr-TR-EmelNeural", "pitch": 0,
        "prompt": "Sen radyo sunucusu Dilay'sın. 28-45 saniye anons yaz. SADECE düz Türkçe metin. XML/HTML/SSML/Markdown KULLANMA."
    },
    "📢 Kenan — Erkek Sunucu": {
        "id": "kenan", "voice": "tr-TR-AhmetNeural", "pitch": -2,
        "prompt": "Karizmatik erkek sunucu. 30-40 sn. SADECE düz Türkçe."
    },
    "📰 Haber Spikeri": {
        "id": "haber", "voice": "tr-TR-EmelNeural", "pitch": 1,
        "prompt": "Profesyonel haber spikeri. SADECE düz Türkçe."
    },
    "🎭 Reklam Sesi": {
        "id": "reklam", "voice": "tr-TR-AhmetNeural", "pitch": 2,
        "prompt": "Akılda kalıcı 15-30 sn radyo reklamı. SADECE düz Türkçe."
    },
    "🌙 Gece DJsi": {
        "id": "gece", "voice": "tr-TR-EmelNeural", "pitch": -1,
        "prompt": "Gece yayını şiirsel DJ. 40-50 sn. SADECE düz Türkçe."
    },
    "🌅 Sabah Sunucusu": {
        "id": "sabah", "voice": "tr-TR-AhmetNeural", "pitch": 3,
        "prompt": "Enerjik sabah sunucusu. 25-35 sn. SADECE düz Türkçe."
    },
}

GROQ_MODELS = {
    "Hızlı (llama3-8b)": "llama3-8b-8192",
    "Standart (llama3-70b)": "llama-3.3-70b-versatile",
    "Gelişmiş (mixtral-8x7b)": "mixtral-8x7b-32768",
}

def groq_gen(msg: str, char_id: str = "dilay", model_key: str = "Standart (llama3-70b)",
             temp: float = 0.87, max_tok: int = 450) -> Tuple[bool, str]:
    if not groq_client:
        return False, "⚠️ Groq bağlantısı yok. GROQ_API_KEY ayarlayın."
    char = next((c for c in CHARS.values() if c["id"] == char_id), list(CHARS.values())[0])
    model = GROQ_MODELS.get(model_key, "llama-3.3-70b-versatile")
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": char["prompt"]},
                      {"role": "user", "content": msg}],
            model=model, temperature=temp, max_tokens=max_tok,
        )
        return True, clean_text(res.choices[0].message.content.strip())
    except Exception as e:
        return False, f"⚠️ Groq: {e}"

def groq_mood(song: str) -> dict:
    pr = (f'Şarkı: "{song}"\nSadece JSON döndür:\n'
          '{"mood":"mutlu|melankolik|enerjik|romantik|nostaljik|hüzünlü",'
          '"tempo":"yavaş|orta|hızlı",'
          '"tone_suggestion":"Duygusal|Neşeli|Espirili|Derin|Nostaljik|Enerjik",'
          '"yorum":"tek cümle"}')
    ok, r = groq_gen(pr, char_id="dilay", temp=0.2, max_tok=160)
    if not ok:
        return {"mood": "?", "tempo": "orta", "tone_suggestion": "Duygusal", "yorum": ""}
    try:
        c = re.sub(r'```[^`]*```', '', r).strip()
        return json.loads(c)
    except Exception:
        return {"mood": "?", "tempo": "orta", "tone_suggestion": "Duygusal", "yorum": ""}

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:12px 0 8px">'
        '<div style="font-size:26px;font-weight:800;color:#2563eb;letter-spacing:-1px">K3N4N</div>'
        '<div style="font-size:11px;color:#64748b;font-weight:600;letter-spacing:3px">HYBRID v28.0</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.divider()

    MENU = [
        "📡 Gösterge Paneli",
        "🎛️ Fon+Anons Mikseri",
        "🎭 Karakter Stüdyosu",
        "🎮 Canlı Reji",
        "📩 İstek & Mesajlar",
        "✍️ Manuel Stüdyo",
        "📦 Toplu TTS",
        "🎬 Intro/Outro",
        "✂️ Ses Editörü",
        "🔄 A/B Test",
        "🔊 Ses Araçları",
        "📡 Stream Yayın",
        "🗣️ Piper TTS",
        "📁 Kaynak Ses",
        "📅 Program Planlayıcı",
        "📊 Analitikler",
        "📁 Kütüphane",
        "📻 Arşiv",
        "⚙️ Ayarlar",
    ]
    menu = st.radio("Menü:", MENU, label_visibility="collapsed")
    st.divider()

    # TTS Motoru
    tts_options = ["EdgeTTS", "Piper (ONNX/TR)"]
    if GOOGLE_TTS_OK:
        tts_options.append("Google TTS")
    tts_engine_sb = st.selectbox("TTS Motoru:", tts_options, label_visibility="collapsed", key="sb_tts")
    
    google_voice_sb = "tr-TR-Standard-A"
    google_speed_sb = 1.0
    if tts_engine_sb == "Google TTS" and GOOGLE_TTS_OK:
        google_voice_sb = GOOGLE_VOICES[st.selectbox("Google Ses:", list(GOOGLE_VOICES.keys()),
                                                     label_visibility="collapsed", key="sb_google")]["voice"]
        google_speed_sb = st.slider("Hız:", 0.5, 2.0, 1.0, 0.1, key="sb_gspeed")
    
    piper_model_sb = list(PIPER_MODELS_TR.keys())[0]
    if tts_engine_sb == "Piper (ONNX/TR)":
        piper_model_sb = st.selectbox("Piper Model:", list(PIPER_MODELS_TR.keys()),
                                      label_visibility="collapsed", key="sb_piper")
        mp, cp = piper_model_path(piper_model_sb)
        if mp:
            st.markdown(chip_html("✓ PIPER HAZIR", "green"), unsafe_allow_html=True)
        else:
            st.markdown(chip_html("İndirilmedi", "amber"), unsafe_allow_html=True)
            if st.button("⬇️ İndir", key="piper_dl_sb"):
                with st.spinner("İndiriliyor..."):
                    ok, msg = piper_download(piper_model_sb)
                if ok:
                    st.success("✅ İndirildi!")
                    st.rerun()
                else:
                    st.error(msg[:80])

    # Karakter
    char_name = st.selectbox("Karakter:", list(CHARS.keys()), label_visibility="collapsed", key="sb_char")
    AC = CHARS[char_name]

    # RVC
    all_models = scan_rvc_models()
    if all_models and RVC_OK:
        sel_label = st.selectbox("RVC Model:", [m["label"] for m in all_models],
                                 label_visibility="collapsed", key="sb_mdl")
        sel_model = next(m for m in all_models if m["label"] == sel_label)
        A_PTH = sel_model["pth"]
        A_INDEX = sel_model["index"]
        st.markdown(chip_html("PTH ✓", "green") + " " +
                    chip_html("IDX ✓" if A_INDEX else "IDX ✗", "green" if A_INDEX else "amber"),
                    unsafe_allow_html=True)
    else:
        A_PTH = ""
        A_INDEX = None
        st.markdown(chip_html("RVC: Model yok", "gray"), unsafe_allow_html=True)

    pitch_sb = st.slider("Pitch", -14, 14, AC["pitch"])
    speed_sb = st.slider("Hız (%)", 75, 130, 100)
    
    eq_sb = st.selectbox("EQ:", ["Broadcast Clear", "Radio Warm", "Vintage", "Deep Bass",
                                  "Crisp HiFi", "AM Radio", "Podcast Studio", "Ham (Efektsiz)"],
                          label_visibility="collapsed")
    reverb_sb = st.slider("Reverb", 0.0, 1.0, 0.0, 0.05)
    norm_sb = st.slider("Normalize", -24, -8, -16)
    
    groq_mkey = st.selectbox("Groq Modeli:", list(GROQ_MODELS.keys()), label_visibility="collapsed", index=1)

A_VOICE = AC["voice"]
A_PITCH = pitch_sb
A_SPEED = speed_sb
A_CHAR = AC["id"]

def vbtn(text: str, key: str, label: str = "🔊 Seslendir", song: str = "") -> Optional[str]:
    if st.button(label, key=f"vb_{key}"):
        if not text or not text.strip():
            st.warning("Metin boş!")
            return None
        fname = f"{sfn(key)}_{ts()}.wav"
        with st.spinner("🎙️ Ses üretiliyor..."):
            ok, path = asyncio.run(build_voice(
                text, A_VOICE, A_SPEED, A_PITCH, A_PTH, A_INDEX, fname,
                eq=eq_sb, reverb=reverb_sb, norm_db=float(norm_sb),
                tts_engine=tts_engine_sb, piper_model=piper_model_sb,
                google_voice=google_voice_sb, google_speed=google_speed_sb,
            ))
        if ok and os.path.exists(path):
            dur = audio_dur(path)
            qs = quality_score(path)
            st.success("✅ Ses hazır!")
            st.markdown(
                chip_html(f"⏱ {fmt_dur(dur)}", "blue") + " " +
                chip_html(f"🎯 {qs}/100", "purple") + " " +
                chip_html(tts_engine_sb, "teal"),
                unsafe_allow_html=True
            )
            st.audio(path)
            qbar(qs)
            draw_waveform(path)
            save_history(fname, text, A_CHAR, song)
            return path
        else:
            st.error("❌ Ses üretilemedi.")
            return None
    return None

# ═══════════════════════════════════════════════════════════════
# MENÜLER (KISA VERSİYONLAR)
# ═══════════════════════════════════════════════════════════════

if menu == "📡 Gösterge Paneli":
    st.markdown("## 📡 Gösterge Paneli")
    songs = list_audio(PLAYLIST_DIR)
    outputs = list_audio(OUT_DIR)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Şarkı", len(songs))
    c2.metric("Üretilen Ses", len(outputs))
    c3.metric("TTS Motoru", tts_engine_sb)
    c4.metric("RVC", "✅" if A_PTH else "❌")
    
    st.divider()
    st.markdown("### ⚡ Hızlı Anons")
    qa = st.text_input("Şarkı adı:")
    if st.button("✨ AI Anons Üret"):
        if qa.strip():
            md = groq_mood(qa)
            pr = f"Şarkı: {qa}\nMood: {md.get('mood','')}\n~60 kelime anons. Sadece düz metin."
            ok, txt = groq_gen(pr, char_id=A_CHAR, model_key=groq_mkey, max_tok=150)
            if ok:
                st.session_state["qa_txt"] = txt
                st.rerun()
    if st.session_state.get("qa_txt"):
        ed = st.text_area("Anons:", value=st.session_state["qa_txt"], height=110)
        st.session_state["qa_txt"] = ed
        vbtn(ed, "qa_v")

# ─── FON+ANONS MİKSERİ ──────────────────────────────────────────────────────
elif menu == "🎛️ Fon+Anons Mikseri":
    st.markdown("## 🎛️ Fon+Anons Mikseri")
    fon_files = list_audio(FON_DIR)
    
    c1, c2 = st.columns(2)
    with c1:
        fa_song = st.text_input("Şarkı/Konu:")
        if st.button("✨ AI Anons Üret"):
            if fa_song.strip():
                md = groq_mood(fa_song)
                pr = f"Şarkı: {fa_song}\nMood: {md.get('mood','')}\nProfesyonel anons. SADECE düz Türkçe."
                ok, txt = groq_gen(pr, char_id=A_CHAR, model_key=groq_mkey)
                if ok:
                    st.session_state["fa_txt"] = txt
                    st.rerun()
    with c2:
        fa_txt = st.text_area("Anons:", value=st.session_state.get("fa_txt",""), height=130)
        if fa_txt != st.session_state.get("fa_txt",""):
            st.session_state["fa_txt"] = fa_txt
    
    if fon_files:
        sel_fon = st.selectbox("Fon:", fon_files)
        fon_vol = st.slider("Fon Seviyesi:", -24, 0, -8)
        
        if st.button("🎛️ MİKSLE & OLUŞTUR"):
            if fa_txt.strip() and PYDUB_OK:
                with st.spinner("🎙️ Ses üretiliyor..."):
                    ok, vp = asyncio.run(build_voice(
                        fa_txt, A_VOICE, A_SPEED, A_PITCH, A_PTH, A_INDEX,
                        f"fon_anons_{ts()}.wav", eq=eq_sb, reverb=reverb_sb,
                        norm_db=float(norm_sb), tts_engine=tts_engine_sb,
                        piper_model=piper_model_sb, google_voice=google_voice_sb,
                        google_speed=google_speed_sb,
                    ))
                if ok:
                    fonseg = AudioSegment.from_file(os.path.join(FON_DIR, sel_fon))
                    vseg = AudioSegment.from_file(vp)
                    mixed = mix_fon_voice(fonseg, vseg, fon_vol=fon_vol)
                    out_p = os.path.join(OUT_DIR, f"mixed_{ts()}.wav")
                    mixed.export(out_p, "wav")
                    st.success("✅ Hazır!")
                    st.audio(out_p)
                    draw_waveform(out_p)

# ─── KARAKTER STÜDYOSU ──────────────────────────────────────────────────────
elif menu == "🎭 Karakter Stüdyosu":
    st.markdown("## 🎭 Karakter Stüdyosu")
    song_in = st.text_input("Şarkı / Konu:")
    if st.button("🎭 Tüm Karakterleri Üret"):
        if song_in.strip():
            mood = groq_mood(song_in)
            for cn, cd in CHARS.items():
                pr = f"Şarkı: {song_in}\nMood: {mood.get('mood','')}\nKarakterine uygun anons. SADECE düz Türkçe."
                ok, txt = groq_gen(pr, char_id=cd["id"], model_key=groq_mkey)
                if ok:
                    st.session_state[f"cs_{cd['id']}"] = txt
            st.rerun()
    
    for cn, cd in CHARS.items():
        with st.expander(cn):
            cur = st.session_state.get(f"cs_{cd['id']}", "")
            txt = st.text_area("Metin:", value=cur, height=100, key=f"cs_ta_{cd['id']}")
            if txt != cur:
                st.session_state[f"cs_{cd['id']}"] = txt
            if txt.strip():
                if st.button(f"🔊 Seslendir", key=f"cs_vb_{cd['id']}"):
                    ok, p = asyncio.run(build_voice(
                        txt, cd["voice"], A_SPEED, cd["pitch"],
                        A_PTH, A_INDEX, f"CHAR_{cd['id']}_{ts()}.wav",
                        tts_engine=tts_engine_sb, piper_model=piper_model_sb,
                        google_voice=google_voice_sb, google_speed=google_speed_sb,
                    ))
                    if ok:
                        st.audio(p)

# ─── CANLI REJİ ──────────────────────────────────────────────────────────────
elif menu == "🎮 Canlı Reji":
    st.markdown("## 🎮 Canlı Reji")
    st.markdown(f'<div class="live-badge"><span class="live-dot"></span>CANLI YAYIN · {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    
    TPLS = {
        "☀️ Sabah": f"Günaydın! Saat {datetime.now().strftime('%H:%M')}...",
        "🌙 Gece": "Gecenin bu sessiz saatinde sizinle olmak büyük mutluluk...",
        "🎵 Geçiş": "Ve şimdi sizi muhteşem bir melodiyle baş başa bırakıyoruz...",
    }
    cols = st.columns(len(TPLS))
    for i, (lbl, txt) in enumerate(TPLS.items()):
        with cols[i]:
            if st.button(lbl, key=f"lv_t_{i}"):
                st.session_state["live_txt"] = txt
    
    lv = st.text_area("Canlı Metin:", value=st.session_state.get("live_txt",""), height=130)
    if lv != st.session_state.get("live_txt",""):
        st.session_state["live_txt"] = lv
    
    if st.button("🔴 ANİNDA SESLENDİR", type="primary"):
        vbtn(lv, "live_main")

# ─── TOPLU TTS ──────────────────────────────────────────────────────────────
elif menu == "📦 Toplu TTS":
    st.markdown("## 📦 Toplu TTS")
    txt_input = st.text_area("Her satır ayrı ses:", height=200, 
                             placeholder="Günaydın!\nHava çok güzel.\nVe şimdi müzik...")
    prefix = st.text_input("Ön ek:", value="anons")
    
    if st.button("🚀 Hepsini Üret") and txt_input.strip():
        lines = [l.strip() for l in txt_input.split("\n") if l.strip()]
        prog = st.progress(0)
        results = []
        for i, line in enumerate(lines):
            fname = f"{prefix}_{i+1:03d}_{ts()}.wav"
            ok, path = asyncio.run(build_voice(
                line, A_VOICE, A_SPEED, A_PITCH, A_PTH, A_INDEX, fname,
                tts_engine=tts_engine_sb, piper_model=piper_model_sb,
                google_voice=google_voice_sb, google_speed=google_speed_sb,
            ))
            if ok:
                results.append(path)
            prog.progress((i+1)/len(lines))
        st.success(f"✅ {len(results)}/{len(lines)} ses üretildi!")
        for r in results[:3]:
            st.audio(r)

# ─── AYARLAR ──────────────────────────────────────────────────────────────────
elif menu == "⚙️ Ayarlar":
    st.markdown("## ⚙️ Ayarlar")
    tab1, tab2 = st.tabs(["🔑 API Durumu", "📋 Aktif Ayarlar"])
    
    with tab1:
        st.json({
            "Groq": "✅" if groq_client else "❌",
            "EdgeTTS": "✅" if TTS_OK else "❌",
            "Google TTS": "✅" if GOOGLE_TTS_OK else "❌",
            "Piper ONNX": "✅" if ONNX_OK else "❌",
            "RVC": "✅" if RVC_OK else "❌",
            "PyDub": "✅" if PYDUB_OK else "❌",
        })
    
    with tab2:
        st.json({
            "Karakter": A_CHAR,
            "TTS Motoru": tts_engine_sb,
            "Pitch": A_PITCH,
            "Hız": A_SPEED,
            "EQ": eq_sb,
            "Reverb": reverb_sb,
        })

# ─── FOOTER ──────────────────────────────────────────────────────────────────
si = " · ".join([
    f"{'✓' if groq_client else '✗'} Groq",
    f"{'✓' if TTS_OK else '✗'} EdgeTTS",
    f"{'✓' if GOOGLE_TTS_OK else '✗'} Google TTS",
    f"{'✓' if RVC_OK else '✗'} RVC",
    f"{'✓' if PYDUB_OK else '✗'} PyDub",
])
st.markdown(
    f'<div class="footer">K3N4N HYBRID v28.0 · {datetime.now().year} · {si}</div>',
    unsafe_allow_html=True
)