import streamlit as st
from groq import Groq
import re, base64, json, time, random, hashlib

# ═══════════════════════════════════════════════════════════════
# 1. SAYFA AYARLARI
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="K3N4N VOICE v31",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# 2. CSS + JS — TAM MOTOR
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Nabla&family=Bungee+Spice&family=Bungee+Shade&family=Rubik+Glitch&family=Rubik+Mono+One&family=Faster+One&family=Righteous&family=Nosifer&family=Creepster&family=Pacifico&family=Monoton&family=Press+Start+2P&family=VT323&family=Audiowide&family=Rajdhani:wght@400;700&family=Turret+Road:wght@800&family=Black+Ops+One&family=Alfa+Slab+One&family=Russo+One&family=Bebas+Neue&family=Permanent+Marker&family=Satisfy&family=Lobster&family=Exo+2:wght@900&family=Bangers&family=Lilita+One&family=Fredoka+One&family=Titan+One&family=Squada+One&display=swap');

:root {
  --bg:#020205; --surface:#0b0b16; --surface2:#111122;
  --border:#1e1e3a; --border2:#2a2a55;
  --a1:#ff00cc; --a2:#3333ff; --a3:#00ffcc; --a4:#ffcc00; --a5:#ff6600;
  --text:#dde0ff; --muted:#55557a; --danger:#ff3355;
  --success:#00ff88; --warn:#ffaa00;
}
*,*::before,*::after{box-sizing:border-box;}
html{scroll-behavior:smooth;}
.stApp{background:var(--bg)!important;color:var(--text);}
.stApp>header{background:transparent!important;}
section[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}

/* ── Butonlar ── */
.stButton>button{
  background:linear-gradient(135deg,var(--a2),var(--a1))!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-family:'Orbitron',sans-serif!important;font-weight:700!important;
  letter-spacing:.8px;transition:all .2s!important;
}
.stButton>button:hover{filter:brightness(1.25)!important;transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(100,0,255,.4)!important;}
.stFormSubmitButton>button{
  background:linear-gradient(135deg,#ff5500,#ff0033)!important;
  font-size:1.05rem!important;border-radius:14px!important;
  font-family:'Orbitron',sans-serif!important;
  box-shadow:0 0 35px rgba(255,60,0,.55)!important;width:100%!important;
  padding:15px!important;letter-spacing:1.5px!important;
}

/* ── Input ── */
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{
  background:var(--surface2)!important;border:1px solid var(--border2)!important;
  color:var(--text)!important;border-radius:10px!important;
  font-family:'Rajdhani',sans-serif!important;font-size:1rem!important;
}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{
  border-color:var(--a1)!important;box-shadow:0 0 14px rgba(255,0,204,.35)!important;
}
.stSelectbox>div>div{background:var(--surface2)!important;border:1px solid var(--border2)!important;color:var(--text)!important;border-radius:10px!important;}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:12px;padding:5px;border:1px solid var(--border);}
.stTabs [data-baseweb="tab"]{color:var(--muted)!important;font-family:'Orbitron',sans-serif!important;font-size:.72rem!important;padding:8px 14px!important;}
.stTabs [aria-selected="true"]{background:var(--a2)!important;color:#fff!important;border-radius:8px!important;}
hr{border-color:var(--border)!important;}
.stCodeBlock{border-radius:12px!important;border:1px solid var(--border)!important;}
[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:12px 16px;}
[data-testid="stMetricValue"]{color:var(--a3)!important;font-family:'Orbitron',sans-serif!important;}
[data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:12px!important;}

/* ── Başlık ── */
.omega-title{
  text-align:center;font-family:'Orbitron',sans-serif;
  font-size:clamp(2rem,4.5vw,3.2rem);font-weight:900;
  background:linear-gradient(90deg,#ff00cc,#3333ff,#00ffcc,#ffcc00,#ff6600,#ff00cc);
  background-size:400% 400%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:gShift 5s ease infinite;margin-bottom:2px;
}
.omega-sub{text-align:center;font-family:'Rajdhani',sans-serif;color:var(--muted);letter-spacing:5px;font-size:.85rem;margin-bottom:24px;}
@keyframes gShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}

/* ── Mikrofon ── */
.mic-wrap{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:22px 28px;text-align:center;margin-bottom:18px;position:relative;overflow:hidden;}
.mic-wrap::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at 50% 0%,rgba(255,0,100,.08),transparent 70%);pointer-events:none;}
.mic-btn{background:linear-gradient(135deg,#bb0000,#ff2200);color:#fff;border:none;border-radius:50px;padding:16px 40px;font-size:1.1rem;font-weight:700;font-family:'Orbitron',sans-serif;cursor:pointer;box-shadow:0 0 25px rgba(255,30,0,.45);transition:all .3s;letter-spacing:1px;}
.mic-btn:hover{box-shadow:0 0 55px rgba(255,30,0,.8);transform:scale(1.05);}
.mic-btn.listening{animation:micPulse 1s ease-in-out infinite;background:#ff0000!important;}
@keyframes micPulse{0%,100%{box-shadow:0 0 20px #ff0000}50%{box-shadow:0 0 70px #ff0000,0 0 120px #ff6600}}

/* ── Renk chip ── */
.chip{display:inline-block;width:26px;height:26px;border-radius:50%;border:2px solid #333;margin:3px;vertical-align:middle;transition:transform .2s;cursor:pointer;}
.chip:hover{transform:scale(1.35);}

/* ── Skor / rating ── */
.star-row{font-size:1.4rem;cursor:pointer;letter-spacing:4px;}
.ai-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(50,50,200,.2);border:1px solid var(--a2);border-radius:20px;padding:4px 12px;font-family:'Orbitron',sans-serif;font-size:.68rem;color:var(--a3);}
.tag-pill{display:inline-block;background:rgba(255,0,204,.12);border:1px solid var(--a1);border-radius:20px;padding:3px 10px;font-size:.72rem;margin:3px;font-family:'Rajdhani',sans-serif;color:var(--a1);}

/* ── Prompt builder ── */
.prompt-token{display:inline-block;background:var(--surface2);border:1px solid var(--border2);border-radius:8px;padding:5px 10px;margin:4px;font-size:.8rem;cursor:pointer;transition:all .2s;font-family:'Rajdhani',sans-serif;}
.prompt-token:hover{border-color:var(--a3);color:var(--a3);}
.prompt-token.active{background:rgba(0,255,200,.15);border-color:var(--a3);color:var(--a3);}

/* ── Comparison ── */
.compare-frame{border:2px solid var(--border2);border-radius:14px;overflow:hidden;position:relative;}
.compare-label{position:absolute;top:8px;left:8px;z-index:10;background:rgba(0,0,0,.7);color:#fff;padding:4px 10px;border-radius:6px;font-family:'Orbitron',sans-serif;font-size:.65rem;}

/* ── Toast-like ── */
.info-bar{background:linear-gradient(90deg,rgba(51,51,255,.2),rgba(255,0,204,.2));border:1px solid var(--border2);border-radius:10px;padding:10px 16px;margin:8px 0;font-family:'Rajdhani',sans-serif;font-size:.9rem;}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--a2);border-radius:3px;}

/* ── Progress bar ── */
.gen-progress{height:4px;background:linear-gradient(90deg,var(--a2),var(--a1),var(--a3));border-radius:2px;animation:progressAnim 1.5s ease-in-out infinite;margin-bottom:10px;}
@keyframes progressAnim{0%{opacity:1}50%{opacity:.4}100%{opacity:1}}

/* ── CSS var editör ── */
.css-var-row{display:flex;align-items:center;gap:8px;margin-bottom:6px;font-family:'Rajdhani',sans-serif;font-size:.9rem;}
</style>

<script>
// ── Ses Motoru ────────────────────────────────────────────────
function startVoice(lang, targetId) {
  const SRC = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SRC) { alert("Chrome tarayıcısı gerekli (Web Speech API)."); return; }
  const r = new SRC();
  r.lang = lang; r.interimResults = false; r.maxAlternatives = 3;
  const btn = document.getElementById('micBtn');
  btn.textContent = "🔴 DİNLİYORUM…";
  btn.classList.add('listening');

  r.onresult = e => {
    const txt = e.results[0][0].transcript;
    const conf = Math.round(e.results[0][0].confidence * 100);
    const doc = window.parent.document;
    doc.querySelectorAll('textarea').forEach(a => {
      Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set.call(a, txt);
      a.dispatchEvent(new Event('input',{bubbles:true}));
      a.dispatchEvent(new Event('change',{bubbles:true}));
    });
    btn.textContent = `✅ %${conf} — ${txt.substring(0,28)}${txt.length>28?'…':''}`;
    btn.classList.remove('listening');
    setTimeout(()=>{ btn.textContent = "🎤 SESLİ KOMUT VER"; }, 3500);
  };
  r.onerror = e => {
    btn.textContent = "⚠️ HATA: " + e.error.toUpperCase();
    btn.classList.remove('listening');
    if (e.error === 'not-allowed') alert("Mikrofon izni ver: adres çubuğu > kilit simgesi > izinler");
  };
  r.onend = () => btn.classList.remove('listening');
  r.start();
}

// ── Text-to-Speech ───────────────────────────────────────────
function speakText(text, lang) {
  if (!window.speechSynthesis) { alert("TTS desteklenmiyor."); return; }
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang; u.rate = 0.95; u.pitch = 1.1; u.volume = 1;
  window.speechSynthesis.speak(u);
}

// ── Önizleme snapshot (CSS filter) ──────────────────────────
function applyFilter(iframeId, filter) {
  const f = document.getElementById(iframeId);
  if (f) { f.style.filter = filter; f.style.transition = 'filter .4s'; }
}

// ── Prompt token toggle ──────────────────────────────────────
function toggleToken(el, text) {
  el.classList.toggle('active');
  const doc = window.parent.document;
  const areas = doc.querySelectorAll('textarea');
  areas.forEach(a => {
    let cur = a.value;
    if (el.classList.contains('active')) {
      a.value = cur ? cur + ', ' + text : text;
    } else {
      a.value = cur.replace(', ' + text, '').replace(text + ', ', '').replace(text, '').trim();
    }
    Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set.call(a, a.value);
    a.dispatchEvent(new Event('input',{bubbles:true}));
    a.dispatchEvent(new Event('change',{bubbles:true}));
  });
}

// ── Renk paleti kopyala ─────────────────────────────────────
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(()=>{ 
    const t = document.createElement('div');
    t.style.cssText='position:fixed;top:20px;right:20px;background:#00ff88;color:#000;padding:10px 20px;border-radius:8px;font-weight:700;z-index:9999;font-family:Orbitron,sans-serif;font-size:.8rem;';
    t.textContent='✅ Kopyalandı!';
    document.body.appendChild(t);
    setTimeout(()=>t.remove(), 2000);
  });
}
</script>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 3. VERİ KÜTÜPHANELERİ
# ═══════════════════════════════════════════════════════════════
FONTS = {
    # ── Efekt ──
    "🌈 Nabla":            "Nabla",
    "🔥 Bungee Spice":     "Bungee Spice",
    "👤 Bungee Shade":     "Bungee Shade",
    "💀 Nosifer":          "Nosifer",
    "😱 Creepster":        "Creepster",
    "🌀 Rubik Glitch":     "Rubik Glitch",
    # ── Geometrik ──
    "🚀 Orbitron":         "Orbitron",
    "⚡ Turret Road":      "Turret Road",
    "🎯 Audiowide":        "Audiowide",
    "🔮 Monoton":          "Monoton",
    "🕹️ Press Start 2P":   "Press Start 2P",
    "📺 VT323":            "VT323",
    "🏁 Black Ops One":    "Black Ops One",
    "🛸 Russo One":        "Russo One",
    "⚙️ Rajdhani":         "Rajdhani",
    "🤖 Rubik Mono One":   "Rubik Mono One",
    "📐 Exo 2":            "Exo 2",
    "🎪 Bangers":          "Bangers",
    "🔲 Squada One":       "Squada One",
    "🟦 Bebas Neue":       "Bebas Neue",
    # ── Script / Dekoratif ──
    "✍️ Pacifico":         "Pacifico",
    "⚡ Faster One":       "Faster One",
    "🎸 Righteous":        "Righteous",
    "🅰️ Alfa Slab One":    "Alfa Slab One",
    "🖊️ Permanent Marker": "Permanent Marker",
    "🌸 Satisfy":          "Satisfy",
    "🦞 Lobster":          "Lobster",
    "🧡 Fredoka One":      "Fredoka One",
    "🔴 Titan One":        "Titan One",
    "🔵 Lilita One":       "Lilita One",
}

COLOR_PALETTES = {
    "🔥 Ateş":      ["#ff0000","#ff6600","#ffcc00","#ff3300","#ff9900"],
    "💎 Elmas":     ["#00ccff","#0066ff","#aa00ff","#ffffff","#aaddff"],
    "🌿 Matrix":    ["#00ff41","#003300","#00cc33","#00ff99","#001100"],
    "🌅 Gün Batımı":["#ff6b6b","#feca57","#ff9ff3","#54a0ff","#5f27cd"],
    "🪙 Gold":      ["#ffd700","#ffaa00","#cc8800","#fff5cc","#b8860b"],
    "🌙 Gece":      ["#4834d4","#686de0","#30336b","#c7ecee","#130f40"],
    "⚡ Neon":      ["#ff00ff","#00ffff","#ff0099","#00ff66","#ffff00"],
    "🎨 Pastel":    ["#a29bfe","#fd79a8","#fdcb6e","#55efc4","#74b9ff"],
    "🖤 Monokom":   ["#ffffff","#cccccc","#888888","#444444","#000000"],
    "🌺 Tropik":    ["#ff4757","#ffa502","#2ed573","#1e90ff","#ff6b81"],
    "🧊 Buz":       ["#d6eaf8","#85c1e9","#2980b9","#1a5276","#aed6f1"],
    "🍇 Mor Rüya":  ["#8e44ad","#9b59b6","#d2b4de","#f8f9f9","#4a235a"],
}

EFFECT_PRESETS = [
    {"e":"✨ Altın Işıltı",   "d":"gold metallic gradient, shimmer animation, sparkle particles, drop shadow"},
    {"e":"🌊 Okyanus",        "d":"deep blue to cyan gradient, wave animation, water bubble particles"},
    {"e":"🔥 Alevler",        "d":"red orange yellow fire gradient, flame keyframe animation, ember sparks"},
    {"e":"💜 Hologram",       "d":"purple pink holographic foil, rainbow scanline overlay, glitch flicker"},
    {"e":"🌈 Krom",           "d":"chrome mirror metallic, rainbow reflection, beveled 3D text, glossy finish"},
    {"e":"⚡ Elektrik",       "d":"neon blue lightning arc, electric plasma glow, energy field animation"},
    {"e":"🎮 8-Bit Piksel",   "d":"pixel art retro style, 8-bit blocky shadow, CRT scanlines effect"},
    {"e":"🌸 Sakura",         "d":"pink cherry blossom gradient, petal fall animation, dreamy soft glow"},
    {"e":"🤖 Cyberpunk",      "d":"neon yellow green on dark, glitch shift animation, circuit board texture"},
    {"e":"💎 Kristal",        "d":"ice crystal transparent, refraction rainbow light, diamond sparkle"},
    {"e":"🌋 Magma",          "d":"dark red molten lava, cracked earth texture, glowing orange veins"},
    {"e":"🌌 Galaksi",        "d":"deep space starfield, milky way gradient, nebula glow, star particles"},
    {"e":"🐉 Ejderha",        "d":"dark fantasy dragon scales texture, red fire breath glow, epic shadow"},
    {"e":"🎆 Havai Fişek",    "d":"colorful firework explosion burst, sparkle trails, festive glow"},
    {"e":"🧬 DNA Helix",      "d":"green biohazard glow, helix particle animation, lab scanner beam"},
    {"e":"🏆 Altın Kupa",     "d":"3D gold trophy emboss, luxury serif, radiant sunburst rays"},
    {"e":"❄️ Buz Kristali",   "d":"frozen ice texture, snowflake geometry, cold blue white shimmer"},
    {"e":"🎸 Rock Metal",     "d":"dark brushed steel, lightning bolt, distressed grunge texture, heavy shadow"},
    {"e":"🌈 Neon Rainbow",   "d":"full spectrum neon rainbow gradient cycling, glow bloom, vivid saturation"},
    {"e":"🔮 Mistik",         "d":"deep purple magic rune glow, ethereal mist particles, arcane aura"},
]

ANIM_TYPES = [
    "Yok", "Soluk alma (pulse)", "Titreme (shake/vibrate)",
    "Döngüsel renk (hue-rotate)", "Soldan sağa kayma (slide-in)",
    "Zoom in/out (scale pulse)", "Sallanma (swing)", "Float (yukarı-aşağı)",
    "Parlama tarama (light-sweep)", "Glitch kayması", "Bounce (zıplama)",
    "Flip 3D (Y ekseni)", "Wave (harf harf dalga)", "Typewriter yazı",
]

TEXT_EFFECTS = [
    "Normal", "3D Kabartma (emboss)", "Neon Glow (tek renk)",
    "Çift Neon Glow (2 renk)", "Outline kontur", "Çift outline",
    "Drop Shadow katmanlı", "İç gölge (inset)", "Text-stroke rainbow",
    "Hologram tarama", "Degrade dolgu (gradient fill)", "Smokey blur",
    "Metalik parlaklık", "Glitch shift (kırmızı-mavi)", "3D perspektif",
]

QUICK_TOKENS = [
    "gold sparkle", "neon glow", "fire flames", "ice crystal", "rainbow gradient",
    "holographic foil", "chrome metallic", "glitch effect", "star particles",
    "smoke haze", "3D emboss", "watercolor splash", "laser beam", "plasma energy",
    "galaxy stars", "lava texture", "diamond shine", "electric arc", "cherry blossom",
    "cyberpunk neon", "pixel art", "grunge texture", "bokeh lights", "aurora glow",
]

STYLE_CATEGORIES = {
    "🎮 Gaming":     "epic gaming style, esports logo feel, intense dramatic lighting, dark background",
    "💅 Luxury":     "premium luxury brand, gold serif, elegant minimalist, sophisticated shadow",
    "🎨 Artistic":   "abstract expressionist, paint strokes, canvas texture, bold brushwork",
    "🤖 Sci-Fi":     "futuristic sci-fi HUD, holographic data overlay, techy grid lines",
    "🌊 Nature":     "organic flowing shapes, natural earth tones, botanical elements",
    "🎃 Horror":     "creepy dark gothic, dripping text, horror movie poster style",
    "🎉 Festive":    "party celebration confetti, bright festive colors, joyful bouncy",
    "🏛️ Classic":    "timeless classical serif, old world engraving, vintage letterpress",
    "🌸 Kawaii":     "cute japanese kawaii style, pastel bubble letters, sweet sparkles",
    "💢 Anime":      "anime manga bold title, speed lines, action energy burst",
}

VOICE_LANGS = {
    "🇹🇷 Türkçe":    "tr-TR",
    "🇺🇸 İngilizce": "en-US",
    "🇩🇪 Almanca":   "de-DE",
    "🇫🇷 Fransızca": "fr-FR",
    "🇪🇸 İspanyolca":"es-ES",
    "🇯🇵 Japonca":   "ja-JP",
    "🇰🇷 Korece":    "ko-KR",
    "🇦🇪 Arapça":    "ar-SA",
}

GROQ_MODELS = {
    "llama-3.3-70b-versatile":  "⚡ Llama 3.3 70B (Güçlü)",
    "llama-3.1-8b-instant":     "🚀 Llama 3.1 8B (Hızlı)",
    "mixtral-8x7b-32768":       "🌀 Mixtral 8x7B (Çok yönlü)",
    "gemma2-9b-it":             "💎 Gemma2 9B (Google)",
}

# ═══════════════════════════════════════════════════════════════
# 4. SESSION STATE
# ═══════════════════════════════════════════════════════════════
DEFAULTS = {
    "history": [], "favorites": [], "current_html": "",
    "current_entry": {}, "generation_count": 0,
    "ratings": {},        # hash -> int(1-5)
    "tags": {},           # hash -> [str]
    "compare_a": None, "compare_b": None,
    "prompt_tokens": [],  # seçili hızlı tokenler
    "live_css_vars": {},  # custom CSS variable overrides
    "batch_results": [],  # toplu üretim sonuçları
    "ai_suggest_prompt": "",
    "code_edit_mode": False,
    "manual_html": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def html_hash(html): return hashlib.md5(html.encode()).hexdigest()[:8]

# ═══════════════════════════════════════════════════════════════
# 5. API
# ═══════════════════════════════════════════════════════════════
api_key = None
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]

# ═══════════════════════════════════════════════════════════════
# 6. SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<p style='font-family:Orbitron;font-size:1rem;color:var(--a1);font-weight:900;margin:0 0 14px;'>⚙️ KONTROL PANELİ</p>", unsafe_allow_html=True)

    if not api_key:
        api_key = st.text_input("🔑 Groq API Key:", type="password", help="groq.com'dan ücretsiz alın")

    st.markdown("**🤖 AI Modeli**")
    model_label = st.selectbox("", list(GROQ_MODELS.values()), label_visibility="collapsed")
    model_choice = [k for k, v in GROQ_MODELS.items() if v == model_label][0]

    st.markdown("**🌐 Ses Dili**")
    vlang_label = st.selectbox("", list(VOICE_LANGS.keys()), label_visibility="collapsed")
    vlang_code  = VOICE_LANGS[vlang_label]

    st.divider()
    st.markdown("**🎛️ Üretim Parametreleri**")
    temperature = st.slider("Yaratıcılık", 0.0, 1.5, 0.95, 0.05,
                            help="Yüksek = daha deneysel, düşük = daha tutarlı")
    max_tokens  = st.slider("Max Token", 512, 4096, 2048, 128)
    top_p       = st.slider("Top-P", 0.1, 1.0, 0.95, 0.05)

    st.divider()
    st.markdown("**🖼️ Önizleme**")
    canvas_h = st.slider("Yükseklik (px)", 250, 950, 500, 10)
    bg_opts  = {"⬜ Beyaz":"#ffffff","⬛ Siyah":"#000000","🔲 Koyu":"#111111","🔵 Lacivert":"#0a0a2e","🟣 Mor":"#1a001a"}
    bg_choice = st.selectbox("Arka plan:", list(bg_opts.keys()))
    preview_bg = bg_opts[bg_choice]
    if st.checkbox("🎨 Özel arka plan rengi"):
        preview_bg = st.color_picker("Seç:", preview_bg)

    st.divider()
    st.markdown("**📊 Oturum**")
    m1, m2 = st.columns(2)
    m1.metric("Üretilen", st.session_state.generation_count)
    m2.metric("Favori", len(st.session_state.favorites))
    m3, m4 = st.columns(2)
    m3.metric("Geçmiş", len(st.session_state.history))
    m4.metric("Puanlanan", len(st.session_state.ratings))

    st.divider()
    if st.button("🗑️ Geçmişi Sıfırla", use_container_width=True):
        st.session_state.history = []
        st.session_state.batch_results = []
        st.rerun()

if not api_key:
    st.markdown('<div class="omega-title">K3N4N VOICE Ω</div>', unsafe_allow_html=True)
    st.error("⚠️ Sol panelden Groq API anahtarınızı girin. groq.com → ücretsiz hesap")
    st.stop()

client = Groq(api_key=api_key)

# ═══════════════════════════════════════════════════════════════
# 7. AI ÇAĞRI FONKSİYONLARI
# ═══════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """Sen bir ödüllü UI/text-effect tasarımcısısın. Yalnızca HTML+CSS+JS kodu üret.
KURALLAR (KESINLIKLE UYULMALI):
1. Ham kod döndür — ``` işaretleri, açıklama, preamble YASAK.
2. <body> arka planı SABIT BEYAZ (#fff) kalacak. Değiştirme.
3. Metin canvas ortasında, büyük, görünür olacak.
4. @keyframes animasyon zorunlu (en az 1 tane).
5. ::before / ::after ile derinlik/gölge kat.
6. CSS custom properties ile renk sistemi kur.
7. Parçacık efekti istenirse <canvas> veya DOM span parçacıkları JS ile oluştur.
8. text-shadow, filter, backdrop-filter, mix-blend-mode kullan.
9. Geçerli, cross-browser uyumlu, hatasız kod yaz.
10. Kod kalitesi: production-ready, temiz, yorumsuz."""

def build_prompt(nick, font, size, desc, palette, anim, effect, presets,
                 style_cat, add_bg, add_ptcl, add_box, multi_col, letter_spacing,
                 extra_css):
    pal_str = ""
    if palette != "Serbest (AI seçsin)" and palette in COLOR_PALETTES:
        pal_str = "Renk paleti: " + ", ".join(COLOR_PALETTES[palette])
    extras = []
    if add_bg:    extras.append("animated gradient/mesh background behind text")
    if add_ptcl:  extras.append("JS floating particle/glitter system (canvas or DOM spans)")
    if add_box:   extras.append("neon glow border card/frame around text")
    if multi_col: extras.append("each character wrapped in <span> with different color & staggered animation")
    if extra_css: extras.append(f"inject this CSS override: {extra_css}")

    return f"""Metin: "{nick}"
Font: {font} | Boyut: {size}px | Harf aralığı: {letter_spacing}px
{pal_str}
Kategori stili: {style_cat}
Animasyon: {anim}
Metin efekti: {effect}
Preset efektler: {presets or 'yok'}
Özel tarif: {desc or 'yok'}
Ekstra: {', '.join(extras) if extras else 'yok'}
En iyi, en etkileyici, production-ready sonucu üret."""

def call_ai(nick, font, size, desc, palette, anim, effect, presets,
            style_cat, add_bg, add_ptcl, add_box, multi_col,
            letter_spacing, extra_css, model, temp, mtok, top_p_val=0.95):
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":build_prompt(
                    nick, font, size, desc, palette, anim, effect, presets,
                    style_cat, add_bg, add_ptcl, add_box, multi_col,
                    letter_spacing, extra_css
                )},
            ],
            temperature=temp, max_tokens=mtok,
            top_p=top_p_val,
        )
        raw = resp.choices[0].message.content
        clean = re.sub(r"```(html|css|javascript|js)?", "", raw).replace("```","").strip()
        return clean, None
    except Exception as e:
        return None, str(e)

def call_ai_suggest(context):
    """AI'dan prompt önerisi al"""
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role":"system","content":"Sen bir kreatif metin efekti tasarım danışmanısın. Kullanıcıya 3 farklı yaratıcı tasarım önerisi sun. Her öneriyi tek satırda, Türkçe olarak yaz. Sadece önerileri listele, başka hiçbir şey yazma."},
                {"role":"user","content":f"Şu bilgilere göre 3 farklı tasarım tarifı öner: {context}"},
            ],
            temperature=1.1, max_tokens=400,
        )
        return resp.choices[0].message.content
    except:
        return ""

def wrap_html(code, font_name, bg="#fff"):
    fu = font_name.replace(" ","+")
    return f"""<!DOCTYPE html>
<html lang="tr">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<link href="https://fonts.googleapis.com/css2?family={fu}:wght@400;700;900&family=Nabla&family=Bungee+Spice&family=Orbitron:wght@900&display=swap" rel="stylesheet">
<style>
html,body{{margin:0;padding:0;background:{bg};display:flex;justify-content:center;align-items:center;min-height:100vh;overflow:hidden;font-family:'{font_name}',sans-serif;}}
</style>
</head>
<body>{code}</body>
</html>"""

# ═══════════════════════════════════════════════════════════════
# 8. BAŞLIK + MİKROFON
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="omega-title">K3N4N VOICE Ω v31</div>', unsafe_allow_html=True)
st.markdown('<div class="omega-sub">⚡ NEXT-GEN AI TEXT DESIGN STUDIO ⚡</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="mic-wrap">
  <button id="micBtn" class="mic-btn" onclick="startVoice('{vlang_code}','desc')">
    🎤 SESLİ KOMUT VER — Tıkla & Konuş ({vlang_label})
  </button>
  <div style="margin-top:10px;color:var(--muted);font-size:.82rem;font-family:sans-serif;">
    Konuştuktan sonra metin otomatik "Tasarım Tarifi"ne yazılır &nbsp;|&nbsp;
    <span style="cursor:pointer;color:var(--a3);" onclick="speakText('Tasarım hazır, K3N4N','{vlang_code}')">🔊 TTS Test</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 9. ANA FORM
# ═══════════════════════════════════════════════════════════════
with st.form("main_form"):
    # — Satır 1: Metin / Font / Boyut / Harf Aralığı
    c1, c2, c3, c4 = st.columns([2.5, 2.5, 1, 1])
    with c1: nick = st.text_input("✏️ Metin / Nick:", value="K3N4N")
    with c2:
        font_label = st.selectbox("🔤 Font:", list(FONTS.keys()))
        font_name  = FONTS[font_label]
    with c3: font_size = st.number_input("📏 Boyut:", min_value=20, max_value=320, value=80, step=4)
    with c4: letter_sp = st.number_input("↔️ Aralık:", min_value=-10, max_value=40, value=0, step=1)

    # — Satır 2: Palette / Style / Animasyon / Efekt
    c5, c6 = st.columns(2)
    with c5:
        palette_name = st.selectbox("🎨 Renk Paleti:", ["Serbest (AI seçsin)"] + list(COLOR_PALETTES.keys()))
        if palette_name != "Serbest (AI seçsin)":
            chips = COLOR_PALETTES[palette_name]
            chip_html = "".join(f'<span class="chip" title="{c}" style="background:{c}" onclick="copyToClipboard(\'{c}\')"></span>' for c in chips)
            st.markdown(chip_html, unsafe_allow_html=True)
        style_cat = st.selectbox("🎭 Stil Kategorisi:", ["AI Seçsin"] + list(STYLE_CATEGORIES.keys()))
    with c6:
        anim_type   = st.selectbox("🎬 Animasyon:", ANIM_TYPES)
        text_effect = st.selectbox("🌟 Metin Efekti:", TEXT_EFFECTS)

    # — Efekt presetleri
    st.markdown("**⚡ Hızlı Efekt Presetleri**")
    preset_cols = st.columns(5)
    selected_presets = []
    for i, p in enumerate(EFFECT_PRESETS):
        if preset_cols[i % 5].checkbox(p["e"], key=f"p_{i}"):
            selected_presets.append(p["d"])

    # — Hızlı token builder
    st.markdown("**🔖 Prompt Token Hızlı Ekle** *(tikla → tarife eklenir)*")
    token_html = "".join(f'<span class="prompt-token" onclick="toggleToken(this,\'{t}\')">{t}</span>' for t in QUICK_TOKENS)
    st.markdown(f'<div style="line-height:2.2;">{token_html}</div>', unsafe_allow_html=True)

    # — Tarif + Extra CSS
    d1, d2 = st.columns([2, 1])
    with d1:
        user_desc = st.text_area("📝 Tasarım Tarifi:", height=100,
            placeholder="Örn: altın parıltılı hologram efektli, glitch animasyonlu krom metin...")
    with d2:
        extra_css = st.text_area("🎨 Ekstra CSS Override:",height=100,
            placeholder="font-style:italic;\ntext-transform:uppercase;")

    # — Ekstra özellikler
    oc1, oc2, oc3, oc4, oc5 = st.columns(5)
    with oc1: add_bg    = st.checkbox("🌌 BG Animasyon")
    with oc2: add_ptcl  = st.checkbox("✨ Parçacık")
    with oc3: add_box   = st.checkbox("📦 Glow Kutu")
    with oc4: multi_col = st.checkbox("🌈 Renk/Harf")
    with oc5: code_edit = st.checkbox("✏️ Kod Editörü")

    # — Batch & AI Suggest
    bc1, bc2 = st.columns(2)
    with bc1:
        batch_mode = st.checkbox("🔁 Toplu Üretim (5 varyasyon otomatik)")
    with bc2:
        ai_suggest_mode = st.checkbox("💡 AI Prompt Önerisi Al (önce öner, sonra üret)")

    submit = st.form_submit_button("⚡ OMEGA v31 MOTORLA OLUŞTUR", use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# 10. FORM İŞLEMİ
# ═══════════════════════════════════════════════════════════════
style_cat_str = STYLE_CATEGORIES.get(style_cat, "AI en uygun stili seçsin")
preset_str    = ", ".join(selected_presets)

if submit:
    # ── AI Prompt Önerisi ────────────────────────────────────
    if ai_suggest_mode:
        with st.spinner("💡 AI prompt önerileri üretiyor..."):
            suggestions = call_ai_suggest(f"Nick:{nick}, Font:{font_name}, Tarif:{user_desc}")
        if suggestions:
            st.markdown("### 💡 AI Tasarım Önerileri")
            st.markdown(f'<div class="info-bar">{suggestions.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
            st.info("Bu önerileri tarife kopyalayıp tekrar oluşturabilirsiniz.")

    # ── Normal Üretim ────────────────────────────────────────
    if not batch_mode:
        prog = st.empty()
        prog.markdown('<div class="gen-progress"></div>', unsafe_allow_html=True)
        with st.spinner(f"🤖 {model_choice} üretiyor..."):
            html_code, err = call_ai(
                nick, font_name, font_size, user_desc, palette_name,
                anim_type, text_effect, preset_str, style_cat_str,
                add_bg, add_ptcl, add_box, multi_col, letter_sp, extra_css,
                model_choice, temperature, max_tokens, top_p
            )
        prog.empty()
        if err:
            st.error(f"❌ AI Hatası: {err}")
        else:
            st.session_state.current_html = html_code
            entry = {
                "nick":nick,"font":font_name,"size":font_size,"desc":user_desc,
                "html":html_code,"ts":time.strftime("%H:%M:%S"),
                "model":model_choice,"palette":palette_name,
                "anim":anim_type,"effect":text_effect,
                "hash":html_hash(html_code),
            }
            st.session_state.current_entry = entry
            st.session_state.history.insert(0, entry)
            if len(st.session_state.history) > 60:
                st.session_state.history = st.session_state.history[:60]
            st.session_state.generation_count += 1
            st.success(f"✅ Tasarım hazır! Model: `{model_choice}` | {entry['ts']}")

    # ── Toplu Üretim ─────────────────────────────────────────
    else:
        st.markdown("### 🔁 Toplu Üretim — 5 Varyasyon")
        batch_cols = st.columns(5)
        batch_results = []
        rand_fonts = random.sample(list(FONTS.values()), min(5, len(FONTS)))
        for i in range(5):
            f = rand_fonts[i]
            with batch_cols[i]:
                with st.spinner(f"#{i+1}..."):
                    bh, _ = call_ai(
                        nick, f, font_size, user_desc, palette_name,
                        random.choice(ANIM_TYPES[1:]), random.choice(TEXT_EFFECTS[1:]),
                        preset_str, style_cat_str, add_bg, False, False, False,
                        letter_sp, "", model_choice, temperature, max_tokens, top_p
                    )
                    if bh:
                        batch_results.append({"font":f,"html":bh,"nick":nick})
                        st.components.v1.html(wrap_html(bh, f, preview_bg), height=200)
                        st.caption(f"🔤 {f}")
                        b64b = base64.b64encode(wrap_html(bh, f).encode()).decode()
                        st.markdown(f'<a href="data:text/html;base64,{b64b}" download="batch_{i}.html" style="color:var(--a3);font-size:.75rem;">⬇️ İndir</a>', unsafe_allow_html=True)
        st.session_state.batch_results = batch_results
        st.session_state.generation_count += 5

# ═══════════════════════════════════════════════════════════════
# 11. SEKMELER
# ═══════════════════════════════════════════════════════════════
st.divider()
tabs = st.tabs([
    "🖼️ Önizleme", "✏️ Canlı Editör", "🔀 Varyasyon",
    "⚖️ Karşılaştır", "📜 Geçmiş", "⭐ Favoriler",
    "🎨 Renk Stüdyosu", "📦 Export", "🧪 Prompt Labı"
])
tab_prev, tab_edit, tab_var, tab_cmp, tab_hist, tab_fav, tab_color, tab_export, tab_lab = tabs

# ── TAB 1: ÖNİZLEME ────────────────────────────────────────
with tab_prev:
    if st.session_state.current_html:
        entry = st.session_state.current_entry or st.session_state.history[0]
        
        col_l, col_r = st.columns([1.7, 1])
        with col_l:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
              <span style="font-family:Orbitron;font-size:.85rem;color:var(--a1);">🖼️ CANLI ÖNİZLEME</span>
              <span class="ai-badge">✅ HAZIR &nbsp;|&nbsp; {entry.get('model','')}</span>
            </div>""", unsafe_allow_html=True)

            # CSS filtre kontrolleri
            fc1, fc2, fc3, fc4 = st.columns(4)
            filter_val = "none"
            with fc1:
                if st.button("🔵 Soğuk", key="f1"): filter_val = "hue-rotate(180deg) saturate(1.5)"
            with fc2:
                if st.button("🔴 Sıcak", key="f2"): filter_val = "hue-rotate(-30deg) saturate(1.8)"
            with fc3:
                if st.button("⚪ Gri", key="f3"):  filter_val = "grayscale(1)"
            with fc4:
                if st.button("🌈 Normal", key="f4"): filter_val = "none"

            full_html = wrap_html(st.session_state.current_html, entry.get("font","Orbitron"), preview_bg)
            st.components.v1.html(full_html, height=canvas_h)

        with col_r:
            # Puan sistemi
            h = entry.get("hash", html_hash(st.session_state.current_html))
            cur_rating = st.session_state.ratings.get(h, 0)
            st.markdown(f"**⭐ Tasarımı Puanla**")
            rating = st.select_slider("", options=[1,2,3,4,5], value=max(cur_rating,1), key="rating_slider",
                                       format_func=lambda x: "⭐"*x)
            if st.button("💾 Puanı Kaydet", key="save_rating"):
                st.session_state.ratings[h] = rating
                st.success(f"{'⭐'*rating} kaydedildi!")

            # Etiket sistemi
            st.markdown("**🏷️ Etiket Ekle**")
            tag_input = st.text_input("Etiket:", placeholder="örn: en iyi, altın, oyun", key="tag_inp", label_visibility="collapsed")
            if st.button("➕ Ekle", key="add_tag"):
                tags = st.session_state.tags.get(h, [])
                if tag_input and tag_input not in tags:
                    tags.append(tag_input)
                    st.session_state.tags[h] = tags
            existing_tags = st.session_state.tags.get(h, [])
            if existing_tags:
                st.markdown("".join(f'<span class="tag-pill">{t}</span>' for t in existing_tags), unsafe_allow_html=True)

            st.divider()
            # Aksiyon butonları
            if st.button("⭐ Favoriye Ekle", key="fav_now", use_container_width=True):
                if len(st.session_state.favorites) < 30:
                    fav_entry = entry.copy()
                    fav_entry["rating"] = st.session_state.ratings.get(h, 0)
                    st.session_state.favorites.insert(0, fav_entry)
                    st.success("Favorilere eklendi!")
                else: st.warning("Limit: 30 favori")

            if st.button("🔄 Yeniden Üret", key="regen", use_container_width=True):
                with st.spinner("Yeniden üretiliyor..."):
                    nh, _ = call_ai(
                        entry.get("nick","K3N4N"), entry.get("font","Orbitron"),
                        entry.get("size",80), entry.get("desc",""),
                        entry.get("palette","Serbest (AI seçsin)"), entry.get("anim","Yok"),
                        entry.get("effect","Normal"), "", style_cat_str,
                        False, False, False, False, 0, "",
                        model_choice, temperature, max_tokens, top_p
                    )
                    if nh:
                        st.session_state.current_html = nh
                        st.session_state.history[0]["html"] = nh
                        st.rerun()

            # Kaynak kod
            ct1, ct2 = st.tabs(["🧩 Fragment", "📄 Tam HTML"])
            with ct1: st.code(st.session_state.current_html, language="html")
            with ct2: st.code(wrap_html(st.session_state.current_html, entry.get("font","Orbitron")), language="html")

            # İndir butonu
            b64dl = base64.b64encode(wrap_html(st.session_state.current_html, entry.get("font","Orbitron")).encode()).decode()
            fname = f"k3n4n_{entry.get('nick','design').replace(' ','_')}_{entry.get('ts','')}.html"
            st.markdown(f"""
            <a href="data:text/html;base64,{b64dl}" download="{fname}"
               style="display:block;text-align:center;background:linear-gradient(135deg,var(--a2),var(--a1));
                      color:#fff;padding:11px;border-radius:10px;text-decoration:none;
                      font-family:Orbitron;font-size:.78rem;font-weight:700;margin-top:8px;">
                ⬇️ HTML İNDİR
            </a>""", unsafe_allow_html=True)
    else:
        st.info("⬆️ Formu doldurup **OMEGA v31 MOTORLA OLUŞTUR** butonuna basın.")

# ── TAB 2: CANLI HTML EDITÖR ────────────────────────────────
with tab_edit:
    st.markdown("### ✏️ Canlı HTML/CSS Editörü")
    st.markdown("Kodu değiştir → Önizleme anlık güncellenir")
    if st.session_state.current_html:
        default_code = st.session_state.current_html
    else:
        default_code = '<h1 style="font-family:Orbitron;font-size:80px;color:#ff00cc;text-shadow:0 0 30px #ff00cc;">K3N4N</h1>'

    edited_code = st.text_area("HTML/CSS Kodu:", value=default_code, height=280, key="live_editor")
    
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        live_font = st.selectbox("Font:", list(FONTS.keys()), key="live_font_sel")
        live_font_name = FONTS[live_font]
    with ec2:
        live_bg = st.color_picker("Arka plan:", preview_bg, key="live_bg")
    with ec3:
        live_h = st.slider("Yükseklik:", 200, 700, 400, key="live_h")

    if st.button("🔄 Önizlemeyi Güncelle", key="live_update", use_container_width=True):
        st.components.v1.html(wrap_html(edited_code, live_font_name, live_bg), height=live_h)
        if st.button("💾 Bu Kodu Kaydet", key="save_edit"):
            st.session_state.current_html = edited_code
            st.session_state.history.insert(0, {
                "nick":"[Düzenlendi]","font":live_font_name,"size":0,
                "desc":"Manuel düzenleme","html":edited_code,
                "ts":time.strftime("%H:%M:%S"),"model":"Manuel",
                "palette":"","anim":"","effect":"","hash":html_hash(edited_code),
            })
            st.success("Kaydedildi!")
    else:
        st.components.v1.html(wrap_html(edited_code, live_font_name, live_bg), height=live_h)

# ── TAB 3: VARYASYONLAR ─────────────────────────────────────
with tab_var:
    st.markdown("### 🔀 Çok Varyasyon Üret")
    if not st.session_state.current_html:
        st.info("Önce bir tasarım oluşturun.")
    else:
        entry = st.session_state.history[0]
        v1c, v2c = st.columns(2)
        with v1c:
            var_count = st.radio("Varyasyon sayısı:", [2, 3, 4, 6], horizontal=True, index=1)
        with v2c:
            var_mode = st.radio("Varyasyon modu:", ["Farklı fontlar","Farklı efektler","Tam rastgele"], horizontal=True)
        
        var_fonts = st.multiselect("Font seç:", list(FONTS.keys()), default=list(FONTS.keys())[:var_count])

        if st.button("🎲 Varyasyonları Üret", use_container_width=True, key="gen_var"):
            cols = st.columns(min(var_count, 3))
            for i in range(var_count):
                vf_label = var_fonts[i] if i < len(var_fonts) else random.choice(list(FONTS.keys()))
                vf_name  = FONTS[vf_label]
                v_anim   = random.choice(ANIM_TYPES[1:]) if var_mode != "Farklı fontlar" else anim_type
                v_effect = random.choice(TEXT_EFFECTS[1:]) if var_mode == "Tam rastgele" else text_effect

                with cols[i % min(var_count, 3)]:
                    with st.spinner(f"#{i+1} üretiliyor..."):
                        vh, _ = call_ai(
                            entry["nick"], vf_name, entry["size"],
                            entry["desc"], entry.get("palette","Serbest (AI seçsin)"),
                            v_anim, v_effect, "", style_cat_str,
                            False, False, False, False, 0, "",
                            model_choice, temperature, max_tokens, top_p
                        )
                        if vh:
                            st.markdown(f"**#{i+1} — {vf_label}**")
                            st.components.v1.html(wrap_html(vh, vf_name, preview_bg), height=240)
                            b64v = base64.b64encode(wrap_html(vh, vf_name).encode()).decode()
                            st.markdown(f'<a href="data:text/html;base64,{b64v}" download="var_{i+1}.html" style="color:var(--a3);font-size:.78rem;">⬇️ İndir</a>', unsafe_allow_html=True)
                            if st.button(f"⭐ Fav #{i+1}", key=f"var_fav_{i}"):
                                st.session_state.favorites.insert(0,{"nick":entry["nick"],"font":vf_name,"html":vh,"ts":time.strftime("%H:%M"),"size":entry["size"],"desc":"Varyasyon","model":model_choice,"palette":"","anim":v_anim,"effect":v_effect,"hash":html_hash(vh)})

# ── TAB 4: KARŞILAŞTIRMA ────────────────────────────────────
with tab_cmp:
    st.markdown("### ⚖️ Yan Yana Karşılaştır")
    if len(st.session_state.history) < 2:
        st.info("En az 2 tasarım gerekli.")
    else:
        history_labels = [f"#{i+1} — {h['nick']} | {h['font']} | {h['ts']}"
                          for i, h in enumerate(st.session_state.history)]
        cc1, cc2 = st.columns(2)
        with cc1:
            sel_a = st.selectbox("Sol taraf:", history_labels, index=0, key="cmp_a")
        with cc2:
            sel_b = st.selectbox("Sağ taraf:", history_labels, index=1 if len(history_labels)>1 else 0, key="cmp_b")

        idx_a = history_labels.index(sel_a)
        idx_b = history_labels.index(sel_b)
        item_a = st.session_state.history[idx_a]
        item_b = st.session_state.history[idx_b]

        ca, cb = st.columns(2)
        with ca:
            st.markdown(f'<div class="compare-label">A: {item_a["nick"]} / {item_a["font"]}</div>', unsafe_allow_html=True)
            st.components.v1.html(wrap_html(item_a["html"], item_a["font"], preview_bg), height=380)
            ra = st.session_state.ratings.get(item_a.get("hash",""), 0)
            st.markdown(f"{'⭐'*ra if ra else '—'}")
        with cb:
            st.markdown(f'<div class="compare-label">B: {item_b["nick"]} / {item_b["font"]}</div>', unsafe_allow_html=True)
            st.components.v1.html(wrap_html(item_b["html"], item_b["font"], preview_bg), height=380)
            rb = st.session_state.ratings.get(item_b.get("hash",""), 0)
            st.markdown(f"{'⭐'*rb if rb else '—'}")

        # Kazananı seç
        win_c1, win_c2 = st.columns(2)
        with win_c1:
            if st.button("🏆 A Kazandı — Favoriye Ekle", use_container_width=True):
                st.session_state.favorites.insert(0, item_a.copy())
                st.success("A favorilere eklendi!")
        with win_c2:
            if st.button("🏆 B Kazandı — Favoriye Ekle", use_container_width=True):
                st.session_state.favorites.insert(0, item_b.copy())
                st.success("B favorilere eklendi!")

# ── TAB 5: GEÇMİŞ ──────────────────────────────────────────
with tab_hist:
    st.markdown(f"### 📜 Üretim Geçmişi ({len(st.session_state.history)} kayıt)")
    if not st.session_state.history:
        st.info("Henüz tasarım üretilmedi.")
    else:
        # Arama / filtre
        search_q = st.text_input("🔍 Nick veya font ara:", key="hist_search")
        filtered = [h for h in st.session_state.history
                    if search_q.lower() in h["nick"].lower() or search_q.lower() in h["font"].lower()] if search_q else st.session_state.history

        for i, item in enumerate(filtered):
            h_hash = item.get("hash","")
            r = st.session_state.ratings.get(h_hash, 0)
            tags_str = " ".join(f'<span class="tag-pill">{t}</span>' for t in st.session_state.tags.get(h_hash,[]))
            label = f"#{i+1} — **{item['nick']}** | `{item['font']}` | {item['ts']} {'⭐'*r if r else ''}"
            with st.expander(label):
                hc1, hc2 = st.columns([1.6, 1])
                with hc1:
                    st.components.v1.html(wrap_html(item["html"], item["font"], preview_bg), height=200)
                    if tags_str: st.markdown(tags_str, unsafe_allow_html=True)
                with hc2:
                    st.markdown(f"**Model:** `{item.get('model','?')}`")
                    st.markdown(f"**Tarif:** {item.get('desc','—')[:80]}")
                    st.code(item["html"][:400]+("…" if len(item["html"])>400 else ""), language="html")
                    ha1, ha2, ha3 = st.columns(3)
                    with ha1:
                        if st.button("⭐", key=f"hfav_{i}", help="Favoriye ekle"):
                            st.session_state.favorites.insert(0, item.copy())
                    with ha2:
                        if st.button("⚖️", key=f"hcmp_{i}", help="Karşılaştırmaya ekle"):
                            st.session_state.compare_a = item
                    with ha3:
                        b64h = base64.b64encode(wrap_html(item["html"], item["font"]).encode()).decode()
                        st.markdown(f'<a href="data:text/html;base64,{b64h}" download="h_{i}.html" style="color:var(--a3);font-size:.8rem;">⬇️</a>', unsafe_allow_html=True)

# ── TAB 6: FAVORİLER ────────────────────────────────────────
with tab_fav:
    st.markdown(f"### ⭐ Favorilerim ({len(st.session_state.favorites)})")
    if not st.session_state.favorites:
        st.info("Favori yok. Önizleme sekmesinden ⭐ butonuna bas.")
    else:
        # Sıralama
        sort_by = st.radio("Sırala:", ["En yeni","En yüksek puan"], horizontal=True, key="fav_sort")
        favs = st.session_state.favorites.copy()
        if sort_by == "En yüksek puan":
            favs.sort(key=lambda x: st.session_state.ratings.get(x.get("hash",""),0), reverse=True)

        fc = st.columns(2)
        for i, fav in enumerate(favs):
            with fc[i % 2]:
                h_hash = fav.get("hash","")
                r = st.session_state.ratings.get(h_hash, 0)
                tags_display = " ".join(f'<span class="tag-pill">{t}</span>' for t in st.session_state.tags.get(h_hash,[]))
                st.markdown(f"**{fav['nick']}** — `{fav['font']}` {'⭐'*r if r else ''}")
                if tags_display: st.markdown(tags_display, unsafe_allow_html=True)
                st.components.v1.html(wrap_html(fav["html"], fav["font"], preview_bg), height=200)
                fb1, fb2, fb3 = st.columns(3)
                with fb1:
                    b64f = base64.b64encode(wrap_html(fav["html"], fav["font"]).encode()).decode()
                    st.markdown(f'<a href="data:text/html;base64,{b64f}" download="fav_{i}.html" style="color:var(--a4);font-size:.8rem;">⬇️ İndir</a>', unsafe_allow_html=True)
                with fb2:
                    if st.button("✏️ Düzenle", key=f"fedit_{i}"):
                        st.session_state.current_html = fav["html"]
                        st.session_state.current_entry = fav
                        st.rerun()
                with fb3:
                    if st.button("🗑️", key=f"fdel_{i}"):
                        st.session_state.favorites.pop(i)
                        st.rerun()

# ── TAB 7: RENK STÜDYOSU ────────────────────────────────────
with tab_color:
    st.markdown("### 🎨 Renk Stüdyosu")
    st.markdown("Renk paletlerini incele, kur, AI ile üret.")

    cs1, cs2 = st.columns(2)
    with cs1:
        st.markdown("**Mevcut Paletler**")
        for name, colors in COLOR_PALETTES.items():
            chips = "".join(f'<span class="chip" title="{c}" style="background:{c}" onclick="copyToClipboard(\'{c}\')"></span>' for c in colors)
            st.markdown(f"<div style='margin:8px 0;'><b style='font-family:Rajdhani;'>{name}</b> &nbsp; {chips}</div>", unsafe_allow_html=True)

    with cs2:
        st.markdown("**🤖 AI Özel Palet Üret**")
        palette_theme = st.text_input("Tema:", placeholder="örn: aurora borealis, cyberpunk city, autumn forest")
        if st.button("✨ AI Palet Oluştur", key="gen_palette"):
            with st.spinner("Palet üretiliyor..."):
                try:
                    pr = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role":"system","content":"Return ONLY a JSON array of exactly 5 hex color codes for the given theme. No text, no explanation. Example: [\"#ff0000\",\"#00ff00\",\"#0000ff\",\"#ffff00\",\"#ff00ff\"]"},
                            {"role":"user","content":f"Theme: {palette_theme}"},
                        ],
                        temperature=0.9, max_tokens=80,
                    )
                    raw_p = pr.choices[0].message.content.strip()
                    colors_ai = json.loads(re.search(r'\[.*?\]', raw_p, re.DOTALL).group())
                    chip_html = "".join(f'<span class="chip" style="background:{c};width:40px;height:40px;" title="{c}" onclick="copyToClipboard(\'{c}\')"></span>' for c in colors_ai)
                    st.markdown(f"<div style='margin:12px 0;'>{chip_html}</div>", unsafe_allow_html=True)
                    st.code(json.dumps(colors_ai), language="json")
                    st.success("Palette oluşturuldu! Renklere tıklayarak kopyalayabilirsiniz.")
                except Exception as e:
                    st.error(f"Palette oluşturulamadı: {e}")

        st.divider()
        st.markdown("**🔀 Gradient Üretici**")
        gc1, gc2, gc3 = st.columns(3)
        g_col1 = gc1.color_picker("Renk 1:", "#ff00cc")
        g_col2 = gc2.color_picker("Renk 2:", "#3333ff")
        g_angle = gc3.slider("Açı:", 0, 360, 135)
        grad_css = f"linear-gradient({g_angle}deg, {g_col1}, {g_col2})"
        st.markdown(f'<div style="height:60px;border-radius:12px;background:{grad_css};margin:8px 0;"></div>', unsafe_allow_html=True)
        st.code(f"background: {grad_css};", language="css")

# ── TAB 8: EXPORT ───────────────────────────────────────────
with tab_export:
    st.markdown("### 📦 Export & Paylaşım Merkezi")
    if not st.session_state.current_html:
        st.info("Önce bir tasarım oluşturun.")
    else:
        entry = st.session_state.current_entry or st.session_state.history[0]
        full_export = wrap_html(st.session_state.current_html, entry.get("font","Orbitron"))
        b64_ex = base64.b64encode(full_export.encode()).decode()
        fname  = f"k3n4n_{entry.get('nick','tasarim').replace(' ','_')}.html"

        ex1, ex2, ex3 = st.columns(3)
        with ex1:
            st.markdown("**🌐 Standalone HTML**")
            st.markdown("Font ve stiller gömülü, çevrimdışı çalışır.")
            st.markdown(f'<a href="data:text/html;base64,{b64_ex}" download="{fname}" style="display:block;text-align:center;background:linear-gradient(135deg,var(--a2),#6600cc);color:#fff;padding:12px;border-radius:10px;text-decoration:none;font-family:Orbitron;font-size:.8rem;font-weight:700;">⬇️ HTML İNDİR</a>', unsafe_allow_html=True)

        with ex2:
            st.markdown("**📋 Tüm Geçmişi JSON**")
            jdata = json.dumps([{"nick":h["nick"],"font":h["font"],"size":h["size"],"desc":h.get("desc",""),"ts":h["ts"],"model":h.get("model","")} for h in st.session_state.history], ensure_ascii=False, indent=2)
            b64j = base64.b64encode(jdata.encode()).decode()
            st.markdown(f'<a href="data:application/json;base64,{b64j}" download="gecmis.json" style="display:block;text-align:center;background:linear-gradient(135deg,#006633,#00cc44);color:#fff;padding:12px;border-radius:10px;text-decoration:none;font-family:Orbitron;font-size:.8rem;font-weight:700;">⬇️ JSON GEÇMİŞ</a>', unsafe_allow_html=True)

        with ex3:
            st.markdown("**⭐ Favorileri JSON**")
            fjdata = json.dumps([{"nick":f["nick"],"font":f["font"],"ts":f.get("ts",""),"desc":f.get("desc","")} for f in st.session_state.favorites], ensure_ascii=False, indent=2)
            b64fj = base64.b64encode(fjdata.encode()).decode()
            st.markdown(f'<a href="data:application/json;base64,{b64fj}" download="favoriler.json" style="display:block;text-align:center;background:linear-gradient(135deg,#885500,#ffaa00);color:#fff;padding:12px;border-radius:10px;text-decoration:none;font-family:Orbitron;font-size:.8rem;font-weight:700;">⬇️ FAVORİLER JSON</a>', unsafe_allow_html=True)

        st.divider()
        st.markdown("**🧾 CSS Kodu Çıkar**")
        st.markdown("Sadece CSS stil bloğunu çek:")
        css_match = re.findall(r'<style[^>]*>(.*?)</style>', full_export, re.DOTALL)
        if css_match:
            st.code("\n".join(css_match), language="css")
        
        st.markdown("**📄 Tam Kaynak Kodu**")
        st.code(full_export, language="html")

# ── TAB 9: PROMPT LABI ──────────────────────────────────────
with tab_lab:
    st.markdown("### 🧪 Prompt Laboratuvarı")
    st.markdown("AI'ı direkt test et, prompt mühendisliği yap.")

    lab_c1, lab_c2 = st.columns(2)
    with lab_c1:
        st.markdown("**🔬 Serbest AI Chat (HTML üretici)**")
        lab_prompt = st.text_area("Serbest prompt:", height=150,
            placeholder="İstediğin herhangi bir HTML/CSS efektini tarif et...",
            key="lab_prompt")
        lab_nick_override = st.text_input("Nick override:", value="K3N4N", key="lab_nick")
        lab_font_sel = st.selectbox("Font:", list(FONTS.keys()), key="lab_font")
        lab_font_name = FONTS[lab_font_sel]

        if st.button("🚀 Lab Üret", key="lab_gen", use_container_width=True):
            with st.spinner("Lab üretiyor..."):
                lh, le = call_ai(
                    lab_nick_override, lab_font_name, 80, lab_prompt,
                    "Serbest (AI seçsin)", "Yok", "Normal", "", "AI Seçsin",
                    False, False, False, False, 0, "",
                    model_choice, temperature, max_tokens, top_p
                )
                if lh:
                    st.session_state["lab_result"] = lh
                    st.session_state["lab_font"] = lab_font_name
                else:
                    st.error(le)

    with lab_c2:
        st.markdown("**🔭 Lab Önizleme**")
        if "lab_result" in st.session_state and st.session_state["lab_result"]:
            lf = st.session_state.get("lab_font","Orbitron")
            st.components.v1.html(wrap_html(st.session_state["lab_result"], lf, preview_bg), height=320)
            st.code(st.session_state["lab_result"][:600], language="html")
            if st.button("📌 Ana Geçmişe Ekle", key="lab_save"):
                lentry = {
                    "nick":lab_nick_override,"font":lf,"size":80,
                    "desc":lab_prompt,"html":st.session_state["lab_result"],
                    "ts":time.strftime("%H:%M:%S"),"model":model_choice,
                    "palette":"","anim":"","effect":"",
                    "hash":html_hash(st.session_state["lab_result"]),
                }
                st.session_state.history.insert(0, lentry)
                st.session_state.current_html   = st.session_state["lab_result"]
                st.session_state.current_entry  = lentry
                st.session_state.generation_count += 1
                st.success("Geçmişe eklendi!")

    st.divider()
    st.markdown("**📊 Prompt A/B Test**")
    st.markdown("İki farklı prompt'u karşılaştır:")
    ab1, ab2 = st.columns(2)
    with ab1:
        ab_prompt_a = st.text_area("Prompt A:", height=80, key="ab_a",
            placeholder="gold metallic sparkle, 3D emboss")
    with ab2:
        ab_prompt_b = st.text_area("Prompt B:", height=80, key="ab_b",
            placeholder="neon cyberpunk glitch, plasma energy")

    ab_nick = st.text_input("A/B Nick:", value="K3N4N", key="ab_nick")
    ab_font_label = st.selectbox("A/B Font:", list(FONTS.keys()), key="ab_font")
    ab_font_name  = FONTS[ab_font_label]

    if st.button("⚡ İkisini Üret & Karşılaştır", key="ab_run", use_container_width=True):
        abc1, abc2 = st.columns(2)
        with abc1:
            with st.spinner("A üretiliyor..."):
                aha, _ = call_ai(ab_nick, ab_font_name, 80, ab_prompt_a, "Serbest (AI seçsin)",
                                  "Yok","Normal","","AI Seçsin",False,False,False,False,0,"",
                                  model_choice,temperature,max_tokens,top_p)
            if aha:
                st.markdown("**Prompt A**")
                st.components.v1.html(wrap_html(aha, ab_font_name, preview_bg), height=280)
        with abc2:
            with st.spinner("B üretiliyor..."):
                ahb, _ = call_ai(ab_nick, ab_font_name, 80, ab_prompt_b, "Serbest (AI seçsin)",
                                  "Yok","Normal","","AI Seçsin",False,False,False,False,0,"",
                                  model_choice,temperature,max_tokens,top_p)
            if ahb:
                st.markdown("**Prompt B**")
                st.components.v1.html(wrap_html(ahb, ab_font_name, preview_bg), height=280)

# ═══════════════════════════════════════════════════════════════
# 12. ALT BİLGİ
# ═══════════════════════════════════════════════════════════════
st.divider()
st.markdown(f"""
<div style="text-align:center;color:var(--muted);font-family:Orbitron;font-size:.68rem;letter-spacing:2px;padding:10px 0;">
  K3N4N VOICE Ω v31 &nbsp;·&nbsp; {len(FONTS)} Font &nbsp;·&nbsp; {len(COLOR_PALETTES)} Palet &nbsp;·&nbsp; {len(EFFECT_PRESETS)} Preset &nbsp;·&nbsp; Groq AI Powered &nbsp;·&nbsp; 9 Sekme
</div>
""", unsafe_allow_html=True)
