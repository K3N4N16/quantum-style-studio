"""
╔══════════════════════════════════════════════════════════════════╗
║  İMAJ FM · TTS STÜDYO  v6.0                                      ║
║  v6 yenilikleri:                                                 ║
║  · 3 tema: Koyu · Açık · Yüksek Kontrast (+ yazı boyutu)         ║
║    WCAG kontrast ölçülmüş paletler, mobilde okunaklı             ║
║  · Radyo Otomasyon: otomatik akış (saat çarkı), arşivden klip,   ║
║    şarkı etiketleri/jingle, önizleme, zaman damgalı yayın listesi║
║  · Anons Yazarı: yapay zekâ ile anons metni varyasyonları        ║
║  · Günlük istek grafiği, önbellek yönetimi                       ║
║  v5'ten: disk kalıcılığı, Interactions API, MP3, montaj, tam     ║
║  yayın çıktısı, crossfade, fon müziği, akıllı API rotasyonu      ║
╚══════════════════════════════════════════════════════════════════╝
Gereksinimler: pip install streamlit numpy miniaudio lameenc "google-genai>=2.25.0"
Secrets (.streamlit/secrets.toml):
    GEMINI_API_KEY_1 = "AIza..."   (… _10'a kadar)
    APP_USER = "kenan"             APP_PASS = "imajfm"
"""

import streamlit as st
import wave, io, zipfile, re, time, datetime, hashlib, json, os, hmac, shutil, base64
import html as _html
import random
from pathlib import Path
import numpy as np
try:
    import miniaudio          # MP3/OGG okuma (pip install miniaudio)
except Exception:
    miniaudio = None
try:
    import lameenc            # MP3 yazma (pip install lameenc)
except Exception:
    lameenc = None

from google import genai
from google.genai import types

import inspect
def _ucw():
    # Yeni Streamlit: width="stretch"; eski sürümler: use_container_width=True
    try:
        if "width" in inspect.signature(st.button).parameters:
            return {"width": "stretch"}
    except Exception:
        pass
    return {"use_container_width": True}
UCW = _ucw()

st.set_page_config(page_title="İmaj FM · TTS Stüdyo v6", page_icon="🎙️",
                   layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────
# (CSS: inject_css() — aşağıda, tema destekli)


# ═════════════════════════════════════════════════════════════════
# SABİTLER
# ═════════════════════════════════════════════════════════════════
SR = 24000
MAX_ARCHIVE = 80

VOICES = {
    "Zephyr":("♀","Parlak · Neşeli"), "Puck":("♂","Enerjik · Hareketli"),
    "Charon":("♂","Bilgilendirici · Açık"), "Kore":("♀","Sıcak · Güven Veren"),
    "Fenrir":("♂","Heyecanlı · Dinamik"), "Aoede":("♀","Akıcı · Doğal"),
    "Leda":("♀","Genç · Enerjik"), "Orus":("♂","Kararlı · Güçlü"),
    "Achird":("♂","Dostane · Samimi"), "Algenib":("♂","Pürüzlü · Özgün"),
    "Algieba":("♂","Yumuşak · Hoş"), "Alnilam":("♂","Sağlam · Güçlü"),
    "Autonoe":("♀","Parlak · İyimser"), "Callirrhoe":("♀","Rahat · Akıcı"),
    "Despina":("♀","Pürüzsüz · Zarif"), "Enceladus":("♂","Yumuşak · Nefes"),
    "Erinome":("♀","Net · Hassas"), "Gacrux":("♂","Olgun · Deneyimli"),
    "Iapetus":("♂","Net · Anlaşılır"), "Laomedeia":("♀","Neşeli · Canlı"),
    "Pulcherrima":("♀","İfadeli · Çarpıcı"), "Rasalgethi":("♂","Profesyonel"),
    "Sadachbia":("♂","Canlı · Hareketli"), "Sadaltager":("♂","Bilgili · Otoriter"),
    "Schedar":("♂","Güçlü · Etkileyici"), "Sulafat":("♀","Sıcak · Davetkar"),
    "Umbriel":("♂","Derin · Gizemli"), "Vindemiatrix":("♀","Nazik · Kibar"),
    "Achernar":("♀","Yumuşak · Hassas"), "Zubenelgenubi":("♂","Rahat · Dengeli"),
}
MODELS = {
    "gemini-3.8-flash-tts":"💎 3.8 Flash  (En Kaliteli)",
    "gemini-3.8-flash-lite-tts":"⚡ 3.8 Flash-Lite  (Hızlı · Ekonomik)",
    "gemini-3.1-flash-tts-preview":"🎭 3.1 Flash Preview  (Köşeli etiketler)",
    "gemini-2.5-pro-preview-tts":"🧪 2.5 Pro Preview",
}
# Eski/geçersiz adlar → güncel Gemini API adı.
MODEL_ALIAS = {
    "gemini-2.5-flash-tts":"gemini-3.8-flash-lite-tts",
    "gemini-2.5-flash-preview-tts":"gemini-3.8-flash-lite-tts",
    "gemini-2.5-flash-lite-preview-tts":"gemini-3.8-flash-lite-tts",
    "gemini-2.5-pro-tts":"gemini-2.5-pro-preview-tts",
}
LANGUAGES = {
    "otomatik":"🌐 Oto","tr-TR":"🇹🇷 Türkçe","en-US":"🇺🇸 EN-US","en-GB":"🇬🇧 EN-UK",
    "de-DE":"🇩🇪 Almanca","fr-FR":"🇫🇷 Fransızca","es-ES":"🇪🇸 İspanyolca","it-IT":"🇮🇹 İtalyanca",
    "pt-BR":"🇧🇷 PT-BR","ru-RU":"🇷🇺 Rusça","ja-JP":"🇯🇵 Japonca","ko-KR":"🇰🇷 Korece",
    "zh-CN":"🇨🇳 Çince","ar-XA":"🇸🇦 Arapça","hi-IN":"🇮🇳 Hintçe","nl-NL":"🇳🇱 Felemenkçe",
    "pl-PL":"🇵🇱 Lehçe","sv-SE":"🇸🇪 İsveççe",
}
STYLE_PRESETS = {
    "— Seçin —":"",
    "📻 Haber Sunucusu":"Profesyonel haber sunucusu gibi net, otoriter ve güven verici bir tonla oku.",
    "🎉 Neşeli & Enerjik":"Çok neşeli ve coşkulu, müzik programı sunuyormuş gibi oku.",
    "🎭 Dramatik & Güçlü":"Dramatik ve etkileyici, büyük sahne duyurusu gibi oku.",
    "🌙 Sakin & Huzurlu":"Sakin, huzurlu ve rahatlatıcı, gece kuşağı tonu ile oku.",
    "🚨 Acil & Hızlı":"Acil haber tonu, hızlı ve yüksek enerjili sesle oku.",
    "☕ Sıcak & Samimi":"Sıcak ve dostça, yakın arkadaşa anlatır gibi oku.",
    "📣 Reklam Sesi":"Profesyonel reklam seslendirmesi, çekici ve ikna edici oku.",
    "📖 Hikaye Anlatıcısı":"Büyüleyici hikaye anlatıcısı gibi ritmik ve ifadeli oku.",
    "⚽ Spor Yorumcusu":"Heyecanlı spor yorumcusu gibi yüksek tempo ile oku.",
    "🎬 Belgesel Sesi":"Derin belgesel anlatıcısı, ağır ve anlamlı tonla oku.",
}
TEMPLATES = {
    "🎙️ Sabah Açılış":"[excitedly] Günaydın! İmaj FM ile sabahın en güzel sesine uyanıyorsunuz!\n[seriously] Bugün haber bültenimizle başlıyoruz... [normal] hoş geldiniz!\n[excitedly] BU SABAH müzik, haber ve çok daha fazlası burada!",
    "🌙 Gece Kapanış":"[whispers] Ve gece yarısına yaklaşırken... İmaj FM sizinle.\n[sighs] Uzun bir günün ardından... kulaklarınıza iyi geceler.\n[whispers] Yarın yeniden buradayız. Tatlı rüyalar.",
    "📢 Özel Duyuru":"[excitedly] DUYURU DUYURU!\n[seriously] Değerli dinleyicilerimiz, önemli bir bildirimiz var.\n[excitedly] BU HAFTA sonu unutulmaz bir etkinlik sizi bekliyor!\n[shouting] KAÇIRMAYIN!",
    "🎵 Müzik Geçişi":"[normal] Ve müziğimiz devam ediyor...\n[whispers] Şimdi sizin için harika bir seçim var.\n[excitedly] İşte o şarkı!",
    "📰 Haber Girişi":"[seriously] İmaj FM Ana Haber Bülteni.\n[pause 0.6]\n[normal] Günün öne çıkan haberleriyle karşınızdayız.\n[seriously] Şimdi tüm ayrıntılarıyla...",
    "🎉 Yarışma":"[excitedly] BÜYÜK YARIŞMA BAŞLIYOR!\n[laughs] Hazır mısınız?\n[shouting] BU HAFTA kazanan sizin aranızdan çıkacak!\n[seriously] Hemen arayın... [excitedly] KAZANMA ŞANSI SİZİN!",
    "☀️ Öğle Bülteni":"[normal] İmaj FM Öğle Bülteni ile karşınızdayız.\n[seriously] Bugünün öne çıkan gelişmeleri...\n[normal] Haberlerden sonra müziğe devam.",
    "🌟 Program Tanıtım":"[excitedly] BU AKŞAM İmaj FM'de çok özel bir program!\n[whispers] Fısıltıyla söyleyelim... sürpriz konuklar var.\n[pause 0.8]\n[excitedly] Saat tam 20:00'de... SADECE İMAJ FM'DE!",
    "🌡️ Hava Durumu":"[normal] İmaj FM hava durumu. İstanbul'da bugün hava parçalı bulutlu, sıcaklık 18 derece. Yağış ihtimali %30.",
}
ETAGS = [("🔥","Coşkulu","[excitedly] "),("🤫","Fısıltı","[whispers] "),("😄","Gülümseyen","[laughs] "),
         ("📰","Ciddi","[seriously] "),("📢","Bağırma","[shouting] "),("😮‍💨","Yorgun","[sighs] "),
         ("🎙️","Normal","[normal] "),("⏸️","Duraklama","[pause 1] ")]

TAG_RE = re.compile(r"\[(excitedly|whispers|laughs|seriously|shouting|sighs|normal)\]", re.I)
PAUSE_RE = re.compile(r"\[(?:pause|bekle)\s*([0-9]+(?:[.,][0-9]+)?)\s*(?:s|sn)?\]", re.I)

CFG_DEF = {"theme":"dark","fsize":100,"norm":True,"trim":True,"comp":False,"fade_ms":40,"head":0.10,"tail":0.30,
           "nums":True,"use_dict":True,"chunk":True,"chunk_chars":800,"max_per_key":10,
           "usd_min":0.015,"custom_model":"","dict":"FM=Ef Em\nDJ=Di Ci\nTRT=Te Er Te"}

# ═════════════════════════════════════════════════════════════════
# DİSK KALICILIĞI
# ═════════════════════════════════════════════════════════════════
DATA = Path(os.environ.get("IMAJFM_DATA", "imajfm_data"))
AUDIO = DATA / "audio"
PREV = DATA / "previews"
SONGS = DATA / "songs"
BROAD = DATA / "broadcasts"
ANN = DATA / "ann_cache"
for _p in (AUDIO, PREV, SONGS, BROAD, ANN):
    _p.mkdir(parents=True, exist_ok=True)

def jload(name, default):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except Exception:
        return default

def jsave(name, obj):
    try:
        tmp = DATA / (name + ".tmp")
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(DATA / name)
    except Exception as e:
        st.session_state["_io_err"] = str(e)

def _init(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

def _load_pool():
    saved = jload("pool.json", {})
    today = datetime.date.today().isoformat()
    used = saved.get("used", []) if saved.get("date") == today else []
    labels = saved.get("labels", [])
    return [{"key": "",
             "used": int(used[i]) if i < len(used) else 0,
             "label": labels[i] if i < len(labels) else f"API {i+1}"} for i in range(10)]

def save_pool():
    p = st.session_state._pool
    jsave("pool.json", {"date": datetime.date.today().isoformat(),
                        "used": [s["used"] for s in p], "labels": [s["label"] for s in p]})

_init("cfg", {**CFG_DEF, **jload("settings.json", {})})
_init("_arc", jload("archive.json", []))
_init("_favs", jload("favorites.json", []))
_init("_stats", jload("stats.json", {"calls": 0, "chars": 0, "secs": 0.0}))
_init("_pool", _load_pool())
_init("_active", 0)
_init("_auth", False)
_init("_last", {})
_init("_secrets_loaded", False)
_init("txt_tek", "[excitedly] İmaj FM'e hoş geldiniz! BU GECE unutulmaz bir program var...\n[pause 0.7]\n[whispers] Sürprizler için kulaklarınız bizde olsun.\n[seriously] Şimdi haberlere geçiyoruz.")
_init("txt_cift", "Sunucu: [excitedly] İmaj FM'e hoş geldiniz!\nMisafir: [laughs] Teşekkürler, burada olmak harika!\nSunucu: [seriously] Haberler... [normal] Müziğe dönüyoruz.")
_init("txt_bulk", "İmaj FM sabah yayını başlıyor.\nHaber bülteni için bekleyiniz.\nKore | Müzik programımıza hoş geldiniz.\nİyi dinlemeler dileriz.")
_init("txt_a", "[excitedly] İmaj FM'e hoş geldiniz!")
_init("txt_b", "[seriously] İmaj FM'e hoş geldiniz.")

def cfg():
    return st.session_state.cfg

def mpk():
    return int(cfg()["max_per_key"])

def get_models():
    m = dict(MODELS)
    cm = cfg().get("custom_model", "").strip()
    if cm and cm not in m:
        m[cm] = f"🧪 {cm}"
    return m

# ─────────────────────────────────────────────────────────────────
# TEMA (koyu / açık) — tüm renkler CSS değişkenlerinden gelir
# ─────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────
# TEMA (koyu / açık) — tüm renkler CSS değişkenlerinden gelir
# ─────────────────────────────────────────────────────────────────
THEMES = {
 "dark": dict(bg="#0b1220", bg2="#0d1626", panel="#162033", panel2="#1b2840", border="#5b7099",
              text="#ffffff", text2="#e6edf7", muted="#c3d0e4", accent="#ff7b7b", link="#9ccbff",
              inp="#0f1a2d", h1a="#ffffff", btn="#c62828", btnfg="#ffffff",
              hdr="linear-gradient(135deg,#17315e 0%,#0f1b30 60%,#0b1220 100%)",
              gbg="#06381b", gfg="#a7f3c0", abg="#3a2800", afg="#ffe08a",
              rbg="#3d0f0f", rfg="#ffc2c2", pbg="#2a1750", pfg="#e6dcff", bbg="#10294d", scheme="dark"),
 "light": dict(bg="#f4f6fb", bg2="#e6ebf5", panel="#ffffff", panel2="#eef2f9", border="#7f8fab",
               text="#0b1220", text2="#1e293b", muted="#334155", accent="#b91c1c", link="#1d4ed8",
               inp="#ffffff", h1a="#0b1220", btn="#c62828", btnfg="#ffffff",
               hdr="linear-gradient(135deg,#ffffff 0%,#e8eefb 70%,#e1e8f5 100%)",
               gbg="#dff5e7", gfg="#0f4d27", abg="#fff0cf", afg="#6b3500",
               rbg="#fde2e2", rfg="#7a1313", pbg="#ece4fd", pfg="#3f1a8a", bbg="#e3edff", scheme="light"),
 "hc": dict(bg="#000000", bg2="#0a0a0a", panel="#121212", panel2="#1c1c1c", border="#ffffff",
            text="#ffffff", text2="#ffffff", muted="#f0f0f0", accent="#ffd60a", link="#5fd0ff",
            inp="#000000", h1a="#ffffff", btn="#ffd60a", btnfg="#000000",
            hdr="linear-gradient(135deg,#1a1a1a 0%,#0a0a0a 100%)",
            gbg="#002b10", gfg="#8dffb0", abg="#2b2000", afg="#ffe45c",
            rbg="#330000", rfg="#ffb3b3", pbg="#20103f", pfg="#ddd0ff", bbg="#001a33", scheme="dark"),
}
LOOKS = {"dark": "🌙 Koyu", "light": "☀️ Açık", "hc": "🔆 Yüksek Kontrast"}
SIZES = {100: "Yazı: Normal", 112: "Yazı: Büyük", 125: "Yazı: Çok büyük"}
TOML_THEME = {
 "dark":  {"base": "dark",  "primaryColor": "#ff7b7b", "backgroundColor": "#0b1220", "secondaryBackgroundColor": "#162033", "textColor": "#ffffff"},
 "light": {"base": "light", "primaryColor": "#b91c1c", "backgroundColor": "#f4f6fb", "secondaryBackgroundColor": "#ffffff", "textColor": "#0b1220"},
 "hc":    {"base": "dark",  "primaryColor": "#ffd60a", "backgroundColor": "#000000", "secondaryBackgroundColor": "#121212", "textColor": "#ffffff"},
}

def write_streamlit_theme(theme):
    # Streamlit'in yerel öğeleri (üst menü, açılır pencereler) bu dosyadaki temayı kullanır.
    try:
        p = Path(".streamlit") / "config.toml"
        p.parent.mkdir(exist_ok=True)
        old = p.read_text(encoding="utf-8") if p.exists() else ""
        out, skip = [], False
        for ln in old.splitlines():
            if ln.strip().startswith("["):
                skip = ln.strip() == "[theme]"
            if not skip:
                out.append(ln)
        out += ["", "[theme]"] + [f'{k} = "{v}"' for k, v in TOML_THEME.get(theme, TOML_THEME["dark"]).items()]
        p.write_text("\n".join(out).strip() + "\n", encoding="utf-8")
    except Exception:
        pass

STATIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');
*,*::before,*::after{box-sizing:border-box;}
html,body,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"],.main{background:var(--bg)!important;color:var(--text);font-family:'Inter',sans-serif;}
[data-testid="stHeader"]{background:var(--bg)!important;}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebarContent"]{padding:.65rem .75rem;}
h1,h2,h3,h4,h5,h6{color:var(--text)!important;}
[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li,[data-testid="stMarkdownContainer"] td,[data-testid="stMarkdownContainer"] th,[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label,label,[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p,[data-testid="stRadio"] label p,[data-testid="stCheckbox"] label p,[data-testid="stToggle"] label p,[data-testid="stSlider"] label p,[data-testid="stTickBarMin"],[data-testid="stTickBarMax"],[data-testid="stFileUploader"] label p{color:var(--text)!important;}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--text2)!important;}
.stApp :is(p,li,label,small):not([style*="color"]){color:var(--text)!important;opacity:1!important;}
[data-testid="stWidgetLabel"] *,[data-testid="stWidgetLabel"]{color:var(--text)!important;opacity:1!important;font-weight:600;}
[data-testid="stCaptionContainer"] *,[data-testid="stCaptionContainer"]{color:var(--text2)!important;opacity:1!important;}
[data-testid="stSidebar"] :is(p,li,label,small){color:var(--text)!important;opacity:1!important;}
[data-baseweb="radio"]>div:first-child,[data-baseweb="checkbox"]>span:first-child{border-color:var(--text2)!important;}
[data-testid="stMarkdownContainer"] code{background:var(--panel2)!important;color:var(--link)!important;border:1px solid var(--border);border-radius:4px;padding:0 4px;}
[data-testid="stMarkdownContainer"] a{color:var(--link)!important;}
.hdr{background:var(--hdr);border:1px solid var(--border);border-radius:16px;padding:22px 28px;margin-bottom:18px;position:relative;overflow:hidden;}
.hdr::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#e02020,#f07800,#e02020);background-size:200%;animation:scan 3s linear infinite;}
@keyframes scan{0%{background-position:0%}100%{background-position:200%}}
.hdr h1{font-family:'Syne',sans-serif;font-size:1.75rem;font-weight:800;margin:0 0 4px;background:linear-gradient(90deg,var(--h1a) 25%,#e02020 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hdr p{margin:0;color:var(--text2);font-size:.84rem;letter-spacing:.03em;}
.ldot{display:inline-block;width:7px;height:7px;background:#ff3a3a;border-radius:50%;margin-right:7px;animation:blink 1.2s ease-in-out infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.12}}
.sl{font-family:'Syne',sans-serif;font-size:.7rem;font-weight:800;letter-spacing:.14em;color:var(--accent);text-transform:uppercase;margin:16px 0 6px;display:block;}
.sl2{font-family:'Syne',sans-serif;font-size:.64rem;font-weight:800;letter-spacing:.12em;color:var(--link);text-transform:uppercase;margin:10px 0 4px;display:block;}
.mbox{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:12px;text-align:center;}
.mbox .v{font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:var(--accent);}
.mbox .l{font-size:.64rem;letter-spacing:.1em;color:var(--text2);text-transform:uppercase;margin-top:2px;font-weight:600;}
.mbox.g .v{color:#16a34a;}.mbox.b .v{color:#2563eb;}.mbox.a .v{color:#d97706;}.mbox.p .v{color:#7c3aed;}
.card{background:var(--panel);border:1px solid var(--border);border-radius:9px;padding:11px 14px;margin:7px 0;font-size:.88rem;color:var(--text);line-height:1.5;}
.card.b{border-left:4px solid #3a7bd5;background:var(--bbg);}
.card.g{border-left:4px solid #22c55e;background:var(--gbg);color:var(--gfg);}
.card.a{border-left:4px solid #f59e0b;background:var(--abg);color:var(--afg);}
.card.r{border-left:4px solid #ef4444;background:var(--rbg);color:var(--rfg);}
.card.p{border-left:4px solid #a78bfa;background:var(--pbg);color:var(--pfg);}
.card code{color:inherit;font-weight:700;}
[data-testid="stButton"]>button,[data-testid="stDownloadButton"]>button,[data-testid="stBaseButton-secondary"]{font-family:'Syne',sans-serif;font-weight:700;letter-spacing:.03em;border-radius:9px;transition:all .2s;background:var(--panel)!important;border:1px solid var(--border)!important;color:var(--text)!important;}
[data-testid="stButton"]>button p,[data-testid="stDownloadButton"]>button p{color:var(--text)!important;}
[data-testid="stButton"]>button:hover,[data-testid="stDownloadButton"]>button:hover{border-color:var(--link)!important;color:var(--link)!important;}
[data-testid="stButton"]>button[kind="primary"],[data-testid^="stBaseButton-primary"]{background:var(--btn)!important;border:none!important;color:var(--btnfg)!important;}
html body .stApp [data-testid^="stBaseButton-primary"] *,html body .stApp button[kind="primary"] *{color:var(--btnfg)!important;}
[data-testid="stButton"]>button[kind="primary"]:hover{filter:brightness(1.12);transform:translateY(-1px);}
button:disabled{opacity:.5!important;}
input,textarea,[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="textarea"]{background:var(--inp)!important;color:var(--text)!important;-webkit-text-fill-color:var(--text)!important;caret-color:var(--accent)!important;}
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div{border:1px solid var(--border)!important;border-radius:9px!important;}
[data-testid="stTextArea"] textarea{font-size:.95rem!important;line-height:1.65!important;border-radius:10px!important;}
textarea:focus,input:focus{border-color:var(--accent)!important;}
::placeholder{color:var(--muted)!important;opacity:1!important;-webkit-text-fill-color:var(--muted)!important;}
[data-baseweb="select"]>div{background:var(--inp)!important;}
[data-baseweb="select"] *{color:var(--text)!important;}
[data-baseweb="select"] svg{fill:var(--text2)!important;}
[data-baseweb="popover"],[data-baseweb="popover"]>div,[data-baseweb="menu"],ul[role="listbox"]{background:var(--panel)!important;border:1px solid var(--border);}
[data-baseweb="popover"] li,[role="option"],[data-baseweb="menu"] li{background:var(--panel)!important;color:var(--text)!important;}
[role="option"]:hover,[data-baseweb="menu"] li:hover,li[aria-selected="true"]{background:var(--panel2)!important;color:var(--link)!important;}
[data-testid="stNumberInput"] button{background:var(--panel2)!important;color:var(--text)!important;border-color:var(--border)!important;}
[data-testid="stAudio"]{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:8px;}
[data-testid="stExpander"] details,[data-testid="stSidebar"] details{background:var(--panel)!important;border:1px solid var(--border)!important;border-radius:9px!important;margin-bottom:5px!important;}
details summary p{font-family:'Syne',sans-serif!important;font-size:.82rem!important;font-weight:700!important;color:var(--text)!important;}
details summary{color:var(--text)!important;}
[data-testid="stIconMaterial"],[data-testid="stExpanderToggleIcon"],span[class*="material"]{font-family:'Material Symbols Rounded','Material Symbols Outlined','Material Icons'!important;font-weight:400!important;font-style:normal!important;letter-spacing:normal!important;text-transform:none!important;white-space:nowrap!important;font-feature-settings:'liga'!important;-webkit-font-feature-settings:'liga'!important;line-height:1!important;font-size:1.35rem!important;color:var(--text2)!important;}
details summary{padding:9px 12px!important;}
details summary:hover,details summary:hover p,details[open]>summary,details[open]>summary p{color:var(--accent)!important;}
details summary svg{fill:var(--text2)!important;color:var(--text2)!important;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid var(--border);gap:0;overflow-x:auto;}
[data-testid="stTabs"] [data-baseweb="tab"]{background:transparent!important;color:var(--text2)!important;font-family:'Syne',sans-serif!important;font-weight:700!important;font-size:.8rem!important;letter-spacing:.04em!important;padding:10px 14px!important;border-bottom:2px solid transparent!important;white-space:nowrap;}
[data-testid="stTabs"] [data-baseweb="tab"] p{color:inherit!important;}
[data-testid="stTabs"] [aria-selected="true"]{color:var(--accent)!important;border-bottom:3px solid var(--accent)!important;}
[data-testid="stFileUploaderDropzone"]{background:var(--panel2)!important;border:1px dashed var(--border)!important;}
[data-testid="stFileUploaderDropzone"] *{color:var(--text2)!important;}
[data-testid="stFileUploaderDropzone"] button{color:var(--text)!important;background:var(--panel)!important;border:1px solid var(--border)!important;}
[data-testid="stAlert"]{background:var(--panel2)!important;border:1px solid var(--border)!important;}
[data-testid="stAlert"] *{color:var(--text)!important;}
[data-testid="stCode"] pre,pre{background:var(--panel2)!important;border:1px solid var(--border);}
pre code,pre code span{color:var(--text)!important;}
[data-testid="stProgress"] *{color:var(--text2)!important;}
.qbar{background:var(--border);border-radius:4px;height:5px;margin:3px 0;overflow:hidden;}
.qbar-f{height:100%;border-radius:4px;transition:width .4s;}
.arc-card{background:var(--panel);border:1px solid var(--border);border-radius:9px;padding:11px 13px;margin-bottom:6px;}
.arc-card:hover{border-color:var(--link);}
.arc-meta{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;}
.arc-voice{font-family:'Syne',sans-serif;font-size:.82rem;font-weight:800;color:var(--link);}
.arc-ts{font-size:.7rem;color:var(--muted);font-family:'JetBrains Mono',monospace;}
.arc-info{font-size:.72rem;color:var(--text2);margin-bottom:5px;}
.arc-text{font-size:.82rem;color:var(--text);line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.fav-card{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:9px 12px;margin:5px 0;}
.fav-name{font-family:'Syne',sans-serif;font-size:.8rem;font-weight:800;color:var(--text);}
.fav-prev{font-size:.74rem;color:var(--text2);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.ttbl{width:100%;border-collapse:collapse;font-size:.74rem;}
.ttbl th{color:var(--accent);font-family:'Syne',sans-serif;font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;padding:4px 3px;border-bottom:1px solid var(--border);text-align:left;}
.ttbl td{padding:4px 3px;color:var(--text);border-bottom:1px solid var(--border);vertical-align:top;}
.tc{color:var(--link);font-family:'JetBrains Mono',monospace;font-size:.76rem;font-weight:600;}
.wf-wrap{background:var(--panel2);border:1px solid var(--border);border-radius:8px;padding:4px 6px;margin:6px 0;}
.tiny{font-size:.76rem;color:var(--text2);margin:3px 0 8px;}
[data-testid="stExpander"] details{box-shadow:none;}
hr{border-color:var(--border)!important;margin:11px 0!important;}
::-webkit-scrollbar{width:5px;height:5px;}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
@media (max-width:768px){
.hdr{padding:16px 16px;}.hdr h1{font-size:1.25rem;}.hdr p{font-size:.78rem;}
.sl{font-size:.78rem;}.sl2{font-size:.72rem;}.tiny{font-size:.82rem;}.card{font-size:.92rem;}
.mbox .v{font-size:1.1rem;}.mbox .l{font-size:.68rem;}
[data-testid="stTabs"] [data-baseweb="tab"]{font-size:.86rem!important;padding:10px 12px!important;}
details summary p{font-size:.9rem!important;}
[data-testid="stMarkdownContainer"] p,label{font-size:1rem;}
}
"""

def inject_css():
    c = cfg()
    th = c.get("theme", "dark")
    t = THEMES.get(th, THEMES["dark"])
    fs = int(c.get("fsize", 100))
    root = ":root{" + ";".join(f"--{k}:{v}" for k, v in t.items() if k != "scheme") + f";color-scheme:{t['scheme']}" + "}"
    root += f"html{{font-size:{fs}%;}}@media (max-width:768px){{html{{font-size:{fs + 6}%;}}}}"
    if th == "hc":
        root += ".card,.mbox,.arc-card,.fav-card,[data-testid=\"stExpander\"] details{border-width:2px!important;}"
    st.markdown("<style>" + root + STATIC_CSS + "</style>", unsafe_allow_html=True)

def _look_cb(src):
    ss = st.session_state
    th, fs = ss[f"look_theme{src}"], int(ss[f"look_size{src}"])
    cfg()["theme"], cfg()["fsize"] = th, fs
    for k in ("", "_sb"):
        ss[f"look_theme{k}"], ss[f"look_size{k}"] = th, fs
    write_streamlit_theme(th)

def look_controls(sfx):
    th = cfg().get("theme", "dark")
    fs = int(cfg().get("fsize", 100))
    _init(f"look_theme{sfx}", th if th in LOOKS else "dark")
    _init(f"look_size{sfx}", fs if fs in SIZES else 100)
    c1, c2 = st.columns(2)
    c1.selectbox("Tema", list(LOOKS), format_func=LOOKS.get, key=f"look_theme{sfx}",
                 on_change=_look_cb, args=(sfx,), label_visibility="collapsed")
    c2.selectbox("Yazı boyutu", list(SIZES), format_func=SIZES.get, key=f"look_size{sfx}",
                 on_change=_look_cb, args=(sfx,), label_visibility="collapsed")

inject_css()
if not st.session_state.get("_toml"):
    write_streamlit_theme(cfg().get("theme", "dark"))
    st.session_state["_toml"] = True

# ═════════════════════════════════════════════════════════════════
# API HAVUZU
# ═════════════════════════════════════════════════════════════════
def load_secrets_once():
    if st.session_state._secrets_loaded:
        return
    st.session_state._secrets_loaded = True
    for i in range(10):
        try:
            v = st.secrets.get(f"GEMINI_API_KEY_{i+1}", "")
            if not v and i == 0:
                v = st.secrets.get("GEMINI_API_KEY", "")
            if v and not st.session_state._pool[i]["key"]:
                st.session_state._pool[i]["key"] = v
                st.session_state[f"key_{i}"] = v
        except Exception:
            pass

load_secrets_once()

def get_active_key():
    pool, idx, m = st.session_state._pool, st.session_state._active, mpk()
    for _ in range(10):
        s = pool[idx]
        if s["key"].strip() and s["used"] < m:
            st.session_state._active = idx
            return s["key"].strip(), idx
        idx = (idx + 1) % 10
    return None, -1

def consume(idx, chars=0):
    p, s = st.session_state._pool, st.session_state._stats
    p[idx]["used"] += 1
    s["calls"] += 1
    s["chars"] += chars
    _d = datetime.date.today().isoformat()
    dl = s.setdefault("daily", {})
    dl[_d] = dl.get(_d, 0) + 1
    for _k in sorted(dl)[:-60]:
        dl.pop(_k, None)
    if p[idx]["used"] >= mpk():
        st.session_state._active = (idx + 1) % 10
    save_pool()
    jsave("stats.json", s)

def exhaust(idx):
    st.session_state._pool[idx]["used"] = mpk()
    st.session_state._active = (idx + 1) % 10
    save_pool()

def pool_stats():
    p, m = st.session_state._pool, mpk()
    loaded = sum(1 for s in p if s["key"].strip())
    used = sum(s["used"] for s in p if s["key"].strip())
    remain = sum(max(0, m - s["used"]) for s in p if s["key"].strip())
    return loaded, used, remain

def pool_reset(i):
    st.session_state._pool[i]["used"] = 0
    save_pool()

def pool_activate(i):
    st.session_state._active = i

def pool_delete(i):
    st.session_state._pool[i] = {"key": "", "used": 0, "label": f"API {i+1}"}
    st.session_state[f"key_{i}"] = ""
    st.session_state[f"lbl_{i}"] = f"API {i+1}"
    save_pool()

# ═════════════════════════════════════════════════════════════════
# METİN ÖN İŞLEME
# ═════════════════════════════════════════════════════════════════
def num_tr(n: int) -> str:
    if n == 0:
        return "sıfır"
    O = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
    T = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
    def h(x):
        y, r = divmod(x, 100); t, o = divmod(r, 10); w = []
        if y > 1: w.append(O[y])
        if y: w.append("yüz")
        if t: w.append(T[t])
        if o: w.append(O[o])
        return " ".join(w)
    parts = []
    for div, name in ((10**9, "milyar"), (10**6, "milyon"), (1000, "bin")):
        q, n = divmod(n, div)
        if q:
            parts.append("bin" if (name == "bin" and q == 1) else f"{h(q)} {name}")
    if n:
        parts.append(h(n))
    return " ".join(parts)

def prepare_text(t: str) -> str:
    c = cfg()
    if c["nums"]:
        t = re.sub(r"%\s?(\d{1,9})", lambda m: "yüzde " + num_tr(int(m.group(1))), t)
        def _time(m):
            hh, mm = int(m.group(1)), int(m.group(2))
            return num_tr(hh) + ("" if mm == 0 else (" sıfır " + num_tr(mm) if mm < 10 else " " + num_tr(mm)))
        t = re.sub(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)", _time, t)
        t = re.sub(r"(?<![\d.,])(\d{1,12})(?!\d|[.,]\d)", lambda m: num_tr(int(m.group(1))), t)
    if c["use_dict"]:
        for line in c["dict"].splitlines():
            if "=" in line:
                a, b = line.split("=", 1)
                a, b = a.strip(), b.strip()
                if a:
                    t = re.sub(r"(?<!\w)" + re.escape(a) + r"(?!\w)", lambda m, b=b: b, t)
    return t

def split_segments(text):
    out, pos = [], 0
    for m in PAUSE_RE.finditer(text):
        seg = text[pos:m.start()].strip()
        if seg:
            out.append(("t", seg))
        out.append(("p", min(float(m.group(1).replace(",", ".")), 15.0)))
        pos = m.end()
    tail = text[pos:].strip()
    if tail:
        out.append(("t", tail))
    return out

def chunk_text(t, limit):
    if len(t) <= limit:
        return [t]
    sents = re.split(r"(?<=[.!?…])\s+", t)
    chunks, cur = [], ""
    for s in sents:
        if cur and len(cur) + len(s) + 1 > limit:
            chunks.append(cur); cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        chunks.append(cur)
    return chunks

def count_calls(text):
    n = 0
    for kind, val in split_segments(prepare_text(text)):
        if kind == "t":
            n += len(chunk_text(val, cfg()["chunk_chars"])) if cfg()["chunk"] else 1
    return n

# ═════════════════════════════════════════════════════════════════
# SES İŞLEME
# ═════════════════════════════════════════════════════════════════
def pcm2wav(pcm: bytes, rate=SR, ch=1, sw=2) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(ch); wf.setsampwidth(sw); wf.setframerate(rate)
        wf.writeframes(pcm)
    return buf.getvalue()

def wav_dur(b: bytes) -> float:
    try:
        with wave.open(io.BytesIO(b), "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return 0.0

def read_wav_np(b: bytes):
    with wave.open(io.BytesIO(b), "rb") as w:
        ch, sw, sr = w.getnchannels(), w.getsampwidth(), w.getframerate()
        raw = w.readframes(w.getnframes())
    if sw != 2:
        raise ValueError("Yalnızca 16-bit PCM WAV destekleniyor.")
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        a = a[: len(a) // ch * ch].reshape(-1, ch).mean(axis=1)
    if sr != SR and len(a) > 1:
        a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * SR / sr)),
                      np.arange(len(a)), a).astype(np.float32)
    return a, SR

def np_to_wav(a) -> bytes:
    return pcm2wav((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())

def silence(sec: float) -> bytes:
    return b"\x00\x00" * int(sec * SR)

def postprocess(pcm: bytes) -> bytes:
    c = cfg()
    a = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    if len(a) == 0:
        return pcm
    if c["trim"]:
        idx = np.where(np.abs(a) > 0.008)[0]
        if len(idx):
            a = a[max(0, idx[0] - int(0.05 * SR)): idx[-1] + int(0.10 * SR)]
    if c["comp"]:
        a = np.tanh(a * 1.9) / np.tanh(1.9)
    if c["norm"]:
        pk = float(np.abs(a).max())
        if pk > 0:
            a = a * (0.89 / pk)
    f = int(c["fade_ms"] / 1000 * SR)
    if f > 0 and len(a) > 2 * f:
        a[:f] *= np.linspace(0, 1, f)
        a[-f:] *= np.linspace(1, 0, f)
    a = np.concatenate([np.zeros(int(c["head"] * SR), np.float32), a,
                        np.zeros(int(c["tail"] * SR), np.float32)])
    return (np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()

def waveform_svg(wav: bytes, w=600, h=54, bars=110) -> str:
    try:
        a, _ = read_wav_np(wav)
    except Exception:
        return ""
    if len(a) == 0:
        return ""
    step = max(1, len(a) // bars)
    peaks = [float(np.abs(a[i:i + step]).max()) for i in range(0, len(a), step)][:bars]
    bw = w / len(peaks)
    rects = "".join(
        f"<rect x='{i*bw:.1f}' y='{(h-max(2, p*h))/2:.1f}' width='{bw*0.7:.1f}' "
        f"height='{max(2, p*h):.1f}' rx='1' fill='#e05252'/>" for i, p in enumerate(peaks))
    return (f"<div class='wf-wrap'><svg viewBox='0 0 {w} {h}' width='100%' height='{h}' "
            f"preserveAspectRatio='none'>{rects}</svg></div>")

# ═════════════════════════════════════════════════════════════════
# MP3 / DECODE / YAYIN MOTORU  (44.1 kHz stereo, diske akışlı yazım)
# ═════════════════════════════════════════════════════════════════
SR2 = 44100
MP3_OK = lameenc is not None

def smooth(env, k):
    k = max(1, int(k))
    pad = np.pad(env, (k // 2, k - k // 2), mode="edge")
    c = np.concatenate([[0.0], np.cumsum(pad, dtype=np.float64)])
    return ((c[k:] - c[:-k]) / k)[:len(env)].astype(np.float32)

def decode_mono(data) -> np.ndarray:
    data = bytes(data)
    if miniaudio is not None:
        d = miniaudio.decode(data, output_format=miniaudio.SampleFormat.SIGNED16, nchannels=1, sample_rate=SR)
        return np.frombuffer(d.samples, dtype=np.int16).astype(np.float32) / 32768.0
    if data[:4] == b"RIFF":
        return read_wav_np(data)[0]
    raise RuntimeError("MP3 okumak için: pip install miniaudio")

def decode_stereo(data) -> np.ndarray:
    data = bytes(data)
    if miniaudio is not None:
        d = miniaudio.decode(data, output_format=miniaudio.SampleFormat.SIGNED16, nchannels=2, sample_rate=SR2)
        a = np.frombuffer(d.samples, dtype=np.int16).astype(np.float32) / 32768.0
        return a[: len(a) // 2 * 2].reshape(-1, 2)
    if data[:4] == b"RIFF":
        with wave.open(io.BytesIO(data), "rb") as w:
            ch, sw, sr = w.getnchannels(), w.getsampwidth(), w.getframerate()
            raw = w.readframes(w.getnframes())
        if sw != 2:
            raise ValueError("Yalnızca 16-bit WAV destekleniyor.")
        a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        a = a[: len(a) // ch * ch].reshape(-1, ch)
        a = np.stack([a[:, 0], a[:, 1] if ch > 1 else a[:, 0]], axis=1)
        if sr != SR2 and len(a) > 1:
            n = int(len(a) * SR2 / sr)
            idx = np.linspace(0, len(a) - 1, n)
            a = np.stack([np.interp(idx, np.arange(len(a)), a[:, c]) for c in (0, 1)], axis=1).astype(np.float32)
        return a
    raise RuntimeError("MP3 okumak için: pip install miniaudio")

def mono_to_st(a) -> np.ndarray:
    if len(a) == 0:
        return np.zeros((0, 2), np.float32)
    n = int(len(a) * SR2 / SR)
    x = np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)
    return np.stack([x, x], axis=1)

def wav_to_st(wav: bytes) -> np.ndarray:
    return mono_to_st(read_wav_np(wav)[0])

def wav_to_mp3(wav: bytes, kbps=192):
    if lameenc is None:
        return None
    a, _ = read_wav_np(wav)
    e = lameenc.Encoder()
    e.set_bit_rate(kbps); e.set_in_sample_rate(SR); e.set_channels(1); e.set_quality(2)
    return bytes(e.encode((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()) + e.flush())

@st.cache_data(show_spinner=False, max_entries=20)
def mp3_bytes(wav: bytes):
    try:
        return wav_to_mp3(wav)
    except Exception:
        return None

def rms_norm(a, target_db=-16.0):
    if len(a) == 0:
        return a
    rms = float(np.sqrt(np.mean(np.square(a[::4]))))
    if rms < 1e-5:
        return a
    g = 10 ** ((target_db - 20 * np.log10(rms)) / 20)
    pk = float(np.abs(a).max())
    if pk * g > 0.97:
        g = 0.97 / pk
    return a * np.float32(g)

def _guard(a):
    pk = float(np.abs(a).max()) if len(a) else 0.0
    return a * np.float32(0.98 / pk) if pk > 0.98 else a

def _duck_env(n, start, length, duck_db, ramp=0.3):
    env = np.ones(n, np.float32)
    s, e = max(0, start), min(n, start + length)
    if e > s:
        env[s:e] = 10 ** (-duck_db / 20)
    return smooth(env, int(ramp * SR2))

def _fade(a, fi, fo):
    n = len(a)
    if fi > 0 and n:
        fi = min(fi, n); a[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)[:, None]
    if fo > 0 and n:
        fo = min(fo, n); a[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
    return a

def _overlay(seg, voice, start, duck_db):
    start = max(0, start)
    need = start + len(voice)
    if need > len(seg):
        seg = np.concatenate([seg, np.zeros((need - len(seg), 2), np.float32)])
    out = seg * _duck_env(len(seg), start, len(voice), duck_db)[:, None]
    out[start:start + len(voice)] += voice
    return _guard(out)

def _bed_mix(voice, bed, o):
    pre, post = int(float(o["bed_pre"]) * SR2), int(float(o["bed_post"]) * SR2)
    total = pre + len(voice) + post
    if len(bed) == 0:
        return voice
    if len(bed) >= total:
        bed = bed[:total]
    else:
        bed = np.tile(bed, (int(np.ceil(total / len(bed))), 1))[:total]
    bed = rms_norm(bed, float(o["target_db"])) * np.float32(10 ** (float(o["bed_level"]) / 20))
    bed = bed * _duck_env(total, pre, len(voice), float(o["bed_duck"]))[:, None]
    bed = _fade(bed, int(0.3 * SR2), int(1.5 * SR2))
    bed[pre:pre + len(voice)] += voice
    return _guard(bed)

def mix_music(voice_wav, music_data, level_db, duck_db, pre, post):
    v, _ = read_wav_np(voice_wav)
    m = decode_mono(music_data)
    if len(m) == 0:
        raise ValueError("Müzik dosyası boş.")
    p, q = int(pre * SR), int(post * SR)
    total = p + len(v) + q
    m = np.tile(m, int(np.ceil(total / len(m))))[:total]
    env = np.ones(total, np.float32)
    env[p:p + len(v)] = 10 ** (-duck_db / 20)
    env = smooth(env, int(0.35 * SR))
    m = m * env * (10 ** (level_db / 20))
    fo = min(len(m), int(1.5 * SR))
    m[-fo:] *= np.linspace(1, 0, fo)
    out = m.copy()
    out[p:p + len(v)] += v
    pk = float(np.abs(out).max())
    if pk > 0.95:
        out *= 0.95 / pk
    return np_to_wav(out)

def fill_vars(text, ctx):
    t = text
    for k, v in ctx.items():
        t = t.replace("{" + k + "}", v)
    return t

class _Sink:
    def __init__(self, path, fmt, kbps):
        self.fmt, self.n, self.path = fmt, 0, path
        if fmt == "mp3":
            if lameenc is None:
                raise RuntimeError("MP3 çıktı için: pip install lameenc")
            self.f = open(path, "wb")
            self.enc = lameenc.Encoder()
            self.enc.set_bit_rate(int(kbps)); self.enc.set_in_sample_rate(SR2)
            self.enc.set_channels(2); self.enc.set_quality(2)
        else:
            self.w = wave.open(str(path), "wb")
            self.w.setnchannels(2); self.w.setsampwidth(2); self.w.setframerate(SR2)
    limit = 0
    def write(self, a):
        if len(a) == 0:
            return
        if self.limit:
            room = self.limit - self.n
            if room <= 0:
                return
            if len(a) >= room:
                a = a[:room].copy()
                _fade(a, 0, min(len(a), int(0.6 * SR2)))
        b = np.ascontiguousarray((np.clip(a, -1, 1) * 32767).astype(np.int16)).tobytes()
        self.n += len(a)
        if self.fmt == "mp3":
            self.f.write(self.enc.encode(b))
        else:
            self.w.writeframes(b)
    def close(self):
        if self.fmt == "mp3":
            self.f.write(self.enc.flush()); self.f.close()
        else:
            self.w.close()
    def abort(self):
        try: self.close()
        except Exception: pass
        try: Path(self.path).unlink()
        except Exception: pass

def build_song_segment(song, it, intro, outro, o, prev_kind):
    cf_s = float(o["crossfade"])
    seg = song
    lim = float(it.get("limit", 0) or 0)
    if lim > 0:
        seg = seg[: int(lim * SR2)]
    if o.get("rms_norm", True):
        seg = rms_norm(seg, float(o["target_db"]))
    else:
        seg = seg.copy()
    seg = _fade(seg, int(float(o["fade_in"]) * SR2), int(float(o["fade_out"]) * SR2))
    pre = post = None
    duck = float(o["duck_db"])
    if intro is not None:
        if it.get("intro_mode", "over") == "over":
            d = float(it.get("intro_delay", 2.0))
            if prev_kind == "song":
                d = max(d, cf_s)       # ses, crossfade bitmeden başlamasın
            seg = _overlay(seg, intro, int(d * SR2), duck)
        else:
            pre = intro
    if outro is not None:
        if it.get("outro_mode", "over") == "over":
            gap = max(float(o["outro_end_gap"]), cf_s)
            seg = _overlay(seg, outro, len(seg) - len(outro) - int(gap * SR2), duck)
        else:
            post = outro
    g = np.zeros((int(0.3 * SR2), 2), np.float32)
    parts = ([pre, g] if pre is not None else []) + [seg] + ([g, post] if post is not None else [])
    return np.concatenate(parts) if len(parts) > 1 else seg, pre is not None, post is not None

def render_broadcast(items, o, get_song, get_ann, names, out_path, fmt="mp3", progress=None, get_clip=None, max_sec=0):
    cf = int(float(o["crossfade"]) * SR2)
    K = max(cf, 1)
    sink = _Sink(out_path, fmt, o.get("kbps", 192))
    sink.limit = int(float(max_sec) * SR2) if max_sec else 0
    vg = np.float32(10 ** (float(o.get("voice_db", 0)) / 20))
    carry = None
    cues, tl = [], 0
    lim = int(float(max_sec) * SR2) if max_sec else 0
    prev_kind, prev_post = None, False
    n = max(1, len(items))
    song_idx = [i for i, x in enumerate(items) if x["kind"] == "song"]

    def ann_st(text, voice):
        t = text.strip()
        if not t:
            return None
        return wav_to_st(get_ann(t, voice)) * vg

    try:
        for idx, it in enumerate(items):
            kind = it["kind"]
            prevs = [i for i in song_idx if i < idx]
            nexts = [i for i in song_idx if i > idx]
            ctx = {"sarki": names.get(it.get("song", ""), ""),
                   "onceki": names.get(items[prevs[-1]]["song"], "") if prevs else "",
                   "sonraki": names.get(items[nexts[0]]["song"], "") if nexts else "",
                   "saat": datetime.datetime.now().strftime("%H:%M")}
            if progress:
                lbl = ctx["sarki"] if kind == "song" else ("anons" if kind == "ann" else "boşluk")
                progress(idx / n, f"{idx+1}/{n} · {lbl}")
            seg, has_pre, has_post, cue_name = None, False, False, ""
            if kind == "song":
                data = get_song(it["song"])
                if data is None:
                    continue
                song = decode_stereo(data)
                intro = ann_st(fill_vars(it.get("intro", ""), ctx), it.get("voice", ""))
                outro = ann_st(fill_vars(it.get("outro", ""), ctx), it.get("voice", ""))
                seg, has_pre, has_post = build_song_segment(song, it, intro, outro, o, prev_kind)
                cue_name = names.get(it["song"], "")
            elif kind in ("ann", "clip"):
                if kind == "ann":
                    ftxt = fill_vars(it.get("text", ""), ctx)
                    v = ann_st(ftxt, it.get("voice", ""))
                    cue_name = ftxt.strip()[:80]
                else:
                    d0 = get_clip(it.get("arch")) if get_clip else None
                    v = (wav_to_st(d0) * vg) if d0 else None
                    cue_name = it.get("label", "Klip")
                if v is None:
                    continue
                bed = None
                if it.get("bed"):
                    d = get_song(it["bed"])
                    if d is not None:
                        bed = decode_stereo(d)
                seg = _bed_mix(v, bed, o) if bed is not None else v
            elif kind == "gap":
                seg = np.zeros((int(float(it.get("sec", 2)) * SR2), 2), np.float32)
            if seg is None or len(seg) == 0:
                continue
            xf = cf if (kind == "song" and prev_kind == "song" and not has_pre and not prev_post) else 0
            if carry is None:
                xe = 0
                carry = seg
            else:
                xe = min(xf, len(carry), len(seg))
                if xe > 0:
                    t = np.linspace(0, np.pi / 2, xe, dtype=np.float32)[:, None]
                    blend = carry[-xe:] * np.cos(t) + seg[:xe] * np.sin(t)
                    sink.write(carry[:-xe])
                    carry = np.concatenate([blend, seg[xe:]])
                else:
                    sink.write(carry)
                    carry = seg
            start_pos = tl - xe
            if kind != "gap":
                cues.append({"t": round(max(0, start_pos) / SR2, 1), "kind": kind, "name": cue_name})
            tl = start_pos + len(seg)
            if len(carry) > K:
                sink.write(carry[:-K]); carry = carry[-K:]
            if lim and (sink.n + len(carry)) >= lim:
                prev_kind, prev_post = kind, has_post
                break
            prev_kind, prev_post = kind, has_post
        if carry is not None:
            sink.write(carry)
        if sink.n == 0:
            raise ValueError("Üretilecek ses yok (akış boş veya dosyalar bulunamadı).")
        total = sink.n / SR2
        sink.close()
        if progress:
            progress(1.0, "Tamamlandı")
        return total, cues
    except Exception:
        sink.abort()
        raise


# ═════════════════════════════════════════════════════════════════
# GEMINI ÇAĞRILARI
# ═════════════════════════════════════════════════════════════════
TAG_STYLE = {"excitedly":"excited and energetic","whispers":"whispering","laughs":"cheerful, smiling",
             "seriously":"serious, newsreader tone","shouting":"loud and forceful",
             "sighs":"tired, sighing","normal":""}

def is_new_schema(model):
    """3.8+ modeller speech_metadata kullanır; 3.1 ve 2.5 düz metin + köşeli etiket."""
    return not (model.startswith("gemini-3.1") or model.startswith("gemini-2.5"))

def _turn(text, style="", speaker=None):
    """[excitedly] vb. etiketleri speech_metadata.style'a, [laughs]/[sighs]'i <laugh>/<sigh>'a çevirir."""
    parts = [style.strip()] if style.strip() else []
    first = TAG_RE.search(text)
    if first and TAG_STYLE.get(first.group(1).lower()):
        parts.append(TAG_STYLE[first.group(1).lower()])
    t = re.sub(r"\[laughs\]", "<laugh>", text, flags=re.I)
    t = re.sub(r"\[sighs\]", "<sigh>", t, flags=re.I)
    t = re.sub(r"[ \t]+", " ", TAG_RE.sub("", t)).strip()
    ann = {"type": "speech_metadata"}
    if speaker: ann["speaker"] = speaker
    if parts: ann["style"] = ", ".join(parts)
    item = {"type": "text", "text": t}
    if len(ann) > 1: item["annotations"] = [ann]
    return item

def _audio_from_interaction(it) -> bytes:
    try:
        d = it.output_audio.data
    except Exception:
        d = None
    if not d:
        raise RuntimeError("Model ses döndürmedi (metin filtreye takılmış veya çok uzun olabilir).")
    b = base64.b64decode(d) if isinstance(d, str) else bytes(d)
    if b[:4] == b"RIFF":      # 3.8 modelleri WAV döndürür -> ham PCM'e çevir
        with wave.open(io.BytesIO(b), "rb") as w:
            return w.readframes(w.getnframes())
    return b                   # 3.1 / 2.5: ham 24 kHz PCM

def make_client(api_key):
    # Interactions/TTS uçları v1beta'dadır; SDK varsayılanı v1 olduğundan 404 verebilir.
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(api_version="v1beta"))

def _interaction(api_key, model, input_, speech_cfg):
    c = make_client(api_key)
    if not hasattr(c, "interactions"):
        raise RuntimeError('google-genai sürümü eski. Güncelleyin: pip install -U "google-genai>=2.25.0"')
    it = c.interactions.create(model=model, input=input_, response_format={"type": "audio"},
                               generation_config={"speech_config": speech_cfg})
    return _audio_from_interaction(it)

FALLBACK = ["gemini-3.8-flash-lite-tts", "gemini-3.1-flash-tts-preview", "gemini-2.5-pro-preview-tts"]

def _is_404(e):
    m = str(e)
    return "404" in m or "NOT_FOUND" in m or "not_found" in m

def _with_fallback(model, fn):
    """Model 404 verirse sıradaki TTS modelini dener; çalışanı hatırlar."""
    orig = MODEL_ALIAS.get(model, model)
    fixed = st.session_state.get("_model_fix", {}).get(orig, orig)
    chain = [fixed] + [m for m in FALLBACK if m != fixed]
    last = None
    for m in chain:
        try:
            r = fn(m)
            if m != fixed:
                st.session_state.setdefault("_model_fix", {})[orig] = m
                st.toast(f"ℹ️ {fixed} bulunamadı → {m} kullanıldı")
            return r
        except Exception as e:
            if _is_404(e):
                last = e
                continue
            raise
    raise RuntimeError("Hiçbir TTS modeli bu anahtarla bulunamadı (404). Sidebar > Ayarlar > "
                       "'Anahtarımın TTS modellerini listele' ile erişimi kontrol edin.") from last

def _single_call(api_key, model, text, voice, lang, style):
    def go(m):
        if is_new_schema(m):
            inp = [{"type": "user_input", "content": [_turn(text, style)]}]
        else:
            inp = f"{style}\n\n{text}" if style.strip() else text
        return _interaction(api_key, m, inp, [{"voice": voice}])
    return _with_fallback(model, go)

def _multi_call(api_key, model, text, sp1, v1, sp2, v2, lang):
    def go(m):
        if is_new_schema(m):
            names = {sp1.lower(): sp1, sp2.lower(): sp2}
            items = []
            for line in text.splitlines():
                if not line.strip():
                    continue
                mm = re.match(r"^\s*([^:]{1,40}):\s*(.*)$", line)
                if mm and mm.group(1).strip().lower() in names:
                    items.append([names[mm.group(1).strip().lower()], mm.group(2)])
                elif items:
                    items[-1][1] += " " + line.strip()
            if not items:
                raise ValueError("Diyalog satırı bulunamadı (Ad: metin biçiminde olmalı).")
            content = [_turn(t, "", sp) for sp, t in items]
            return _interaction(api_key, m, [{"type": "user_input", "content": content}],
                                {"speakers": [{"speaker": sp1, "voice": v1}, {"speaker": sp2, "voice": v2}]})
        return _interaction(api_key, m, text,
                            [{"speaker": sp1, "voice": v1}, {"speaker": sp2, "voice": v2}])
    return _with_fallback(model, go)

def list_tts_models(api_key):
    c = make_client(api_key)
    out = []
    for m in c.models.list():
        n = getattr(m, "name", "") or ""
        if "tts" in n.lower():
            out.append(n.replace("models/", ""))
    return sorted(out)

def run_tts(call, chars):
    """Anahtar rotasyonu + yeniden deneme. call(api_key) -> pcm bytes"""
    last = None
    for attempt in range(4):
        key, idx = get_active_key()
        if key is None:
            raise RuntimeError("Kullanılabilir API anahtarı kalmadı.")
        try:
            raw = call(key)
            consume(idx, chars)
            return raw
        except Exception as e:
            last = e
            msg = str(e)
            low = msg.lower()
            if isinstance(e, (RuntimeError, ValueError)) and "429" not in msg:
                raise                      # bizim hatalarımız: tekrar denemenin anlamı yok
            if "INVALID_ARGUMENT" in msg:
                raise                      # 400: istek biçimi/model adı hatası, tekrar deneme
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in low:
                exhaust(idx); continue
            if "API_KEY_INVALID" in msg or "401" in msg or "403" in msg or "api key" in low:
                exhaust(idx); continue
            time.sleep(1.2 * (attempt + 1))
    raise last if last else RuntimeError("Bilinmeyen hata")

def synthesize(text, voice, model, lang, style):
    segs = split_segments(prepare_text(text))
    pcm, calls, tag, after_pause = bytearray(), 0, None, True
    for kind, val in segs:
        if kind == "p":
            pcm += silence(val); after_pause = True; continue
        chunks = chunk_text(val, cfg()["chunk_chars"]) if cfg()["chunk"] else [val]
        for ch in chunks:
            send = f"[{tag}] {ch}" if (tag and not TAG_RE.match(ch.lstrip())) else ch
            found = TAG_RE.findall(ch)
            if found:
                tag = found[-1].lower()
            raw = run_tts(lambda k, s=send: _single_call(k, model, s, voice, lang, style), len(send))
            if pcm and not after_pause:
                pcm += silence(0.12)
            pcm += raw; calls += 1; after_pause = False
    if calls == 0:
        raise ValueError("Seslendirilecek metin yok.")
    return pcm2wav(postprocess(bytes(pcm))), calls

def synthesize_multi(text, model, lang, sp1, v1, sp2, v2):
    raw = run_tts(lambda k: _multi_call(k, model, prepare_text(text), sp1, v1, sp2, v2, lang), len(text))
    return pcm2wav(postprocess(raw)), 1

# ═════════════════════════════════════════════════════════════════
# ARŞİV
# ═════════════════════════════════════════════════════════════════
def archive_add(voice, model, lang, style, text, wav, mode="tek", calls=1):
    dur = wav_dur(wav)
    now = datetime.datetime.now()
    uid = hashlib.md5((text + voice + str(time.time())).encode()).hexdigest()[:10]
    e = {"id": uid, "ts": now.strftime("%d.%m.%Y %H:%M:%S"), "ts_short": now.strftime("%d.%m %H:%M"),
         "voice": voice, "model": model,
         "model_short": model.replace("gemini-", "").replace("-preview", "").replace("-tts", ""),
         "lang": lang, "style": style[:60] if style else "", "text": text,
         "preview": text[:70].replace("\n", " ") + ("…" if len(text) > 70 else ""),
         "dur": round(dur, 1), "size": len(wav), "mode": mode, "calls": calls}
    (AUDIO / f"{uid}.wav").write_bytes(wav)
    arc = st.session_state._arc
    arc.insert(0, e)
    while len(arc) > MAX_ARCHIVE:
        old = arc.pop()
        try: (AUDIO / f"{old['id']}.wav").unlink()
        except Exception: pass
    jsave("archive.json", arc)
    s = st.session_state._stats
    s["secs"] += dur
    jsave("stats.json", s)
    return e

def archive_delete(eid):
    st.session_state._arc = [e for e in st.session_state._arc if e["id"] != eid]
    try: (AUDIO / f"{eid}.wav").unlink()
    except Exception: pass
    jsave("archive.json", st.session_state._arc)

def archive_clear():
    for e in st.session_state._arc:
        try: (AUDIO / f"{e['id']}.wav").unlink()
        except Exception: pass
    st.session_state._arc = []
    jsave("archive.json", [])

def get_entry(eid):
    for e in st.session_state._arc:
        if e["id"] == eid:
            return e
    return None

def read_audio(eid):
    try:
        return (AUDIO / f"{eid}.wav").read_bytes()
    except Exception:
        return None

def produce(text, voice, model, lang, style, mode):
    wav, calls = synthesize(text, voice, model, lang, style)
    return archive_add(voice, model, lang, style, text, wav, mode, calls)

def slug(s, n=24):
    return re.sub(r"[^\w\-]+", "_", s)[:n].strip("_") or "ses"

def zip_entries(entries, namefn):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        for i, e in enumerate(entries, 1):
            w = read_audio(e["id"])
            if w:
                z.writestr(namefn(i, e), w)
    return b.getvalue()

def vicon(voice):
    return VOICES.get(voice.split("+")[0], ("🎙️", ""))[0]

# ═════════════════════════════════════════════════════════════════
# FAVORİLER
# ═════════════════════════════════════════════════════════════════
def add_fav(name, text, voice, model, lang):
    st.session_state._favs.append({
        "id": hashlib.md5((name + str(time.time())).encode()).hexdigest()[:8],
        "name": name, "text": text, "voice": voice, "model": model, "lang": lang})
    jsave("favorites.json", st.session_state._favs)

def del_fav(i):
    st.session_state._favs.pop(i)
    jsave("favorites.json", st.session_state._favs)

def load_fav(i):
    f = st.session_state._favs[i]
    st.session_state["txt_tek"] = f["text"]
    use_voice(f.get("voice", "Kore"))

def use_voice(v):
    if v in VOICES:
        st.session_state["t1_g"] = "Tümü"
        st.session_state["t1_v"] = v

# ═════════════════════════════════════════════════════════════════
# ŞARKI KÜTÜPHANESİ & YAYIN AKIŞI (disk kalıcı)
# ═════════════════════════════════════════════════════════════════
PL_O_DEF = {"voice": "Kore", "model": next(iter(MODELS)), "lang": "tr-TR", "style": "",
            "crossfade": 4.0, "fade_in": 0.5, "fade_out": 2.0, "duck_db": 10, "voice_db": 0.0,
            "outro_end_gap": 1.5, "rms_norm": True, "target_db": -16.0,
            "bed_level": -4, "bed_duck": 12, "bed_pre": 2.0, "bed_post": 3.0,
            "fmt": "MP3", "kbps": 192}

def _pl_merge(d):
    base = {"name": "Yayın Akışı 1", "items": [], "o": dict(PL_O_DEF)}
    if isinstance(d, dict):
        base["name"] = d.get("name", base["name"])
        base["items"] = d.get("items", [])
        base["o"].update(d.get("o", {}))
    return base

_init("_pl", _pl_merge(jload("playlist_current.json", None)))
_init("_pl_ver", 0)
_init("_songs", jload("songs.json", []))
_init("_bcs", jload("broadcasts.json", []))

def K(name, uid=""):
    return f"p{st.session_state._pl_ver}_{name}_{uid}"

def songs_by_id():
    return {s["id"]: s for s in st.session_state._songs}

def _song_dur(path, data):
    if data[:4] == b"RIFF":
        return wav_dur(data)
    if miniaudio is not None:
        try:
            return float(miniaudio.get_file_info(str(path)).duration)
        except Exception:
            pass
    return len(data) / 16000.0

def song_add(name, data):
    md5 = hashlib.md5(data).hexdigest()
    songs = st.session_state._songs
    if any(s["md5"] == md5 for s in songs):
        return False
    ext = ".wav" if data[:4] == b"RIFF" else ".mp3"
    sid = md5[:10]
    path = SONGS / f"{sid}{ext}"
    path.write_bytes(data)
    songs.append({"id": sid, "name": Path(name).stem, "file": path.name,
                  "dur": round(_song_dur(path, data), 1), "md5": md5, "size": len(data), "tag": ""})
    jsave("songs.json", songs)
    return True

def song_delete(sid):
    s = songs_by_id().get(sid)
    if s:
        try: (SONGS / s["file"]).unlink()
        except Exception: pass
    st.session_state._songs = [x for x in st.session_state._songs if x["id"] != sid]
    jsave("songs.json", st.session_state._songs)

def song_bytes(sid):
    s = songs_by_id().get(sid)
    if not s:
        return None
    try:
        return (SONGS / s["file"]).read_bytes()
    except Exception:
        return None

def _uid():
    return hashlib.md5((str(time.time()) + str(np.random.rand())).encode()).hexdigest()[:8]

def pl_add_song(sid):
    st.session_state._pl["items"].append({
        "uid": _uid(), "kind": "song", "song": sid, "limit": 0.0, "intro": "", "intro_mode": "over",
        "intro_delay": 2.0, "outro": "", "outro_mode": "over", "voice": ""})

def pl_add_ann():
    st.session_state._pl["items"].append({"uid": _uid(), "kind": "ann", "text": "", "bed": None, "voice": ""})

def pl_add_gap():
    st.session_state._pl["items"].append({"uid": _uid(), "kind": "gap", "sec": 2.0})

def pl_move(i, d):
    it = st.session_state._pl["items"]
    j = i + d
    if 0 <= j < len(it):
        it[i], it[j] = it[j], it[i]

def pl_del(i):
    st.session_state._pl["items"].pop(i)

def pl_clear():
    st.session_state._pl["items"] = []

def pl_apply_tpl():
    ss = st.session_state
    for it in ss._pl["items"]:
        if it["kind"] == "song":
            if ss.get("tpl_do_in", True):
                it["intro"] = ss.tpl_in; ss[K("in", it["uid"])] = ss.tpl_in
            if ss.get("tpl_do_out", True):
                it["outro"] = ss.tpl_out; ss[K("out", it["uid"])] = ss.tpl_out

def pl_save():
    saved = jload("playlists.json", {})
    pl = st.session_state._pl
    saved[pl["name"]] = json.loads(json.dumps(pl))
    jsave("playlists.json", saved)

def pl_load(name):
    saved = jload("playlists.json", {})
    if name in saved:
        st.session_state._pl = _pl_merge(json.loads(json.dumps(saved[name])))
        st.session_state._pl_ver += 1

def pl_forget(name):
    saved = jload("playlists.json", {})
    saved.pop(name, None)
    jsave("playlists.json", saved)

def ann_wav(text, voice, o):
    key = hashlib.md5(f"{prepare_text(text)}|{voice}|{o['model']}|{o['style']}|{o['lang']}".encode()).hexdigest()[:16]
    f = ANN / f"{key}.wav"
    if f.exists():
        return f.read_bytes()
    wav, _ = synthesize(text, voice, o["model"], o["lang"], o["style"])
    f.write_bytes(wav)
    return wav

def bc_delete(bid):
    for e in st.session_state._bcs:
        if e["id"] == bid:
            try: (BROAD / f"{bid}.{e['fmt']}").unlink()
            except Exception: pass
    st.session_state._bcs = [e for e in st.session_state._bcs if e["id"] != bid]
    jsave("broadcasts.json", st.session_state._bcs)


# ── etiket · klip · otomatik akış · yapay zekâ metin ──────────────
def song_tags(s):
    return [t.strip().lower() for t in (s.get("tag") or "").split(",") if t.strip()]

def song_set_tag(sid):
    v = st.session_state.get(f"stag_{sid}", "")
    for s in st.session_state._songs:
        if s["id"] == sid and s.get("tag", "") != v:
            s["tag"] = v
            jsave("songs.json", st.session_state._songs)

def all_tags():
    return sorted({t for s in st.session_state._songs for t in song_tags(s)})

def pl_add_clip():
    eid = st.session_state.get("clip_sel")
    e = get_entry(eid) if eid else None
    if e:
        st.session_state._pl["items"].append({"uid": _uid(), "kind": "clip", "arch": eid, "bed": None,
                                              "label": f"{e['voice']} · {e['preview'][:30]}"})

def pl_add_ann_text(text):
    st.session_state._pl["items"].append({"uid": _uid(), "kind": "ann", "text": text, "bed": None, "voice": ""})

def _song_item(s, intro="", outro="", limit=0.0):
    return {"uid": _uid(), "kind": "song", "song": s["id"], "limit": float(limit), "intro": intro,
            "intro_mode": "over", "intro_delay": 2.0, "outro": outro, "outro_mode": "over", "voice": ""}

def pl_autobuild():
    ss = st.session_state
    rnd = random.Random(int(ss.get("ab_seed", 0)) or None)
    sel = [t.lower() for t in ss.get("ab_tags", [])]
    pool = [s for s in ss._songs if "jingle" not in song_tags(s) and (not sel or any(t in song_tags(s) for t in sel))]
    jingles = [s for s in ss._songs if "jingle" in song_tags(s)]
    if not pool:
        ss["_ab_msg"] = "⚠️ Uygun şarkı yok. Kütüphaneye şarkı ekleyin veya etiket seçimini değiştirin."
        return
    texts = [l.strip() for l in ss.get("ab_pool", "").splitlines() if l.strip()]
    target = float(ss.get("ab_min", 30)) * 60.0
    every = int(ss.get("ab_every", 3))
    cap = float(ss.get("ab_max", 0))
    use_tpl = bool(ss.get("ab_tpl", True))
    tin = ss.get("tpl_in", "Şimdi İmaj FM'de {sarki}.") if use_tpl else ""
    tout = ss.get("tpl_out", "{sarki} dinlediniz. Saat {saat}, İmaj FM sizinle.") if use_tpl else ""
    items, total, n, last, order = [], 0.0, 0, None, []
    def ann(t):
        return {"uid": _uid(), "kind": "ann", "text": t, "bed": None, "voice": ""}
    if ss.get("ab_open", "").strip():
        items.append(ann(ss.ab_open.strip())); total += len(ss.ab_open) / 15
    while total < target and n < 400:
        if not order:
            order = pool[:]
            rnd.shuffle(order)
            if len(order) > 1 and order[0]["id"] == last:
                order.append(order.pop(0))
        s = order.pop(0)
        last = s["id"]
        items.append(_song_item(s, tin, tout, cap))
        total += min(s["dur"], cap) if cap > 0 else s["dur"]
        n += 1
        if every > 0 and n % every == 0 and total < target:
            if texts:
                t = rnd.choice(texts); items.append(ann(t)); total += len(t) / 15
            if jingles:
                j = rnd.choice(jingles); items.append(_song_item(j)); total += j["dur"]
    if ss.get("ab_close", "").strip():
        items.append(ann(ss.ab_close.strip()))
    if ss.get("ab_append", False):
        ss._pl["items"].extend(items)
    else:
        ss._pl["items"] = items
    ss._pl_ver += 1
    ss["_ab_msg"] = f"✅ {n} şarkılık akış oluşturuldu (~{total/60:.0f} dk)."

TEXT_MODELS = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]

def run_text(prompt, model=""):
    chain = ([model] if model.strip() else []) + [m for m in TEXT_MODELS if m != model.strip()]
    last = None
    for m in chain:
        for _ in range(3):
            key, idx = get_active_key()
            if key is None:
                raise RuntimeError("Kullanılabilir API anahtarı kalmadı.")
            try:
                r = make_client(key).models.generate_content(model=m, contents=prompt)
                consume(idx, len(prompt))
                return (r.text or "").strip(), m
            except Exception as e:
                last = e
                msg = str(e)
                if _is_404(e):
                    break
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "API_KEY_INVALID" in msg or "api key" in msg.lower():
                    exhaust(idx); continue
                raise
    raise last if last else RuntimeError("Metin modeli bulunamadı.")

def copy_state(src, dst):
    st.session_state[dst] = st.session_state[src]

def ann_from_state(src):
    pl_add_ann_text(st.session_state[src])

def fav_from_state(src):
    t = st.session_state[src]
    add_fav("Yazar " + datetime.datetime.now().strftime("%d.%m %H:%M"), t, "Kore", next(iter(MODELS)), "tr-TR")

def cache_info():
    fs = list(ANN.glob("*.wav"))
    return len(fs), sum(f.stat().st_size for f in fs) / (1024 * 1024)

def clear_ann_cache():
    for f in ANN.glob("*.wav"):
        try: f.unlink()
        except Exception: pass
    for f in PREV.glob("*.wav"):
        try: f.unlink()
        except Exception: pass

def fmt_t(sec):
    sec = int(sec)
    return f"{sec//3600:02d}:{(sec%3600)//60:02d}:{sec%60:02d}"

KIND_TR = {"song": "Şarkı", "ann": "Anons", "clip": "Klip"}

def cue_text(cues, name=""):
    lines = [f"YAYIN AKIŞ LİSTESİ — {name}", ""]
    for c in cues:
        lines.append(f"{fmt_t(c['t'])}  {KIND_TR.get(c['kind'], c['kind'])}: {c['name']}")
    return "\n".join(lines)

def cue_csv(cues):
    rows = ["zaman,tur,ad"]
    for c in cues:
        rows.append(f"{fmt_t(c['t'])},{KIND_TR.get(c['kind'], c['kind'])},\"{c['name'].replace(chr(34), chr(39))}\"")
    return "\n".join(rows)


# ═════════════════════════════════════════════════════════════════
# UI YARDIMCILARI
# ═════════════════════════════════════════════════════════════════
def esc(s):
    return _html.escape(str(s))

def add_tag(k, t):
    st.session_state[k] = st.session_state.get(k, "") + t

def set_text(k, v):
    st.session_state[k] = v

def tag_buttons(state_key, prefix):
    cols = st.columns(len(ETAGS))
    for i, (em, lbl, tag) in enumerate(ETAGS):
        cols[i].button(em, key=f"{prefix}_et_{i}", help=f"{lbl}: {tag.strip()}",
                       **UCW, on_click=add_tag, args=(state_key, tag))

def text_stats(text):
    plain = PAUSE_RE.sub("", TAG_RE.sub("", prepare_text(text)))
    cc, wc = len(plain), len(plain.split())
    sc = max(1, plain.count(".") + plain.count("!") + plain.count("?"))
    est = max(1.0, cc / 15)
    calls = count_calls(text)
    cost = est / 60 * float(cfg()["usd_min"])
    st.markdown(f"<div class='tiny'>📊 {cc} karakter · {wc} kelime · {sc} cümle · ~{est:.0f}s · "
                f"<b>{calls} API isteği</b> · ~${cost:.4f}</div>", unsafe_allow_html=True)

def _apply_preset(p):
    st.session_state[f"{p}_str"] = STYLE_PRESETS[st.session_state[f"{p}_ps"]]

def style_widget(p):
    _init(f"{p}_str", "")
    st.selectbox("Preset", list(STYLE_PRESETS), key=f"{p}_ps", label_visibility="collapsed",
                 on_change=_apply_preset, args=(p,))
    a, b = st.columns(2)
    tr = a.text_area("TR", height=62, key=f"{p}_str", label_visibility="collapsed", placeholder="🇹🇷 Coşkulu oku...")
    en = b.text_area("EN", height=62, key=f"{p}_sen", label_visibility="collapsed", placeholder="🇬🇧 Read excited...")
    return " / ".join(filter(None, [tr.strip(), en.strip()]))

def pick_model_lang(p):
    models = get_models()
    mk = st.selectbox("Model", list(models), format_func=lambda k: models[k], key=f"{p}_m", label_visibility="collapsed")
    lk = st.selectbox("Dil", list(LANGUAGES), format_func=LANGUAGES.get, index=1, key=f"{p}_l", label_visibility="collapsed")
    return mk, lk

def voice_picker(p, default="Kore"):
    g = st.radio("Cinsiyet", ["Tümü", "♀ Kadın", "♂ Erkek"], horizontal=True,
                 label_visibility="collapsed", key=f"{p}_g")
    opts = [k for k, v in VOICES.items() if g == "Tümü" or v[0] == g[0]]
    if st.session_state.get(f"{p}_v") not in opts:
        st.session_state.pop(f"{p}_v", None)
    return st.selectbox("Ses", opts, index=opts.index(default) if default in opts else 0,
                        format_func=lambda x: f"{VOICES[x][0]} {x}  —  {VOICES[x][1]}",
                        label_visibility="collapsed", key=f"{p}_v")

def render_entry(e, k, wave=True):
    wav = read_audio(e["id"])
    if wav is None:
        st.warning("Ses dosyası bulunamadı."); return
    st.markdown(f"<div class='card g'>✅ {vicon(e['voice'])} {esc(e['voice'])} · {e['dur']}s · "
                f"{e.get('calls',1)} istek · {len(wav)//1024} KB</div>", unsafe_allow_html=True)
    if wave:
        st.markdown(waveform_svg(wav), unsafe_allow_html=True)
    st.audio(wav, format="audio/wav")
    c1, c2 = st.columns(2)
    c1.download_button("💾 WAV", wav, file_name=f"imajfm_{slug(e['voice'])}_{e['id']}.wav",
                       mime="audio/wav", **UCW, key=f"dl_{k}_{e['id']}")
    if MP3_OK:
        mp = mp3_bytes(wav)
        if mp:
            c2.download_button("🎧 MP3", mp, file_name=f"imajfm_{slug(e['voice'])}_{e['id']}.mp3",
                               mime="audio/mpeg", **UCW, key=f"dlm_{k}_{e['id']}")

def render_last(key, wave=True, cols=1):
    ents = [get_entry(i) for i in st.session_state._last.get(key, [])]
    ents = [e for e in ents if e]
    if not ents:
        return []
    cs = st.columns(cols) if cols > 1 else [st.container()]
    for i, e in enumerate(ents):
        with cs[i % len(cs)]:
            render_entry(e, f"{key}{i}", wave)
    return ents

def set_last(key, entries):
    st.session_state._last[key] = [e["id"] for e in entries]

# ═════════════════════════════════════════════════════════════════
# GİRİŞ
# ═════════════════════════════════════════════════════════════════
def check_login(u, p):
    try:
        su, sp = st.secrets.get("APP_USER", "kenan"), st.secrets.get("APP_PASS", "imajfm")
    except Exception:
        su, sp = "kenan", "imajfm"
    return hmac.compare_digest(u.encode(), str(su).encode()) and hmac.compare_digest(p.encode(), str(sp).encode())

if not st.session_state._auth:
    _, col, _ = st.columns([1, 1.05, 1])
    with col:
        st.markdown("""<div style='margin-top:65px;padding:30px;background:var(--panel);border:1px solid var(--border);border-radius:18px;'>
        <h2 style='text-align:center;font-family:Syne,sans-serif;font-weight:800;font-size:1.5rem;margin:0 0 3px;background:linear-gradient(90deg,var(--h1a) 20%,#ff6060);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>🎙️ İmaj FM</h2>
        <p style='text-align:center;color:var(--muted);font-size:.7rem;letter-spacing:.15em;margin:0;'>TTS STÜDYO v6 · GÜVENLİ GİRİŞ</p></div>""", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Kullanıcı", placeholder="👤  kullanıcı adı", label_visibility="collapsed")
            p = st.text_input("Şifre", type="password", placeholder="🔑  şifre", label_visibility="collapsed")
            if st.form_submit_button("Stüdyoya Bağlan →", type="primary", **UCW):
                if check_login(u, p):
                    st.session_state._auth = True; st.rerun()
                else:
                    st.error("❌ Hatalı giriş.")
    st.stop()

# ═════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<div style='text-align:center;padding:5px 0 11px;'><span style='font-family:Syne,sans-serif;font-size:.95rem;font-weight:800;background:linear-gradient(90deg,var(--h1a),#ff6060);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>🎙️ İmaj FM</span> <span style='font-size:.62rem;color:var(--muted);letter-spacing:.1em;'> TTS v6</span></div>", unsafe_allow_html=True)

    look_controls("_sb")
    ak_sb, ai_sb = get_active_key()
    tk_sb, tu_sb, tr_sb = pool_stats()
    with st.expander(f"🗝️  API Havuzu  ·  {tk_sb}/10  ·  {tr_sb} kalan", expanded=True):
        if ak_sb:
            used_a = st.session_state._pool[ai_sb]["used"]
            pct = used_a / mpk()
            bc = "#22c55e" if pct < .6 else ("#f59e0b" if pct < .9 else "#ef4444")
            st.markdown(f"<div style='background:var(--bg2);border-radius:8px;padding:8px 10px;margin-bottom:7px;font-size:.73rem;color:var(--text2);'>"
                        f"Aktif: <b style='color:#22c55e;'>{esc(st.session_state._pool[ai_sb]['label'])}</b> · "
                        f"Kalan: <b>{mpk()-used_a}/{mpk()}</b> · Toplam kalan: <b style='color:#3b82f6;'>{tr_sb}</b>"
                        f"<div class='qbar'><div class='qbar-f' style='width:{pct*100:.0f}%;background:{bc};'></div></div>"
                        f"<div style='font-size:.61rem;color:var(--muted);'>Kota/hata olunca otomatik sıradaki anahtara geçer · sayaç günlük sıfırlanır</div></div>",
                        unsafe_allow_html=True)
        else:
            st.markdown("<div class='card r'>⛔ API yok! Aşağıdan ekleyin.</div>", unsafe_allow_html=True)
        st.markdown("<span class='sl2'>▸ 10 API SLOTU</span>", unsafe_allow_html=True)
        for i in range(10):
            s = st.session_state._pool[i]
            has, used = bool(s["key"].strip()), s["used"]
            full = has and used >= mpk()
            warn = has and used >= int(mpk() * .6) and not full
            act = (i == st.session_state._active) and has and not full
            icon = "⬜" if not has else ("🔴" if full else ("🟡" if warn else "🟢"))
            badge = "boş" if not has else ("DOLU" if full else f"{used}/{mpk()}")
            with st.expander(f"{icon} {s['label']}{' ◀' if act else ''}  ·  {badge}", expanded=False):
                s["label"] = st.text_input("İsim", value=s["label"], key=f"lbl_{i}", label_visibility="collapsed")
                s["key"] = st.text_input("Key", value=s["key"], type="password", key=f"key_{i}",
                                         placeholder="AIzaSy...", label_visibility="collapsed")
                k1, k2, k3 = st.columns(3)
                k1.button("🔄", key=f"rst_{i}", help="Sayacı sıfırla", **UCW, on_click=pool_reset, args=(i,))
                k2.button("▶", key=f"act_{i}", help="Aktif yap", **UCW, on_click=pool_activate, args=(i,))
                k3.button("🗑️", key=f"del_{i}", help="Sil", **UCW, on_click=pool_delete, args=(i,))

    c = cfg()
    with st.expander("🎚️  Ses İşleme & Ayarlar", expanded=False):
        c["norm"] = st.checkbox("Ses seviyesini normalize et", c["norm"], key="c_norm")
        c["trim"] = st.checkbox("Baş/son sessizliği kırp", c["trim"], key="c_trim")
        c["comp"] = st.checkbox("Radyo sıkıştırma (soft limiter)", c["comp"], key="c_comp")
        c["fade_ms"] = st.slider("Fade (ms)", 0, 300, int(c["fade_ms"]), key="c_fade")
        c["head"] = st.slider("Baş boşluk (s)", 0.0, 2.0, float(c["head"]), 0.05, key="c_head")
        c["tail"] = st.slider("Son boşluk (s)", 0.0, 3.0, float(c["tail"]), 0.05, key="c_tail")
        st.markdown("<span class='sl2'>▸ METİN</span>", unsafe_allow_html=True)
        c["nums"] = st.checkbox("Sayıları Türkçe okut (2026, %20, 20:30)", c["nums"], key="c_nums")
        c["use_dict"] = st.checkbox("Telaffuz sözlüğünü uygula", c["use_dict"], key="c_usedict")
        c["dict"] = st.text_area("Sözlük (her satır: yazım=okunuş)", c["dict"], height=90, key="c_dict")
        c["chunk"] = st.checkbox("Uzun metni cümle bazlı parçala", c["chunk"], key="c_chunk")
        c["chunk_chars"] = st.slider("Parça uzunluğu (karakter)", 200, 2000, int(c["chunk_chars"]), 50, key="c_cc")
        st.markdown("<span class='sl2'>▸ KOTA / MALİYET</span>", unsafe_allow_html=True)
        c["max_per_key"] = st.number_input("Anahtar başına günlük istek", 1, 1000, int(c["max_per_key"]), key="c_max")
        c["usd_min"] = st.number_input("Tahmini $/dk ses", 0.0, 5.0, float(c["usd_min"]), 0.005, format="%.3f", key="c_usd")
        c["custom_model"] = st.text_input("Özel model adı (opsiyonel)", c["custom_model"], key="c_cm",
                                          placeholder="örn. gemini-3.8-flash-tts")
        if st.button("🔎 Anahtarımın TTS modellerini listele", key="chk_models", **UCW):
            _k, _i = get_active_key()
            if not _k:
                st.warning("Önce bir API anahtarı ekleyin.")
            else:
                try:
                    st.session_state["_tts_models"] = list_tts_models(_k)
                except Exception as ex:
                    st.session_state["_tts_models"] = [f"HATA: {ex}"]
        if st.session_state.get("_tts_models") is not None:
            st.code("\n".join(st.session_state["_tts_models"]) or "TTS modeli bulunamadı", language=None)
    if c != st.session_state.get("_cfg_saved"):
        jsave("settings.json", c)
        st.session_state["_cfg_saved"] = dict(c)

    with st.expander("🧹  Depolama & Önbellek", expanded=False):
        _n, _mb = cache_info()
        st.caption(f"Anons/önizleme önbelleği: {_n} dosya · {_mb:.1f} MB (aynı metin tekrar üretilmez, istek tasarrufu sağlar)")
        st.button("Önbelleği temizle", key="clr_cache", on_click=clear_ann_cache, **UCW)
    with st.expander("🎭  Duygu Etiketleri", expanded=False):
        st.markdown("""<table class='ttbl'><thead><tr><th>Etiket</th><th>Anlamı</th></tr></thead><tbody>
        <tr><td><span class='tc'>[excitedly]</span></td><td>Coşkulu, hızlı</td></tr>
        <tr><td><span class='tc'>[whispers]</span></td><td>Fısıltı</td></tr>
        <tr><td><span class='tc'>[laughs]</span></td><td>Gülümseyen</td></tr>
        <tr><td><span class='tc'>[seriously]</span></td><td>Ciddi, haber tonu</td></tr>
        <tr><td><span class='tc'>[shouting]</span></td><td>Bağırma</td></tr>
        <tr><td><span class='tc'>[sighs]</span></td><td>Yorgun</td></tr>
        <tr><td><span class='tc'>[normal]</span></td><td>Normale dön</td></tr>
        <tr><td><span class='tc'>[pause 1.5]</span></td><td>1.5 sn sessizlik (gerçek)</td></tr>
        </tbody></table>""", unsafe_allow_html=True)
        st.markdown("`...` duraklama · `BÜYÜK` vurgu · Toplu sekmede `Kore | metin` ile satır başı ses seçimi")

    with st.expander("💾  Yedek", expanded=False):
        bk = json.dumps({"favorites": st.session_state._favs, "dict": c["dict"]}, ensure_ascii=False, indent=1)
        st.download_button("⬇️ Favori + sözlük yedeği", bk, file_name="imajfm_yedek.json",
                           mime="application/json", **UCW)
        up = st.file_uploader("Yedek yükle", type="json", key="imp", label_visibility="collapsed")
        if up is not None:
            raw = up.getvalue()
            hsh = hashlib.md5(raw).hexdigest()
            if hsh != st.session_state.get("_imp_hash"):
                try:
                    d = json.loads(raw.decode("utf-8"))
                    have = {f["id"] for f in st.session_state._favs}
                    for f in d.get("favorites", []):
                        if f.get("id") not in have:
                            st.session_state._favs.append(f)
                    jsave("favorites.json", st.session_state._favs)
                    if d.get("dict"):
                        c["dict"] = d["dict"]; st.session_state["c_dict"] = d["dict"]
                    st.session_state["_imp_hash"] = hsh
                    st.success("Yüklendi."); st.rerun()
                except Exception as ex:
                    st.error(f"Geçersiz yedek: {ex}")
        st.caption(f"Veri klasörü: {DATA.resolve()}")
    if st.session_state.get("_io_err"):
        st.caption(f"⚠️ Diske yazılamadı: {st.session_state['_io_err']}")
    if st.button("🚪 Çıkış", **UCW):
        st.session_state._auth = False; st.rerun()

# ═════════════════════════════════════════════════════════════════
# HEADER + METRİKLER
# ═════════════════════════════════════════════════════════════════
st.markdown("<div class='hdr'><h1>🎙️ İmaj FM · Seslendirme Stüdyosu</h1><p><span class='ldot'></span>Gemini TTS v6 &nbsp;·&nbsp; Kalıcı Arşiv &nbsp;·&nbsp; Montaj &amp; Fon Müziği &nbsp;·&nbsp; Akıllı API Rotasyonu &nbsp;·&nbsp; Ses Kütüphanesi</p></div>", unsafe_allow_html=True)

_lc, _lc2 = st.columns([3, 2])
with _lc:
    look_controls("")

tk_m, tu_m, tr_m = pool_stats()
ak_m, ai_m = get_active_key()
stt = st.session_state._stats
for col, (val, lbl, cl) in zip(st.columns(6), [
        ("30", "Ses", ""), (f"{tk_m}/10", "API Yüklü", "g"), (str(tr_m), "Kalan İstek", "a"),
        (str(len(st.session_state._arc)), "Arşiv", "b"), (str(stt["calls"]), "Toplam İstek", ""),
        (f"{stt['secs']:.0f}s", "Üretilen Ses", "p")]):
    col.markdown(f'<div class="mbox {cl}"><div class="v">{val}</div><div class="l">{lbl}</div></div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if ak_m is None:
    st.error("⛔ Kullanılabilir API anahtarı yok. Yeni üretim yapılamaz; arşiv, montaj, önbellekteki anonslarla yayın oluşturma ve kütüphane çalışmaya devam eder. Sol panelden anahtar ekleyin veya sayacı sıfırlayın.")
elif tr_m <= 2:
    st.warning(f"⚠️ Toplam kalan istek: {tr_m}. Kota bitmek üzere.")

tabs = st.tabs(["🎤 Tek", "🎭 Diyalog", "📦 Toplu", "🔬 A/B", "🎚️ Montaj", "📻 Otomasyon", "✍️ Anons Yazarı", "🎼 Ses Kütüphanesi", "⭐ Favoriler", "📂 Arşiv"])
t1, t2, t3, t4, t5, t6, t7, t8, t9, t10 = tabs

# ══════════════════════════════════════════════════════════════════
# TAB 1 — TEK KONUŞMACI
# ══════════════════════════════════════════════════════════════════
with t1:
    cL, cR = st.columns([1.05, 1], gap="large")
    with cL:
        st.markdown("<span class='sl'>▶ Şablon</span>", unsafe_allow_html=True)
        tm = st.selectbox("Şablon", ["— Yok —"] + list(TEMPLATES), label_visibility="collapsed", key="tmpl1")
        if tm != "— Yok —":
            st.button("📥 Şablonu Yükle", key="ltmpl1", on_click=set_text, args=("txt_tek", TEMPLATES[tm]))
        st.markdown("<span class='sl'>▶ Model & Dil</span>", unsafe_allow_html=True)
        mdl1, lng1 = pick_model_lang("t1")
        st.markdown("<span class='sl'>▶ Ses Karakteri</span>", unsafe_allow_html=True)
        vc1 = voice_picker("t1")
        st.markdown("<span class='sl'>▶ Duygu & Stil</span>", unsafe_allow_html=True)
        sty1 = style_widget("t1")
        st.markdown("<span class='sl'>▶ Favorilere Ekle</span>", unsafe_allow_html=True)
        fa, fb = st.columns([2, 1])
        fname = fa.text_input("Favori adı", placeholder="Favori ismi...", label_visibility="collapsed", key="fname1")
        if fb.button("⭐ Ekle", key="fadd1", **UCW):
            if fname.strip() and st.session_state.txt_tek.strip():
                add_fav(fname.strip(), st.session_state.txt_tek, vc1, mdl1, lng1)
                st.toast("⭐ Favorilere eklendi")
    with cR:
        st.markdown("<span class='sl'>▶ Anons Metni</span>", unsafe_allow_html=True)
        tag_buttons("txt_tek", "t1")
        txt1 = st.text_area("Metin", height=230, label_visibility="collapsed", key="txt_tek",
                            placeholder="Metni buraya yazın…")
        text_stats(txt1)
        prep = prepare_text(txt1)
        if prep != txt1:
            with st.expander("👁️ Okunacak metin (sayı/sözlük sonrası)", expanded=False):
                st.code(prep, language=None)
        if st.button(f"🔴  {vc1} ile Seslendir", type="primary", **UCW, key="btn1"):
            if not txt1.strip():
                st.warning("⚠️ Metin boş.")
            else:
                with st.spinner(f"🎙️ {vc1} seslendiriyor…"):
                    try:
                        set_last("tek", [produce(txt1, vc1, mdl1, lng1, sty1, "tek")])
                    except Exception as ex:
                        st.error(f"❌ {ex}")
        render_last("tek")

# ══════════════════════════════════════════════════════════════════
# TAB 2 — DİYALOG
# ══════════════════════════════════════════════════════════════════
with t2:
    cL2, cR2 = st.columns([1.05, 1], gap="large")
    with cL2:
        tm2 = st.selectbox("Şablon2", ["— Yok —"] + list(TEMPLATES), label_visibility="collapsed", key="tmpl2")
        if tm2 != "— Yok —":
            st.button("📥 Şablonu Yükle", key="ltmpl2", on_click=set_text, args=("txt_cift", TEMPLATES[tm2]))
        mdl2, lng2 = pick_model_lang("t2")
        mode2 = st.radio("Çıktı", ["Tek WAV (karışık diyalog)", "Ayrı WAV'lar + ZIP"], key="mode2")
        vkeys = list(VOICES)
        fmt = lambda x: f"{VOICES[x][0]} {x} — {VOICES[x][1]}"
        st.markdown("<span class='sl'>▶ Konuşmacı 1</span>", unsafe_allow_html=True)
        ca, cb = st.columns([1, 2])
        sp1n = ca.text_input("S1N", "Sunucu", label_visibility="collapsed", key="sp1n")
        sp1v = cb.selectbox("S1V", vkeys, format_func=fmt, index=vkeys.index("Kore"), label_visibility="collapsed", key="sp1v")
        st.markdown("<span class='sl'>▶ Konuşmacı 2</span>", unsafe_allow_html=True)
        cc_, cd_ = st.columns([1, 2])
        sp2n = cc_.text_input("S2N", "Misafir", label_visibility="collapsed", key="sp2n")
        sp2v = cd_.selectbox("S2V", vkeys, format_func=fmt, index=vkeys.index("Fenrir"), label_visibility="collapsed", key="sp2v")
    with cR2:
        st.markdown("<span class='sl'>▶ Diyalog Metni</span>", unsafe_allow_html=True)
        tag_buttons("txt_cift", "t2")
        txt2 = st.text_area("Diyalog", height=230, label_visibility="collapsed", key="txt_cift",
                            placeholder=f"{sp1n}: [excitedly] ...\n{sp2n}: [laughs] ...")
        text_stats(txt2)
        l1 = [l for l in txt2.splitlines() if re.match(rf"^\s*{re.escape(sp1n)}\s*:", l, re.I)]
        l2 = [l for l in txt2.splitlines() if re.match(rf"^\s*{re.escape(sp2n)}\s*:", l, re.I)]
        st.markdown(f"<div class='tiny'>{esc(sp1n)}: {len(l1)} satır · {esc(sp2n)}: {len(l2)} satır</div>", unsafe_allow_html=True)
        if st.button("🔴  Diyaloğu Seslendir", type="primary", **UCW, key="btn2"):
            if not txt2.strip():
                st.warning("⚠️ Metin boş.")
            elif mode2.startswith("Tek"):
                with st.spinner("🎭 Diyalog üretiliyor…"):
                    try:
                        wav, calls = synthesize_multi(txt2, mdl2, lng2, sp1n, sp1v, sp2n, sp2v)
                        set_last("cift", [archive_add(f"{sp1v}+{sp2v}", mdl2, lng2, "", txt2, wav, "cift", calls)])
                    except Exception as ex:
                        st.error(f"❌ {ex}")
            else:
                made = []
                for nm, vv in ((sp1n, sp1v), (sp2n, sp2v)):
                    lines = []
                    for l in txt2.splitlines():
                        m = re.match(rf"^\s*{re.escape(nm)}\s*:\s*(.*)$", l, re.I)
                        if m and m.group(1).strip():
                            lines.append(m.group(1).strip())
                    if lines:
                        with st.spinner(f"🎤 {nm} ({vv})…"):
                            try:
                                made.append(produce(" ".join(lines), vv, mdl2, lng2, "", "split"))
                            except Exception as ex:
                                st.error(f"❌ {nm}: {ex}")
                if made:
                    set_last("cift", made)
        ents2 = render_last("cift", cols=2)
        if len(ents2) > 1:
            zb = zip_entries(ents2, lambda i, e: f"{i:02d}_{slug(e['voice'])}.wav")
            st.download_button("📦 Hepsini ZIP indir", zb, file_name="imajfm_ayri_sesler.zip",
                               mime="application/zip", **UCW, key="dl2zip")

# ══════════════════════════════════════════════════════════════════
# TAB 3 — TOPLU
# ══════════════════════════════════════════════════════════════════
with t3:
    st.markdown("<div class='card b'><b>📦 Toplu Seslendirme</b> — Her satır ayrı WAV. Satır başına <code>Kore | metin</code> yazarak o satırın sesini değiştirebilirsiniz. Satır içi <code>[pause 1]</code> da çalışır.</div>", unsafe_allow_html=True)
    cL4, cR4 = st.columns([1, 1.2], gap="large")
    with cL4:
        mdl4, lng4 = pick_model_lang("t4")
        vc4 = voice_picker("t4", "Charon")
        sty4 = st.text_area("Stil", height=55, label_visibility="collapsed",
                            placeholder="Tüm satırlara uygulanacak stil…", key="sty4")
    with cR4:
        txt4 = st.text_area("Toplu", height=230, label_visibility="collapsed", key="txt_bulk",
                            placeholder="Her satıra bir metin…")
        jobs = []
        for ln in [l.strip() for l in txt4.splitlines() if l.strip()]:
            v, t = vc4, ln
            if "|" in ln:
                a, b = ln.split("|", 1)
                if a.strip() in VOICES:
                    v, t = a.strip(), b.strip()
            if t:
                jobs.append((v, t))
        need = sum(count_calls(t) for _, t in jobs)
        _, _, rem4 = pool_stats()
        warn4 = need > rem4
        st.markdown(f"<div class='card {'a' if warn4 else 'b'}'>{len(jobs)} satır · ~{need} API isteği · kalan: <b>{rem4}</b>"
                    f"{'<br>⚠️ Kota yetersiz olabilir!' if warn4 else ''}</div>", unsafe_allow_html=True)
        if st.button(f"🔴  {len(jobs)} Satırı Toplu Seslendir", type="primary", **UCW, key="btn4"):
            if not jobs:
                st.warning("⚠️ Satır yok.")
            else:
                made, errs = [], []
                prog = st.progress(0.0, "Başlatılıyor…")
                for i, (v, t) in enumerate(jobs):
                    prog.progress(i / len(jobs), f"{i+1}/{len(jobs)} · {v}: {t[:40]}")
                    try:
                        made.append(produce(t, v, mdl4, lng4, sty4, "bulk"))
                    except Exception as ex:
                        errs.append(f"Satır {i+1}: {ex}")
                        if "kalmadı" in str(ex):
                            break
                prog.empty()
                set_last("bulk", made)
                st.session_state["_bulk_err"] = errs
        for er in st.session_state.get("_bulk_err", []):
            st.markdown(f"<div class='card r'>❌ {esc(er)}</div>", unsafe_allow_html=True)
        ents4 = [get_entry(i) for i in st.session_state._last.get("bulk", [])]
        ents4 = [e for e in ents4 if e]
        if ents4:
            st.markdown(f"<div class='card g'>✅ {len(ents4)} dosya hazır</div>", unsafe_allow_html=True)
            st.download_button("📦 ZIP İndir", zip_entries(ents4, lambda i, e: f"{i:02d}_{slug(e['voice'])}_{slug(e['preview'], 18)}.wav"),
                               file_name="imajfm_toplu.zip", mime="application/zip", **UCW, key="dl4zip")
            for i, e in enumerate(ents4, 1):
                with st.expander(f"🔊 {i}. {e['voice']} · {e['preview'][:50]}", expanded=False):
                    w = read_audio(e["id"])
                    if w:
                        st.audio(w, format="audio/wav")

# ══════════════════════════════════════════════════════════════════
# TAB 4 — A/B TEST
# ══════════════════════════════════════════════════════════════════
with t4:
    st.markdown("<div class='card p'><b>🔬 A/B Test</b> — Aynı (veya farklı) metni iki ses/model/stil ile üretip yan yana dinleyin.</div>", unsafe_allow_html=True)
    same = st.checkbox("B için A'nın metnini kullan", value=False, key="ab_same")
    ca_, cb_ = st.columns(2, gap="large")
    with ca_:
        st.markdown("<div style='font-family:Syne,sans-serif;font-size:.72rem;font-weight:800;letter-spacing:.15em;color:#a78bfa;'>🅐 VERSİYON A</div>", unsafe_allow_html=True)
        mdla, lnga = pick_model_lang("ab_a")
        vca = voice_picker("ab_a", "Kore")
        stya = style_widget("ab_a")
        tag_buttons("txt_a", "ab1")
        txta = st.text_area("Metin A", height=130, label_visibility="collapsed", key="txt_a")
    with cb_:
        st.markdown("<div style='font-family:Syne,sans-serif;font-size:.72rem;font-weight:800;letter-spacing:.15em;color:#fb923c;'>🅑 VERSİYON B</div>", unsafe_allow_html=True)
        mdlb, lngb = pick_model_lang("ab_b")
        vcb = voice_picker("ab_b", "Fenrir")
        styb = style_widget("ab_b")
        tag_buttons("txt_b", "ab2")
        if same:
            st.text_area("Metin B", value=txta, height=130, label_visibility="collapsed", disabled=True, key="txt_b_disabled")
            txtb = txta
        else:
            txtb = st.text_area("Metin B", height=130, label_visibility="collapsed", key="txt_b")
    b1, b2, b3 = st.columns(3)
    run_a = b1.button("🅐 Sadece A", **UCW, key="btnab1")
    run_b = b2.button("🅑 Sadece B", **UCW, key="btnab2")
    run_ab = b3.button("🔴 A ve B birlikte", type="primary", **UCW, key="btnaboth")
    if run_a or run_b or run_ab:
        cur = dict(st.session_state._last.get("ab", {})) if isinstance(st.session_state._last.get("ab"), dict) else {}
        for flag, side, args in ((run_a or run_ab, "A", (txta, vca, mdla, lnga, stya)),
                                 (run_b or run_ab, "B", (txtb, vcb, mdlb, lngb, styb))):
            if flag:
                with st.spinner(f"{side} üretiliyor…"):
                    try:
                        cur[side] = produce(*args, f"ab-{side}")["id"]
                    except Exception as ex:
                        st.error(f"❌ {side}: {ex}")
        st.session_state._last["ab"] = cur
    ab = st.session_state._last.get("ab", {})
    if isinstance(ab, dict) and ab:
        ra, rb = st.columns(2)
        for colx, side in ((ra, "A"), (rb, "B")):
            with colx:
                e = get_entry(ab.get(side, ""))
                if e:
                    st.markdown(f"**{side}** · {e['voice']} · {e['model_short']}")
                    render_entry(e, f"ab{side}")

# ══════════════════════════════════════════════════════════════════
# TAB 5 — MONTAJ & FON MÜZİĞİ
# ══════════════════════════════════════════════════════════════════
with t5:
    arc = st.session_state._arc
    labels = {e["id"]: f"{e['ts_short']} · {e['voice']} · {e['dur']}s · {e['preview'][:32]}" for e in arc}
    if not arc:
        st.info("Montaj için önce arşive ses üretin.")
    else:
        st.markdown("<span class='sl'>▶ 1 · Parçaları Birleştir (seçim sırasıyla)</span>", unsafe_allow_html=True)
        sel = st.multiselect("Parçalar", list(labels), format_func=lambda i: labels[i], key="mon_sel", label_visibility="collapsed")
        gap = st.slider("Parçalar arası boşluk (s)", 0.0, 3.0, 0.4, 0.1, key="mon_gap")
        if st.button("🔗 Birleştir", key="mon_go", type="primary", disabled=len(sel) < 2):
            try:
                parts = []
                for i, eid in enumerate(sel):
                    a, _ = read_wav_np(read_audio(eid))
                    parts.append(a)
                    if i < len(sel) - 1:
                        parts.append(np.zeros(int(gap * SR), np.float32))
                wav = np_to_wav(np.concatenate(parts))
                set_last("montaj", [archive_add("Montaj", "-", "-", "", f"{len(sel)} parça birleşimi", wav, "montaj", 0)])
            except Exception as ex:
                st.error(f"❌ {ex}")
        render_last("montaj")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<span class='sl'>▶ 2 · Fon Müziği Mix (konuşmada otomatik kısılır)</span>", unsafe_allow_html=True)
        vsel = st.selectbox("Konuşma", list(labels), format_func=lambda i: labels[i], key="mix_v")
        src = st.radio("Fon müziği kaynağı", ["⬆️ Dosya yükle (MP3/WAV)", "🎵 Şarkı kütüphanesi"], horizontal=True, key="mix_src")
        bed_bytes = None
        if src.startswith("⬆️"):
            mus = st.file_uploader("Fon müziği (MP3 / WAV)", type=["wav", "mp3"], key="mix_up")
            bed_bytes = mus.getvalue() if mus else None
        else:
            _lib = st.session_state._songs
            if _lib:
                _sb = songs_by_id()
                _sid = st.selectbox("Şarkı", [x["id"] for x in _lib], format_func=lambda i: _sb[i]["name"], key="mix_song")
                bed_bytes = song_bytes(_sid)
            else:
                st.caption("Kütüphane boş. Otomasyon sekmesinden şarkı yükleyin.")
        m1, m2, m3, m4 = st.columns(4)
        lvl = m1.slider("Müzik seviyesi dB", -30, -3, -12, key="mix_lvl")
        duck = m2.slider("Konuşmada kısma dB", 0, 20, 10, key="mix_duck")
        pre = m3.slider("Giriş müziği (s)", 0.0, 8.0, 2.0, 0.5, key="mix_pre")
        post = m4.slider("Çıkış müziği (s)", 0.0, 10.0, 3.0, 0.5, key="mix_post")
        if st.button("🎼 Mix'le", key="mix_go", type="primary", disabled=bed_bytes is None):
            try:
                wav = mix_music(read_audio(vsel), bed_bytes, lvl, duck, pre, post)
                e0 = get_entry(vsel)
                set_last("mix", [archive_add(e0["voice"] + " + müzik", e0["model"], e0["lang"], "", e0["text"], wav, "montaj", 0)])
            except Exception as ex:
                st.error(f"❌ {ex}")
        render_last("mix")

# ══════════════════════════════════════════════════════════════════
# TAB 6 — RADYO OTOMASYON
# ══════════════════════════════════════════════════════════════════
with t6:
    pl = st.session_state._pl
    o = pl["o"]
    items = pl["items"]
    songs = st.session_state._songs
    sbyid = songs_by_id()
    snames = {s["id"]: s["name"] for s in songs}
    st.markdown("<div class='card b'><b>📻 Radyo Otomasyon</b> — Şarkı kütüphanesinden yayın akışı kurun: şarkı başı/sonu anonsu, fon müziği altında anons, crossfade geçişleri. Sonunda <b>tek parça tam yayın dosyası</b> (MP3/WAV) üretir.</div>", unsafe_allow_html=True)
    miss = []
    if miniaudio is None: miss.append("MP3 şarkı okumak için `pip install miniaudio`")
    if lameenc is None: miss.append("MP3 çıktı için `pip install lameenc`")
    if miss:
        st.warning(" · ".join(miss))

    # ── 1) KÜTÜPHANE ────────────────────────────────────────────
    st.markdown("<span class='sl'>▶ 1 · Şarkı Kütüphanesi</span>", unsafe_allow_html=True)
    ups = st.file_uploader("Şarkı yükle (MP3 / WAV · birden fazla seçilebilir)", type=["mp3", "wav"],
                           accept_multiple_files=True, key="song_up")
    if ups:
        added = 0
        for u in ups:
            try:
                if song_add(u.name, u.getvalue()):
                    added += 1
            except Exception as ex:
                st.error(f"{u.name}: {ex}")
        if added:
            st.toast(f"🎵 {added} şarkı eklendi")
            st.rerun()
    if not songs:
        st.caption("Kütüphane boş. Yukarıdan MP3/WAV yükleyin.")
    else:
        st.caption("İpucu: etiketine `jingle` yazdığınız kayıtlar otomatik akışta şarkı aralarına jingle olarak girer.")
        for s in songs:
            c1, c4, c2, c3 = st.columns([3, 2, 1, 1])
            c1.markdown(f"🎵 **{esc(s['name'])}** · {s['dur']:.0f} sn · {s['size']//1024} KB")
            c4.text_input("Etiket", value=s.get("tag", ""), key=f"stag_{s['id']}", label_visibility="collapsed",
                          placeholder="etiket: pop, jingle…", on_change=song_set_tag, args=(s["id"],))
            c2.button("➕", key=f"pls_{s['id']}", help="Akışa ekle", **UCW,
                      on_click=pl_add_song, args=(s["id"],))
            c3.button("🗑️", key=f"sdel_{s['id']}", help="Kütüphaneden sil", **UCW,
                      on_click=song_delete, args=(s["id"],))
        pv = st.selectbox("Önizle", ["—"] + [s["id"] for s in songs],
                          format_func=lambda i: "—" if i == "—" else sbyid[i]["name"], key="song_prev")
        if pv != "—":
            sb = song_bytes(pv)
            if sb:
                st.audio(sb, format="audio/wav" if sb[:4] == b"RIFF" else "audio/mpeg")

    # ── 2) AKIŞ ────────────────────────────────────────────────
    st.markdown("<span class='sl'>▶ 2 · Yayın Akışı</span>", unsafe_allow_html=True)
    pl["name"] = st.text_input("Akış adı", value=pl["name"], key=K("name"))
    b1, b2, b3 = st.columns(3)
    b1.button("➕ Anons bloğu", key="pl_add_ann", **UCW, on_click=pl_add_ann)
    b2.button("➕ Boşluk (2 sn)", key="pl_add_gap", **UCW, on_click=pl_add_gap)
    b3.button("🧹 Akışı temizle", key="pl_clear", **UCW, on_click=pl_clear)

    with st.expander("🪄 Toplu anons şablonu (tüm şarkılara uygula)", expanded=False):
        st.text_input("Şarkı öncesi anons", value="Şimdi İmaj FM'de {sarki}.", key="tpl_in")
        st.text_input("Şarkı sonrası anons", value="{sarki} dinlediniz. Saat {saat}, İmaj FM sizinle.", key="tpl_out")
        st.caption("Değişkenler: {sarki} · {onceki} · {sonraki} · {saat}")
        t1c, t2c = st.columns(2)
        t1c.checkbox("Başa uygula", True, key="tpl_do_in")
        t2c.checkbox("Sona uygula", True, key="tpl_do_out")
        st.button("Şablonu uygula", key="tpl_go", on_click=pl_apply_tpl, **UCW)

    with st.expander("🎙️ Arşivden hazır anons/klip ekle", expanded=False):
        arc_ = st.session_state._arc
        if not arc_:
            st.caption("Arşivde kayıt yok. Önce Tek/Toplu sekmesinden anons üretin.")
        else:
            labs_ = {e["id"]: f"{e['ts_short']} · {e['voice']} · {e['dur']}s · {e['preview'][:34]} · #{e['id'][:4]}" for e in arc_}
            inv_ = {v: k for k, v in labs_.items()}
            pick_ = st.selectbox("Arşiv kaydı", list(labs_.values()), key="clip_lbl")
            st.session_state["clip_sel"] = inv_.get(pick_)
            st.button("➕ Akışa ekle (yeniden üretim yok, istek harcamaz)", key="clip_add", on_click=pl_add_clip, **UCW)

    with st.expander("🤖 Otomatik akış oluşturucu (saat çarkı)", expanded=False):
        st.caption("Hedef süreye kadar şarkıları karıştırır, belli aralıklarla anons ve jingle ekler.")
        st.slider("Hedef süre (dk)", 10, 240, 30, 5, key="ab_min")
        st.multiselect("Şarkı etiketleri (boş = tümü)", all_tags(), key="ab_tags")
        a1, a2 = st.columns(2)
        a1.slider("Her N şarkıda bir anons/jingle", 0, 8, 3, key="ab_every")
        a2.number_input("Şarkı en fazla (sn) · 0 = tamamı", 0.0, 600.0, 0.0, 15.0, key="ab_max")
        st.text_area("Anons havuzu (her satır bir anons, rastgele seçilir)", height=90, key="ab_pool",
                     value="[excitedly] İmaj FM, müziğin adresi!\nSaat {saat}, İmaj FM ile devam ediyoruz.\n[normal] Sevdikleriniz için istek yapabilirsiniz.")
        st.text_input("Açılış anonsu", value="[excitedly] İmaj FM'e hoş geldiniz!", key="ab_open")
        st.text_input("Kapanış anonsu", value="İmaj FM'i dinlediğiniz için teşekkürler.", key="ab_close")
        a3, a4, a5 = st.columns(3)
        a3.checkbox("Şarkı başı/sonu anonsu (şablon)", True, key="ab_tpl")
        a4.checkbox("Mevcut akışa ekle", False, key="ab_append")
        a5.number_input("Karıştırma tohumu (0=rastgele)", 0, 99999, 0, key="ab_seed")
        st.button("🤖 Akışı oluştur", key="ab_go", on_click=pl_autobuild, **UCW, type="primary")
        if st.session_state.get("_ab_msg"):
            st.markdown(f"<div class='card b'>{esc(st.session_state['_ab_msg'])}</div>", unsafe_allow_html=True)

    voice_opts = ["(varsayılan)"] + list(VOICES)
    MODE_IN = {"over": "🎚️ Müziğin üstüne bindir", "seq": "⏮ Şarkıdan önce söyle"}
    MODE_OUT = {"over": "🎚️ Şarkı sonuna bindir", "seq": "⏭ Şarkıdan sonra söyle"}
    if not items:
        st.info("Akış boş. Kütüphaneden ➕ ile şarkı ya da yukarıdan anons bloğu ekleyin.")
    for i, it in enumerate(items):
        uid = it["uid"]
        if it["kind"] == "song":
            s = sbyid.get(it["song"])
            title = f"{i+1}. 🎵 {s['name'] if s else '⚠️ dosya yok'}"
        elif it["kind"] == "ann":
            title = f"{i+1}. 🎙️ {(it['text'][:34] or '(boş anons)')}"
        elif it["kind"] == "clip":
            title = f"{i+1}. 🎧 klip · {it.get('label','')[:34]}"
        else:
            title = f"{i+1}. ⏸ {float(it['sec']):.1f} sn boşluk"
        with st.expander(title, expanded=False):
            m1, m2, m3 = st.columns(3)
            m1.button("⬆️", key=K("up", uid), on_click=pl_move, args=(i, -1), disabled=(i == 0), **UCW)
            m2.button("⬇️", key=K("dn", uid), on_click=pl_move, args=(i, 1), disabled=(i == len(items) - 1), **UCW)
            m3.button("🗑️", key=K("rm", uid), on_click=pl_del, args=(i,), **UCW)
            if it["kind"] == "song":
                it["limit"] = st.number_input("Çalma süresi (sn) · 0 = şarkının tamamı", 0.0, 3600.0, float(it["limit"]), 5.0, key=K("lim", uid))
                it["intro"] = st.text_area("🎙️ Şarkı başı anonsu", value=it["intro"], height=70, key=K("in", uid), placeholder="Şimdi {sarki}...")
                c1, c2 = st.columns(2)
                it["intro_mode"] = c1.selectbox("Başlangıç anonsu", list(MODE_IN), index=list(MODE_IN).index(it["intro_mode"]),
                                                format_func=MODE_IN.get, key=K("inm", uid))
                it["intro_delay"] = c2.number_input("Anons gecikmesi (sn)", 0.0, 60.0, float(it["intro_delay"]), 0.5, key=K("ind", uid))
                it["outro"] = st.text_area("🎙️ Şarkı sonu anonsu", value=it["outro"], height=70, key=K("out", uid), placeholder="{sarki} dinlediniz...")
                it["outro_mode"] = st.selectbox("Bitiş anonsu", list(MODE_OUT), index=list(MODE_OUT).index(it["outro_mode"]),
                                                format_func=MODE_OUT.get, key=K("outm", uid))
                v = st.selectbox("Anons sesi", voice_opts, index=voice_opts.index(it["voice"]) if it["voice"] in VOICES else 0, key=K("v", uid))
                it["voice"] = "" if v == "(varsayılan)" else v
            elif it["kind"] == "ann":
                it["text"] = st.text_area("🎙️ Anons metni", value=it["text"], height=90, key=K("atx", uid),
                                          placeholder="[excitedly] İmaj FM'e hoş geldiniz!  ({saat} {sonraki} kullanılabilir)")
                bopts = ["—"] + [s["id"] for s in songs]
                cur = it["bed"] if it["bed"] in snames else "—"
                bsel = st.selectbox("🎼 Fon müziği (anonsun altında)", bopts, index=bopts.index(cur),
                                    format_func=lambda x: "Yok" if x == "—" else snames[x], key=K("bed", uid))
                it["bed"] = None if bsel == "—" else bsel
                v = st.selectbox("Anons sesi", voice_opts, index=voice_opts.index(it["voice"]) if it["voice"] in VOICES else 0, key=K("av", uid))
                it["voice"] = "" if v == "(varsayılan)" else v
            elif it["kind"] == "clip":
                st.caption(f"Arşiv klibi: {it.get('label','')}")
                e_ = get_entry(it["arch"])
                if e_ is None:
                    st.warning("Arşivde bulunamadı (silinmiş olabilir). Bu öğe atlanır.")
                bopts = ["—"] + [s["id"] for s in songs]
                cur = it["bed"] if it["bed"] in snames else "—"
                bsel = st.selectbox("🎼 Fon müziği", bopts, index=bopts.index(cur),
                                    format_func=lambda x: "Yok" if x == "—" else snames[x], key=K("cbed", uid))
                it["bed"] = None if bsel == "—" else bsel
            else:
                it["sec"] = st.number_input("Boşluk (sn)", 0.0, 120.0, float(it["sec"]), 0.5, key=K("gap", uid))

    # ── AYARLAR ────────────────────────────────────────────────
    with st.expander("⚙️ Yayın Ayarları (ses, geçiş, seviye)", expanded=False):
        mdls = get_models()
        o["voice"] = st.selectbox("Varsayılan anons sesi", list(VOICES), index=list(VOICES).index(o["voice"]) if o["voice"] in VOICES else 0,
                                  format_func=lambda x: f"{VOICES[x][0]} {x} — {VOICES[x][1]}", key=K("o_voice"))
        o["model"] = st.selectbox("Model", list(mdls), index=list(mdls).index(o["model"]) if o["model"] in mdls else 0,
                                  format_func=mdls.get, key=K("o_model"))
        o["style"] = st.text_input("Anons stili (opsiyonel)", value=o["style"], key=K("o_style"), placeholder="Sıcak bir radyo sunucusu gibi oku")
        o["crossfade"] = st.slider("Şarkılar arası geçiş / crossfade (sn)", 0.0, 12.0, float(o["crossfade"]), 0.5, key=K("o_cf"))
        c1, c2 = st.columns(2)
        o["fade_in"] = c1.slider("Şarkı fade-in (sn)", 0.0, 5.0, float(o["fade_in"]), 0.1, key=K("o_fi"))
        o["fade_out"] = c2.slider("Şarkı fade-out (sn)", 0.0, 8.0, float(o["fade_out"]), 0.1, key=K("o_fo"))
        o["duck_db"] = st.slider("Anons sırasında müziği kıs (dB)", 0, 24, int(o["duck_db"]), key=K("o_duck"))
        o["voice_db"] = st.slider("Anons ses seviyesi (dB)", -12.0, 6.0, float(o["voice_db"]), 0.5, key=K("o_vdb"))
        o["outro_end_gap"] = st.slider("Bitiş anonsu şarkı bitmeden kaç sn önce susmalı", 0.0, 10.0, float(o["outro_end_gap"]), 0.5, key=K("o_gap"))
        o["rms_norm"] = st.checkbox("Şarkıları aynı ses seviyesine getir", bool(o["rms_norm"]), key=K("o_rms"))
        o["target_db"] = st.slider("Hedef seviye (dB RMS)", -24.0, -10.0, float(o["target_db"]), 0.5, key=K("o_tgt"))
        st.markdown("<span class='sl2'>▸ ANONS + FON MÜZİĞİ</span>", unsafe_allow_html=True)
        o["bed_level"] = st.slider("Fon müziği seviyesi (tek başınayken, dB)", -20, 0, int(o["bed_level"]), key=K("o_bl"))
        o["bed_duck"] = st.slider("Konuşmada fon müziği kısma (dB)", 0, 24, int(o["bed_duck"]), key=K("o_bd"))
        c3, c4 = st.columns(2)
        o["bed_pre"] = c3.slider("Anons öncesi müzik (sn)", 0.0, 10.0, float(o["bed_pre"]), 0.5, key=K("o_bp"))
        o["bed_post"] = c4.slider("Anons sonrası müzik (sn)", 0.0, 15.0, float(o["bed_post"]), 0.5, key=K("o_bq"))
        st.markdown("<span class='sl2'>▸ ÇIKTI</span>", unsafe_allow_html=True)
        fopts = ["MP3", "WAV"]
        o["fmt"] = st.radio("Biçim", fopts, index=fopts.index(o["fmt"]) if o["fmt"] in fopts else 0, horizontal=True, key=K("o_fmt"))
        o["kbps"] = st.select_slider("MP3 kalitesi (kbps)", [128, 192, 256, 320], value=int(o["kbps"]), key=K("o_kb"))

    with st.expander("💾 Akışları kaydet / yükle", expanded=False):
        sv1, sv2 = st.columns([2, 1])
        sv1.caption("Mevcut akış adıyla kaydedilir; aynı ad üzerine yazar.")
        sv2.button("💾 Kaydet", key="pl_save", on_click=pl_save, **UCW)
        saved = jload("playlists.json", {})
        if saved:
            pick = st.selectbox("Kayıtlı akışlar", list(saved), key="pl_pick")
            l1, l2 = st.columns(2)
            l1.button("📂 Yükle", key="pl_load", on_click=pl_load, args=(pick,), **UCW)
            l2.button("🗑️ Sil", key="pl_forget", on_click=pl_forget, args=(pick,), **UCW)

    # ── 3) ÇIKTI ───────────────────────────────────────────────
    st.markdown("<span class='sl'>▶ 3 · Tam Yayın Çıktısı</span>", unsafe_allow_html=True)
    est, n_ann = 0.0, 0
    for it in items:
        if it["kind"] == "song":
            s = sbyid.get(it["song"])
            if s:
                est += min(s["dur"], float(it["limit"])) if float(it["limit"]) > 0 else s["dur"]
            for k2, md in (("intro", "intro_mode"), ("outro", "outro_mode")):
                if it[k2].strip():
                    n_ann += 1
                    if it[md] == "seq":
                        est += len(it[k2]) / 15 + 0.3
        elif it["kind"] == "ann":
            if it["text"].strip():
                n_ann += 1
                est += len(it["text"]) / 15 + float(o["bed_pre"] + o["bed_post"]) * (1 if it["bed"] else 0)
        elif it["kind"] == "clip":
            e_ = get_entry(it["arch"])
            est += (e_["dur"] if e_ else 0) + (float(o["bed_pre"] + o["bed_post"]) if it["bed"] else 0)
        else:
            est += float(it["sec"])
    _, _, rem = pool_stats()
    warn_q = n_ann > rem
    st.markdown(f"<div class='card {'a' if warn_q else 'b'}'>{len(items)} öğe · tahmini ~{est/60:.1f} dk · "
                f"<b>{n_ann}</b> anons (daha önce üretilenler önbellekten gelir, istek harcamaz) · kalan istek: <b>{rem}</b>"
                f"{'<br>⚠️ Kota yetmeyebilir. Yetmezse üretilenler kalır, kota gelince tekrar basınca kaldığı yerden devam eder.' if warn_q else ''}</div>",
                unsafe_allow_html=True)
    pv1, pv2 = st.columns([2, 1])
    pv_sec = pv2.number_input("Önizleme süresi (sn)", 15, 300, 45, 15, key="pv_sec")
    run_prev = pv1.button("🎧 Önizleme (yalnızca ilk saniyeler)", key="bc_prev", **UCW, disabled=not items)
    run_full = st.button("📻 Tam Yayını Oluştur", type="primary", **UCW, key="bc_go", disabled=not items)
    if run_prev or run_full:
        fmt = "mp3" if o["fmt"] == "MP3" else "wav"
        if fmt == "mp3" and lameenc is None:
            st.error("MP3 çıktı için `pip install lameenc` gerekli (veya biçimi WAV seçin).")
        else:
            bid = hashlib.md5(str(time.time()).encode()).hexdigest()[:10]
            out = BROAD / (f"{bid}.{fmt}" if run_full else f"_preview.{fmt}")
            prog = st.progress(0.0, "Başlıyor…")
            try:
                dur, cues = render_broadcast(items, o, song_bytes, lambda t, v: ann_wav(t, v or o["voice"], o),
                                             snames, out, fmt, lambda f, t: prog.progress(min(max(f, 0.0), 1.0), t),
                                             get_clip=read_audio, max_sec=0 if run_full else pv_sec)
                if run_full:
                    st.session_state._bcs.insert(0, {"id": bid, "name": pl["name"], "fmt": fmt, "dur": round(dur, 1),
                                                     "size": out.stat().st_size, "n": len(items), "cues": cues,
                                                     "ts": datetime.datetime.now().strftime("%d.%m %H:%M")})
                    jsave("broadcasts.json", st.session_state._bcs)
                else:
                    st.session_state["_pv_path"] = str(out)
                st.session_state["_bc_err"] = ""
            except Exception as ex:
                st.session_state["_bc_err"] = str(ex)
            prog.empty()
    if st.session_state.get("_bc_err"):
        st.markdown(f"<div class='card r'>❌ {esc(st.session_state['_bc_err'])}</div>", unsafe_allow_html=True)
    pvp = st.session_state.get("_pv_path")
    if pvp and Path(pvp).exists():
        st.markdown("<div class='card p'>🎧 Önizleme (kayıtlı akışa eklenmez)</div>", unsafe_allow_html=True)
        st.audio(Path(pvp).read_bytes(), format="audio/mpeg" if pvp.endswith("mp3") else "audio/wav")
    for e in st.session_state._bcs[:3]:
        f = BROAD / f"{e['id']}.{e['fmt']}"
        if not f.exists():
            continue
        st.markdown(f"<div class='card g'>✅ <b>{esc(e['name'])}</b> · {e['ts']} · {e['dur']/60:.1f} dk · {e['n']} öğe · {e['size']//1024} KB · {e['fmt'].upper()}</div>", unsafe_allow_html=True)
        data = f.read_bytes()
        st.audio(data, format="audio/mpeg" if e["fmt"] == "mp3" else "audio/wav")
        d1, d2 = st.columns([3, 1])
        d1.download_button(f"💾 İndir ({e['fmt'].upper()})", data, file_name=f"{slug(e['name'])}_{e['id']}.{e['fmt']}",
                           mime="audio/mpeg" if e["fmt"] == "mp3" else "audio/wav", **UCW, key=f"bcdl_{e['id']}")
        d2.button("🗑️", key=f"bcdel_{e['id']}", on_click=bc_delete, args=(e["id"],), **UCW)
        cues_ = e.get("cues", [])
        if cues_:
            with st.expander("📋 Yayın akış listesi (zaman damgalı)", expanded=False):
                st.dataframe([{"Zaman": fmt_t(c["t"]), "Tür": KIND_TR.get(c["kind"], c["kind"]), "Ad": c["name"]} for c in cues_],
                             **UCW, hide_index=True)
                x1, x2 = st.columns(2)
                x1.download_button("📄 TXT", cue_text(cues_, e["name"]), file_name=f"akis_{e['id']}.txt", mime="text/plain",
                                   **UCW, key=f"cuet_{e['id']}")
                x2.download_button("📊 CSV", cue_csv(cues_), file_name=f"akis_{e['id']}.csv", mime="text/csv",
                                   **UCW, key=f"cuec_{e['id']}")

    js = json.dumps(pl, sort_keys=True, ensure_ascii=False)
    if js != st.session_state.get("_pl_saved"):
        jsave("playlist_current.json", pl)
        st.session_state["_pl_saved"] = js


# ══════════════════════════════════════════════════════════════════
# TAB 7 — ANONS YAZARI (yapay zekâ)
# ══════════════════════════════════════════════════════════════════
with t7:
    st.markdown("<div class='card b'><b>✍️ Anons Yazarı</b> — Konuyu yazın, yapay zekâ radyo anonsu varyasyonları üretsin (isteğe bağlı duygu etiketleriyle). Beğendiğinizi tek tıkla seslendirmeye, yayın akışına veya favorilere gönderin. <i>Her üretim 1 API isteği harcar.</i></div>", unsafe_allow_html=True)
    st.text_area("Konu / brief", height=110, key="gen_brief",
                 placeholder="Örn: Cumartesi akşamı 21:00'de Kadıköy'de ücretsiz açık hava konseri var, konuk sanatçı sürpriz...")
    g1, g2, g3 = st.columns(3)
    g1.selectbox("Ton", ["Neşeli & enerjik", "Samimi & sıcak", "Resmi & haber", "Dramatik", "Mizahi", "Sakin & gece kuşağı"], key="gen_tone")
    g2.selectbox("Uzunluk", ["Çok kısa (1 cümle)", "Kısa (2-3 cümle)", "Orta (4-6 cümle)"], index=1, key="gen_len")
    g3.slider("Varyasyon sayısı", 1, 5, 3, key="gen_n")
    gt1, gt2 = st.columns([1, 2])
    gt1.checkbox("Duygu etiketleri ekle", True, key="gen_tags")
    gt2.text_input("Metin modeli (boş = otomatik)", "", key="gen_model", placeholder="örn. gemini-3.8-flash")
    if st.button("✨ Metin Üret", type="primary", **UCW, key="gen_go"):
        brief = st.session_state.get("gen_brief", "").strip()
        if not brief:
            st.warning("⚠️ Konu boş.")
        else:
            tag_rule = ("Metnin uygun yerlerine yalnızca şu köşeli duygu etiketlerini koy: [excitedly] [whispers] [laughs] [seriously] [shouting] [sighs] [normal]. Etiket uydurma."
                        if st.session_state.gen_tags else "Köşeli etiket veya sahne yönergesi kullanma.")
            prompt = (f"Sen deneyimli bir radyo metin yazarısın. İmaj FM için Türkçe radyo anonsu yaz.\n"
                      f"Konu: {brief}\nTon: {st.session_state.gen_tone}\nUzunluk: {st.session_state.gen_len}\n{tag_rule}\n"
                      f"{st.session_state.gen_n} farklı varyasyon yaz. Varyasyonları yalnızca tek satırlık '---' ile ayır. "
                      f"Numara, başlık, açıklama, tırnak işareti yazma; sadece sunucunun okuyacağı metni ver. "
                      f"Saat gerekiyorsa {{saat}} yer tutucusunu aynen kullan.")
            with st.spinner("✍️ Yazılıyor…"):
                try:
                    txt, used_model = run_text(prompt, st.session_state.gen_model)
                    parts = [p.strip() for p in re.split(r"\n\s*---+\s*\n|^\s*---+\s*$", txt, flags=re.M) if p.strip()]
                    st.session_state["_gen"] = parts[: int(st.session_state.gen_n)]
                    st.session_state["_gen_ver"] = st.session_state.get("_gen_ver", 0) + 1
                    st.session_state["_gen_msg"] = f"Model: {used_model}"
                except Exception as ex:
                    st.session_state["_gen"] = []
                    st.session_state["_gen_msg"] = f"❌ {ex}"
    if st.session_state.get("_gen_msg"):
        st.caption(st.session_state["_gen_msg"])
    gv = st.session_state.get("_gen_ver", 0)
    for gi, gtxt in enumerate(st.session_state.get("_gen", [])):
        gk = f"gen_{gv}_{gi}"
        st.text_area(f"Varyasyon {gi+1}", value=gtxt, height=120, key=gk)
        b1, b2, b3 = st.columns(3)
        b1.button("🎤 Tek'e gönder", key=f"{gk}_a", on_click=copy_state, args=(gk, "txt_tek"), **UCW)
        b2.button("📻 Akışa anons", key=f"{gk}_b", on_click=ann_from_state, args=(gk,), **UCW)
        b3.button("⭐ Favori", key=f"{gk}_c", on_click=fav_from_state, args=(gk,), **UCW)


# ══════════════════════════════════════════════════════════════════
# TAB 6 — SES KÜTÜPHANESİ
# ══════════════════════════════════════════════════════════════════
with t8:
    st.markdown("<div class='card b'>Her ses için örnek bir kez üretilir ve diskte saklanır (ikinci kez istek harcamaz). Beğendiğinizi <b>Kullan</b> ile Tek sekmesine atayın.</div>", unsafe_allow_html=True)
    lc1, lc2 = st.columns([2, 1])
    lib_txt = lc1.text_input("Örnek metin", "İmaj FM'e hoş geldiniz, güzel bir gün dilerim.", key="lib_txt")
    with lc2:
        lib_m, lib_l = pick_model_lang("lib")
    lib_g = st.radio("Filtre", ["Tümü", "♀ Kadın", "♂ Erkek"], horizontal=True, key="lib_g", label_visibility="collapsed")
    items = [(v, d) for v, d in VOICES.items() if lib_g == "Tümü" or d[0] == lib_g[0]]
    gc = st.columns(3)
    for i, (v, (gd, desc)) in enumerate(items):
        h = hashlib.md5(f"{v}|{lib_m}|{lib_l}|{lib_txt}".encode()).hexdigest()[:12]
        f = PREV / f"{h}.wav"
        with gc[i % 3]:
            st.markdown(f"<div class='arc-card'><div class='arc-meta'><span class='arc-voice'>{gd} {v}</span></div><div class='arc-info'>{esc(desc)}</div></div>", unsafe_allow_html=True)
            if f.exists():
                st.audio(f.read_bytes(), format="audio/wav")
            else:
                if st.button("▶ Dinle (1 istek)", key=f"lib_{v}", **UCW):
                    with st.spinner(f"{v}…"):
                        try:
                            w, _ = synthesize(lib_txt, v, lib_m, lib_l, "")
                            f.write_bytes(w)
                            st.rerun()
                        except Exception as ex:
                            st.error(f"❌ {ex}")
            st.button("✔ Kullan", key=f"use_{v}", **UCW, on_click=use_voice, args=(v,))

# ══════════════════════════════════════════════════════════════════
# TAB 7 — FAVORİLER
# ══════════════════════════════════════════════════════════════════
with t9:
    favs = st.session_state._favs
    if not favs:
        st.markdown("<div style='text-align:center;padding:50px;color:var(--muted);'><div style='font-size:2rem;'>⭐</div>Favori yok. Tek sekmesinden veya Arşiv'den ekleyin.</div>", unsafe_allow_html=True)
    else:
        for fi, fv in enumerate(favs):
            f1, f2, f3, f4 = st.columns([2.2, .9, .9, .5])
            f1.markdown(f"<div class='fav-card'><div class='fav-name'>⭐ {esc(fv['name'])}</div><div class='fav-prev'>{esc(fv.get('voice','—'))} · {esc(fv.get('lang','—'))}</div><div class='fav-prev'>{esc(fv['text'][:80])}</div></div>", unsafe_allow_html=True)
            f2.button("📋 Yükle", key=f"fcp_{fi}", **UCW, help="Tek sekmesine yükle", on_click=load_fav, args=(fi,))
            if f3.button("🔴 Seslendir", key=f"fsp_{fi}", **UCW):
                with st.spinner("Üretiliyor…"):
                    try:
                        e = produce(fv["text"], fv.get("voice", "Kore"), fv.get("model") or "gemini-3.8-flash-lite-tts",
                                    fv.get("lang") or "tr-TR", "", "fav")
                        st.session_state._last[f"fav{fi}"] = [e["id"]]
                    except Exception as ex:
                        st.error(f"❌ {ex}")
            f4.button("🗑️", key=f"fdel_{fi}", **UCW, on_click=del_fav, args=(fi,))
            render_last(f"fav{fi}", wave=False)

# ══════════════════════════════════════════════════════════════════
# TAB 8 — ARŞİV
# ══════════════════════════════════════════════════════════════════
with t10:
    arc = st.session_state._arc
    s1, s2, s3, s4, s5 = st.columns(5)
    tot_mb = sum(e["size"] for e in arc) / (1024 * 1024)
    for colx, (val, lbl, cl) in zip((s1, s2, s3, s4, s5), [
            (len(arc), "Kayıt", "b"), (stt["calls"], "API Çağrısı", "g"), (f"{stt['secs']:.0f}s", "Üretilen Ses", "a"),
            (f"{stt['chars']:,}", "Karakter", "p"), (f"{tot_mb:.1f}MB", "Arşiv Boyutu", "")]):
        colx.markdown(f'<div class="mbox {cl}"><div class="v">{val}</div><div class="l">{lbl}</div></div>', unsafe_allow_html=True)
    with st.expander("📈 Son 14 gün API isteği", expanded=False):
        dly = stt.get("daily", {})
        days = [(datetime.date.today() - datetime.timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
        try:
            import pandas as pd
            st.bar_chart(pd.DataFrame({"İstek": [dly.get(d, 0) for d in days]}, index=[d[5:] for d in days]))
        except Exception:
            st.caption(" · ".join(f"{d[5:]}: {dly.get(d, 0)}" for d in days))
    st.markdown("<br>", unsafe_allow_html=True)
    if not arc:
        st.markdown("<div style='text-align:center;padding:50px;color:var(--muted);'><div style='font-size:2rem;'>📂</div>Arşiv boş. Üretimler diske kaydedilir; sayfa yenilense de kalır.</div>", unsafe_allow_html=True)
    else:
        af1, af2 = st.columns([2, 1])
        q = af1.text_input("Ara", placeholder="🔍 Ses, metin veya model ara…", label_visibility="collapsed", key="arc_q").lower().strip()
        md = af2.selectbox("Mod", ["Tümü", "tek", "cift", "split", "bulk", "ab-A", "ab-B", "fav", "montaj"], label_visibility="collapsed", key="arc_mode")
        fl = [e for e in arc if (not q or q in e["voice"].lower() or q in e["text"].lower() or q in e["model"].lower())
              and (md == "Tümü" or e.get("mode") == md)]
        PER = 12
        pages = max(1, (len(fl) + PER - 1) // PER)
        pg = st.number_input("Sayfa", 1, pages, 1, key="arc_pg") if pages > 1 else 1
        h1, h2, h3 = st.columns([2, 1, 1])
        h1.markdown(f"<span class='sl'>▶ {len(fl)} kayıt</span>", unsafe_allow_html=True)
        h2.download_button("📦 Filtreyi ZIP", zip_entries(fl, lambda i, e: f"{i:03d}_{slug(e['voice'])}_{e['id']}.wav") if len(fl) <= 40 else b"",
                           file_name="imajfm_arsiv.zip", mime="application/zip", **UCW,
                           key="arc_zip", disabled=len(fl) > 40 or not fl, help="En fazla 40 kayıt")
        if h3.button("🗑️ Tümünü Sil", **UCW, key="arc_clr"):
            st.session_state["_confirm_clr"] = True
        if st.session_state.get("_confirm_clr"):
            st.warning("Tüm arşiv diskten silinecek.")
            y, n = st.columns(2)
            if y.button("Evet, sil", key="clr_y", type="primary"):
                archive_clear(); st.session_state["_confirm_clr"] = False; st.rerun()
            if n.button("Vazgeç", key="clr_n"):
                st.session_state["_confirm_clr"] = False; st.rerun()
        colors = {"tek": "#3b82f6", "cift": "#a78bfa", "split": "#f59e0b", "bulk": "#22c55e",
                  "ab-A": "#a78bfa", "ab-B": "#fb923c", "fav": "#fbbf24", "montaj": "#ec4899"}
        gcols = st.columns(3)
        for gi, e in enumerate(fl[(pg - 1) * PER: pg * PER]):
            with gcols[gi % 3]:
                mc = colors.get(e.get("mode", "tek"), "#3b82f6")
                st.markdown(f"""<div class='arc-card'><div class='arc-meta'><span class='arc-voice'>{vicon(e['voice'])} {esc(e['voice'])}</span><span class='arc-ts'>{e['ts_short']}</span></div>
                <div class='arc-info'><span style='color:{mc};background:{mc}18;border-radius:4px;padding:1px 6px;font-size:.62rem;font-weight:700;'>{esc(e.get('mode','tek')).upper()}</span> {esc(e['model_short'])} · {esc(e['lang'])} · {e['dur']}s · {e['size']//1024}KB</div>
                <div class='arc-text'>{esc(e['preview'])}</div></div>""", unsafe_allow_html=True)
                w = read_audio(e["id"])
                if w is None:
                    st.caption("⚠️ dosya yok"); continue
                st.audio(w, format="audio/wav")
                d1, d2, d3, d4 = st.columns(4)
                d1.download_button("💾", w, file_name=f"imajfm_{slug(e['voice'])}_{e['id']}.wav", mime="audio/wav",
                                   **UCW, key=f"adl_{e['id']}", help="WAV indir")
                d2.button("⭐", key=f"afav_{e['id']}", **UCW, help="Favorilere ekle",
                          on_click=add_fav, args=(f"{e['voice']} {e['ts_short']}", e["text"], e["voice"], e["model"], e["lang"]))
                d3.button("📝", key=f"atxt_{e['id']}", **UCW, help="Metni Tek sekmesine yükle",
                          on_click=set_text, args=("txt_tek", e["text"]))
                d4.button("🗑️", key=f"adel_{e['id']}", **UCW, help="Sil",
                          on_click=archive_delete, args=(e["id"],))

st.markdown("<hr><div style='text-align:center;color:var(--muted);font-size:.65rem;letter-spacing:.1em;padding:5px 0 12px;'>İMAJ FM TTS STÜDYO v6 · Google Gemini TTS API · 2026</div>", unsafe_allow_html=True)
