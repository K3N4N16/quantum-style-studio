import streamlit as st
from groq import Groq
import re
import base64
import json
import time
import random

# ─────────────────────────────────────────────
# 1. SAYFA AYARLARI
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="K3N4N VOICE v30.0",
    layout="wide",
    page_icon="🎙️",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 2. CSS + JS MOTORU
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Nabla&family=Bungee+Spice&family=Bungee+Shade&family=Rubik+Glitch&family=Rubik+Mono+One&family=Faster+One&family=Righteous&family=Nosifer&family=Creepster&family=Pacifico&family=Monoton&family=Press+Start+2P&family=VT323&family=Audiowide&family=Rajdhani:wght@700&family=Turret+Road:wght@800&family=Black+Ops+One&family=Alfa+Slab+One&family=Russo+One&display=swap');

:root {
  --bg: #020205;
  --surface: #0d0d18;
  --border: #222244;
  --accent1: #ff00cc;
  --accent2: #3333ff;
  --accent3: #00ffcc;
  --accent4: #ffcc00;
  --danger: #ff3333;
  --text: #e0e0ff;
  --muted: #666688;
}

*, *::before, *::after { box-sizing: border-box; }

.stApp { background: var(--bg) !important; color: var(--text); }
.stApp > header { background: transparent !important; }

/* Genel buton geçersiz kılma */
.stButton > button {
  background: linear-gradient(135deg, var(--accent2), var(--accent1)) !important;
  color: #fff !important; border: none !important;
  border-radius: 10px !important; font-family: 'Orbitron', sans-serif !important;
  font-weight: 700 !important; letter-spacing: 1px;
  transition: all .25s !important;
}
.stButton > button:hover { filter: brightness(1.3) !important; transform: scale(1.02) !important; }

/* Form submit butonu */
.stFormSubmitButton > button {
  background: linear-gradient(135deg, #ff6600, #ff0000) !important;
  font-size: 1.1rem !important; padding: 14px 32px !important;
  border-radius: 14px !important; font-family: 'Orbitron', sans-serif !important;
  box-shadow: 0 0 30px rgba(255,60,0,.5) !important;
  width: 100% !important;
}

/* Input / Textarea */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 10px !important;
  font-family: 'Rajdhani', sans-serif !important;
  font-size: 1rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--accent1) !important;
  box-shadow: 0 0 12px rgba(255,0,204,.3) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 12px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: var(--muted) !important; font-family: 'Orbitron', sans-serif !important; font-size: .75rem; }
.stTabs [aria-selected="true"] { background: var(--accent2) !important; color: #fff !important; border-radius: 8px !important; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Kod bloğu */
.stCodeBlock { border-radius: 12px !important; border: 1px solid var(--border) !important; }

/* Metric */
[data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px 16px; }

/* Başlık */
.omega-title {
  text-align: center;
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(1.8rem, 4vw, 3rem);
  font-weight: 900;
  background: linear-gradient(90deg, #ff00cc, #3333ff, #00ffcc, #ffcc00, #ff00cc);
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradShift 4s ease infinite;
  margin-bottom: 4px;
}
.omega-sub {
  text-align: center;
  font-family: 'Rajdhani', sans-serif;
  color: var(--muted);
  letter-spacing: 4px;
  font-size: .9rem;
  margin-bottom: 28px;
}
@keyframes gradShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Ses butonu konteyneri */
.mic-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 24px 32px;
  text-align: center;
  margin-bottom: 20px;
}
.mic-btn {
  background: linear-gradient(135deg, #cc0000, #ff3300);
  color: #fff; border: none; border-radius: 50px;
  padding: 18px 44px; font-size: 1.15rem; font-weight: 700;
  font-family: 'Orbitron', sans-serif; cursor: pointer;
  box-shadow: 0 0 28px rgba(255,40,0,.5);
  transition: all .3s; letter-spacing: 1px;
}
.mic-btn:hover { box-shadow: 0 0 50px rgba(255,40,0,.8); transform: scale(1.04); }
.mic-btn.listening { animation: pulse 1s ease-in-out infinite; background: #ff1111 !important; }
@keyframes pulse { 0%,100% { box-shadow: 0 0 20px #ff0000; } 50% { box-shadow: 0 0 60px #ff0000, 0 0 100px #ff6600; } }

/* Önizleme iframe */
iframe {
  background: #fff !important;
  border-radius: 16px !important;
  border: 2px solid var(--border) !important;
}

/* Renk önizlemesi */
.color-chip {
  display: inline-block;
  width: 28px; height: 28px;
  border-radius: 50%; border: 2px solid #444;
  margin: 3px; cursor: pointer; transition: transform .2s;
  vertical-align: middle;
}
.color-chip:hover { transform: scale(1.3); }

/* Preset kartları */
.preset-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: border-color .2s;
}
.preset-card:hover { border-color: var(--accent1); }

/* Durum badge */
.badge {
  display: inline-block;
  padding: 3px 10px; border-radius: 20px;
  font-size: .72rem; font-weight: 700;
  font-family: 'Orbitron', sans-serif; letter-spacing: 1px;
}
.badge-ok  { background: rgba(0,255,150,.15); color: #00ff96; border: 1px solid #00ff96; }
.badge-err { background: rgba(255,50,50,.15); color: #ff5050; border: 1px solid #ff5050; }
.badge-ai  { background: rgba(100,100,255,.15); color: #8888ff; border: 1px solid #8888ff; }

/* Snippet kartları */
.snippet-card {
  background: var(--surface);
  border-left: 3px solid var(--accent2);
  border-radius: 0 10px 10px 0;
  padding: 10px 14px;
  margin-bottom: 8px;
  font-family: 'Rajdhani', sans-serif;
  font-size: .9rem;
  cursor: pointer;
}
.snippet-card:hover { border-left-color: var(--accent1); }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--accent2); border-radius: 3px; }
</style>

<script>
// ── Ses motoru ──────────────────────────────────────────────────
function startVoiceEngine(lang) {
    const SRClass = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SRClass) { alert("Tarayıcınız Web Speech API desteklemiyor (Chrome önerilir)."); return; }

    const recognition = new SRClass();
    recognition.lang = lang || 'tr-TR';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    const btn = document.getElementById('main-voice-btn');
    btn.textContent = "🔴 DİNLİYORUM...";
    btn.classList.add('listening');

    recognition.onresult = function(event) {
        const txt = event.results[0][0].transcript;
        const doc = window.parent.document;
        const areas = doc.querySelectorAll('textarea');
        areas.forEach(a => {
            const nativeSet = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
            nativeSet.call(a, txt);
            a.dispatchEvent(new Event('input', { bubbles: true }));
            a.dispatchEvent(new Event('change', { bubbles: true }));
        });
        btn.textContent = "✅ ALINDI: " + txt.substring(0,30) + (txt.length>30?"…":"");
        btn.classList.remove('listening');
        setTimeout(()=>{ btn.textContent = "🎤 SESLİ KOMUT VER"; }, 3000);
    };

    recognition.onerror = function(e) {
        btn.textContent = "⚠️ HATA: " + e.error.toUpperCase();
        btn.classList.remove('listening');
        if (e.error === 'not-allowed') alert("Mikrofon erişimi reddedildi. Adres çubuğundaki kilit simgesinden izin verin.");
    };

    recognition.onend = () => btn.classList.remove('listening');
    recognition.start();
}

// ── Download helper ─────────────────────────────────────────────
function downloadHTML(content, filename) {
    const blob = new Blob([content], {type: 'text/html'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename || 'tasarim.html';
    a.click();
}
</script>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 3. SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "history": [],          # [{nick, prompt, html, ts}, ...]
    "current_html": "",
    "current_css": "",
    "last_prompt": "",
    "favorites": [],
    "generation_count": 0,
    "dark_preview": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# 4. API BAĞLANTISI
# ─────────────────────────────────────────────
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    with st.sidebar:
        st.markdown("### 🔑 API Anahtarı")
        api_key = st.text_input("Groq Cloud Key:", type="password")

if not api_key:
    st.markdown('<div class="omega-title">K3N4N VOICE Ω</div>', unsafe_allow_html=True)
    st.error("⚠️ Lütfen sol panelden Groq API anahtarınızı girin.")
    st.stop()

client = Groq(api_key=api_key)

# ─────────────────────────────────────────────
# 5. SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-family:Orbitron;font-size:1.1rem;color:#ff00cc;font-weight:900;margin-bottom:16px;'>⚙️ KONTROL PANELİ</div>", unsafe_allow_html=True)

    # ── Model seçimi
    st.markdown("**🤖 AI Modeli**")
    model_choice = st.selectbox("", [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ], label_visibility="collapsed")

    # ── Dil seçimi (ses)
    st.markdown("**🌐 Ses Dili**")
    voice_lang = st.selectbox("", {
        "Türkçe": "tr-TR",
        "İngilizce": "en-US",
        "Almanca": "de-DE",
        "Fransızca": "fr-FR",
        "İspanyolca": "es-ES",
    }.keys(), label_visibility="collapsed")
    voice_lang_code = {"Türkçe":"tr-TR","İngilizce":"en-US","Almanca":"de-DE","Fransızca":"fr-FR","İspanyolca":"es-ES"}[voice_lang]

    # ── Gelişmiş parametreler
    st.markdown("**🎛️ AI Parametreleri**")
    temperature  = st.slider("Yaratıcılık (Temperature)", 0.0, 1.5, 0.9, 0.05)
    max_tokens   = st.slider("Max Token", 512, 4096, 2048, 128)
    st.markdown("**📐 Canvas Boyutu**")
    canvas_h = st.slider("Önizleme Yüksekliği (px)", 300, 900, 520, 10)

    st.divider()

    # ── Önizleme arka planı
    st.markdown("**🎨 Önizleme Arka Planı**")
    bg_choice = st.radio("", ["Beyaz", "Siyah", "Gri", "Özel"], horizontal=True, label_visibility="collapsed")
    custom_bg = "#ffffff"
    if bg_choice == "Beyaz":   custom_bg = "#ffffff"
    elif bg_choice == "Siyah": custom_bg = "#000000"
    elif bg_choice == "Gri":   custom_bg = "#1a1a1a"
    else:
        custom_bg = st.color_picker("Arka plan rengi:", "#ffffff")

    st.divider()

    # ── İstatistikler
    st.markdown("**📊 Oturum İstatistikleri**")
    m1, m2 = st.columns(2)
    m1.metric("Üretilen", st.session_state.generation_count)
    m2.metric("Favori", len(st.session_state.favorites))

    st.divider()

    # ── Geçmişi sıfırla
    if st.button("🗑️ Geçmişi Temizle", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ─────────────────────────────────────────────
# 6. BAŞLIK
# ─────────────────────────────────────────────
st.markdown('<div class="omega-title">K3N4N VOICE Ω v30</div>', unsafe_allow_html=True)
st.markdown('<div class="omega-sub">⚡ AI-POWERED TEXT DESIGN STUDIO ⚡</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 7. SES MOTORU
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="mic-wrap">
    <button id="main-voice-btn" class="mic-btn" onclick="startVoiceEngine('{voice_lang_code}')">
        🎤 SESLİ KOMUT VER — Tıkla ve Konuş ({voice_lang})
    </button>
    <p style="margin-top:12px;color:#666;font-size:.85rem;font-family:sans-serif;">
        Konuşmanız bittiğinde metin otomatik olarak "Tasarım Tarifi" alanına yazılacaktır.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 8. FONT & RENK KÜTÜPHANESİ
# ─────────────────────────────────────────────
FONTS = {
    # Efekt Fontlar
    "🌈 Nabla":           "Nabla",
    "🔥 Bungee Spice":    "Bungee Spice",
    "👻 Bungee Shade":    "Bungee Shade",
    "💀 Nosifer":         "Nosifer",
    "😱 Creepster":       "Creepster",
    "🌀 Rubik Glitch":    "Rubik Glitch",
    # Geometrik / Modern
    "🚀 Orbitron":        "Orbitron",
    "⚡ Turret Road":     "Turret Road",
    "🎯 Audiowide":       "Audiowide",
    "🔮 Monoton":         "Monoton",
    "🕹️ Press Start 2P":  "Press Start 2P",
    "📺 VT323":           "VT323",
    "🏁 Black Ops One":   "Black Ops One",
    "🛸 Russo One":       "Russo One",
    "⚙️ Rajdhani":        "Rajdhani",
    "🤖 Rubik Mono One":  "Rubik Mono One",
    # Dekoratif / Script
    "✍️ Pacifico":        "Pacifico",
    "⚡ Faster One":      "Faster One",
    "🎸 Righteous":       "Righteous",
    "🅰️ Alfa Slab One":   "Alfa Slab One",
}

# Önceden tanımlı renk paletleri
COLOR_PRESETS = {
    "🔥 Ateş": ["#ff0000", "#ff6600", "#ffcc00", "#ff3300"],
    "💎 Elmas": ["#00ccff", "#0066ff", "#aa00ff", "#ffffff"],
    "🌿 Matrix": ["#00ff41", "#003300", "#00cc33", "#ffffff"],
    "🌅 Gün Batımı": ["#ff6b6b", "#feca57", "#ff9ff3", "#54a0ff"],
    "🪙 Gold": ["#ffd700", "#ffaa00", "#cc8800", "#fff5cc"],
    "🌙 Gece": ["#4834d4", "#686de0", "#30336b", "#c7ecee"],
    "⚡ Neon": ["#ff00ff", "#00ffff", "#ff0099", "#00ff66"],
    "🎨 Pastel": ["#a29bfe", "#fd79a8", "#fdcb6e", "#55efc4"],
}

# Efekt presetleri
EFFECT_PRESETS = [
    {"label": "✨ Altın Işıltı", "desc": "gold metallic gradient, shimmer effect, drop shadow, sparkle particles"},
    {"label": "🌊 Okyanus Dalgası", "desc": "deep blue to cyan gradient, wave animation, water ripple texture, bubbles"},
    {"label": "🔥 Alevler", "desc": "red orange yellow flame gradient, fire animation, ember particles, glow"},
    {"label": "💜 Hologram", "desc": "purple pink holographic foil, rainbow shimmer, scanline overlay, glitch effect"},
    {"label": "🌈 Krom", "desc": "chrome metallic mirror finish, rainbow reflection, beveled 3D text, glossy"},
    {"label": "⚡ Elektrik", "desc": "neon blue white lightning, electric arc animation, plasma glow, energy field"},
    {"label": "🎮 Piksel 8-bit", "desc": "pixel art retro style, 8-bit color palette, blocky shadow, scanlines"},
    {"label": "🌸 Sakura", "desc": "pink cherry blossom gradient, petal animation, soft glow, dreamy pastel"},
    {"label": "🤖 Cyberpunk", "desc": "neon yellow green on black, glitch animation, data stream, circuit board texture"},
    {"label": "💎 Kristal", "desc": "ice crystal clear glass, refraction light, frozen texture, diamond sparkle"},
]

# ─────────────────────────────────────────────
# 9. ANA FORM
# ─────────────────────────────────────────────
with st.form("main_form", clear_on_submit=False):
    r1c1, r1c2, r1c3 = st.columns([2, 2, 1])
    
    with r1c1:
        nick = st.text_input("✏️ Metin / Nick:", value="K3N4N", placeholder="Tasarlanacak yazı...")
    
    with r1c2:
        font_label = st.selectbox("🔤 Font Seç:", list(FONTS.keys()))
        font_name  = FONTS[font_label]
    
    with r1c3:
        font_size = st.number_input("📏 Boyut (px):", min_value=24, max_value=300, value=80, step=4)

    # Renk paleti seçici
    r2c1, r2c2 = st.columns([1, 2])
    with r2c1:
        palette_name = st.selectbox("🎨 Renk Paleti:", ["Serbest (AI seçsin)"] + list(COLOR_PRESETS.keys()))
    with r2c2:
        if palette_name != "Serbest (AI seçsin)":
            chips = COLOR_PRESETS[palette_name]
            chip_html = "".join(f'<span class="color-chip" title="{c}" style="background:{c}"></span>' for c in chips)
            st.markdown(f"<div style='padding-top:28px'>{chip_html}</div>", unsafe_allow_html=True)

    # Efekt seçici
    r3c1, r3c2 = st.columns(2)
    with r3c1:
        anim_type = st.selectbox("🎬 Animasyon Tipi:", [
            "Yok", "Soluk alma (pulse)", "Titreme (shake)",
            "Dönme (rotate)", "Sallanma (swing)", "Renk kayması (hue-rotate)",
            "Işık tarama (scan)", "Float (yukarı-aşağı)",
        ])
    with r3c2:
        text_effect = st.selectbox("🌟 Metin Efekti:", [
            "Normal", "3D Kabartma", "Neon Glow", "Outline (kontur)",
            "Çift kontur", "Drop Shadow", "İç gölge",
            "Text-stroke rainbow", "Hologram tarama",
        ])

    # Efekt presetleri
    st.markdown("**⚡ Hızlı Efekt Presetleri** *(Tarife otomatik eklenir)*")
    preset_cols = st.columns(5)
    selected_preset = ""
    for i, p in enumerate(EFFECT_PRESETS):
        if preset_cols[i % 5].checkbox(p["label"], key=f"preset_{i}"):
            selected_preset += p["desc"] + ", "

    # Tarif alanı
    user_desc = st.text_area(
        "📝 Özel Tasarım Tarifi:",
        placeholder="Nabla fontunda, gold sparkle parıltılı, yanıp sönen glow efektli, animasyonlu arka plan...",
        height=110,
    )

    # Ek seçenekler
    opt_c1, opt_c2, opt_c3, opt_c4 = st.columns(4)
    with opt_c1:
        add_bg_anim = st.checkbox("🌌 Arka plan animasyonu")
    with opt_c2:
        add_particles = st.checkbox("✨ Parçacık efekti")
    with opt_c3:
        add_shadow_box = st.checkbox("📦 Kutu / kart efekti")
    with opt_c4:
        multi_color_chars = st.checkbox("🌈 Her harf farklı renk")

    submit = st.form_submit_button("⚡ OMEGA MOTORLA TASARIM OLUŞTUR", use_container_width=True)

# ─────────────────────────────────────────────
# 10. YENİDEN KULLANIM: Hızlı preset uygula
# ─────────────────────────────────────────────
st.divider()
tab_main, tab_variations, tab_history, tab_favorites, tab_export = st.tabs([
    "🖼️ Önizleme", "🔀 Varyasyonlar", "📜 Geçmiş", "⭐ Favoriler", "📦 Export"
])

# ─────────────────────────────────────────────
# 11. AI ÇAĞRISI FONKSİYONU
# ─────────────────────────────────────────────
def build_system_prompt():
    return """Sen bir uzman HTML/CSS text efekt tasarımcısısın.
KURALAR:
1. SADECE geçerli HTML+CSS kodu üret. Hiçbir açıklama, markdown bloğu veya ``` işareti KULLANMA.
2. Zemin (body) her zaman BEYAZ (#fff) olacak. AI bunu değiştirme.
3. Metin tam ortada ve canvas'ı dolduracak şekilde büyük olsun.
4. @keyframes animasyonları dahil et.
5. Çoklu katmanlı efektler için ::before ::after pseudo-elementlerini kullan.
6. CSS custom properties (--var) kullanarak renk sistemi kur.
7. Eğer parçacık efekti istenirse JavaScript ile canvas veya DOM parçacıkları ekle.
8. Her zaman geçerli, hatasız, browser-uyumlu kod yaz.
9. Responsive: max-width kullanma, font-size büyük tut.
10. CSS filter, backdrop-filter, mix-blend-mode gibi ileri özellikleri kullan.
KESİNLİKLE: Yalnızca ham HTML kodu döndür, başka hiçbir şey."""

def build_user_prompt(nick, font, size, desc, palette, anim, effect, selected_preset,
                      add_bg_anim, add_particles, add_shadow_box, multi_color_chars):
    palette_str = ""
    if palette != "Serbest (AI seçsin)" and palette in COLOR_PRESETS:
        colors = COLOR_PRESETS[palette]
        palette_str = f"Renk paleti: {', '.join(colors)}"

    extras = []
    if add_bg_anim:   extras.append("arka planda güzel bir animasyonlu gradient veya mesh arka plan")
    if add_particles: extras.append("JavaScript ile uçuşan glitter/parçacık efekti (canvas veya DOM)")
    if add_shadow_box: extras.append("metnin etrafında neon glow border'lı yarı saydam bir kutu/kart")
    if multi_color_chars: extras.append("her harfi farklı renkte span ile sar ve her birine ayrı animasyon ver")

    return f"""Metin: "{nick}"
Font ailesi: {font}
Font boyutu: {size}px
{palette_str}
Animasyon tipi: {anim}
Metin efekti: {effect}
Preset efektler: {selected_preset}
Özel tarif: {desc}
Ekstra özellikler: {', '.join(extras) if extras else 'yok'}

Bu özellikleri tam olarak uygula ve mükemmel bir tasarım üret."""

def call_ai(nick, font, size, desc, palette, anim, effect, selected_preset,
            add_bg_anim, add_particles, add_shadow_box, multi_color_chars,
            model, temperature, max_tokens):
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user",   "content": build_user_prompt(
                    nick, font, size, desc, palette, anim, effect, selected_preset,
                    add_bg_anim, add_particles, add_shadow_box, multi_color_chars
                )},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        raw = resp.choices[0].message.content
        clean = re.sub(r"```(html|css|javascript)?", "", raw).replace("```", "").strip()
        return clean, None
    except Exception as e:
        return None, str(e)

def wrap_html(code, font_name, bg_color="#fff"):
    f_url = font_name.replace(" ", "+")
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family={f_url}&family=Nabla&family=Bungee+Spice&family=Orbitron:wght@900&display=swap" rel="stylesheet">
<style>
  html, body {{
    margin: 0; padding: 0;
    background: {bg_color};
    display: flex; justify-content: center; align-items: center;
    height: 100vh; overflow: hidden;
    font-family: '{font_name}', sans-serif;
  }}
</style>
</head>
<body>
{code}
</body>
</html>"""

# ─────────────────────────────────────────────
# 12. FORM İŞLEMİ
# ─────────────────────────────────────────────
if submit:
    with st.spinner("🤖 AI tasarım üretiyor..."):
        html_code, err = call_ai(
            nick, font_name, font_size, user_desc, palette_name,
            anim_type, text_effect, selected_preset,
            add_bg_anim, add_particles, add_shadow_box, multi_color_chars,
            model_choice, temperature, max_tokens
        )

    if err:
        st.error(f"❌ AI Hatası: {err}")
    else:
        st.session_state.current_html = html_code
        st.session_state.last_prompt  = user_desc
        st.session_state.generation_count += 1

        entry = {
            "nick":  nick,
            "font":  font_name,
            "size":  font_size,
            "desc":  user_desc,
            "html":  html_code,
            "ts":    time.strftime("%H:%M:%S"),
            "model": model_choice,
        }
        st.session_state.history.insert(0, entry)
        if len(st.session_state.history) > 50:
            st.session_state.history = st.session_state.history[:50]

        st.success(f'✅ Tasarım oluşturuldu! Model: `{model_choice}` | Saat: {entry["ts"]}')

# ─────────────────────────────────────────────
# 13. TAB 1 — ÖNİZLEME
# ─────────────────────────────────────────────
with tab_main:
    if st.session_state.current_html:
        entry = st.session_state.history[0] if st.session_state.history else {}

        col_prev, col_code = st.columns([1.6, 1])

        with col_prev:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <span style="font-family:Orbitron;font-size:.9rem;color:#ff00cc;">🖼️ ÖNİZLEME</span>
                <span class="badge badge-ok">CANLI</span>
                <span class="badge badge-ai">{entry.get('model','')}</span>
            </div>""", unsafe_allow_html=True)

            full_html = wrap_html(st.session_state.current_html,
                                  entry.get("font", font_name), custom_bg)
            st.components.v1.html(full_html, height=canvas_h)

        with col_code:
            st.markdown("<div style='font-family:Orbitron;font-size:.85rem;color:#3333ff;margin-bottom:8px;'>📄 KAYNAK KOD</div>", unsafe_allow_html=True)
            
            # Kaynak kodu sekmeli göster
            ct1, ct2 = st.tabs(["HTML+CSS", "Tam HTML"])
            with ct1:
                st.code(st.session_state.current_html, language="html")
            with ct2:
                st.code(wrap_html(st.session_state.current_html, entry.get("font", font_name)), language="html")

            # Aksiyon butonları
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                if st.button("⭐ Favoriye Ekle", key="fav_btn", use_container_width=True):
                    if len(st.session_state.favorites) < 20:
                        st.session_state.favorites.insert(0, st.session_state.history[0].copy())
                        st.success("Favorilere eklendi!")
                    else:
                        st.warning("Favori limiti: 20")
            with ac2:
                full_html_dl = wrap_html(st.session_state.current_html,
                                         entry.get("font", font_name))
                b64 = base64.b64encode(full_html_dl.encode()).decode()
                st.markdown(f"""
                <a href="data:text/html;base64,{b64}" download="kenan_tasarim.html"
                   style="display:block;text-align:center;background:linear-gradient(135deg,#3333ff,#ff00cc);
                          color:#fff;padding:10px;border-radius:10px;text-decoration:none;
                          font-family:Orbitron;font-size:.75rem;font-weight:700;">
                    ⬇️ HTML İNDİR
                </a>""", unsafe_allow_html=True)
            with ac3:
                if st.button("🔄 Yeniden Üret", key="regen_btn", use_container_width=True):
                    with st.spinner("Yeniden üretiliyor..."):
                        new_html, err2 = call_ai(
                            entry.get("nick","K3N4N"),
                            entry.get("font", font_name), entry.get("size", 80),
                            entry.get("desc",""), palette_name, anim_type, text_effect,
                            selected_preset, add_bg_anim, add_particles, add_shadow_box, multi_color_chars,
                            model_choice, temperature, max_tokens
                        )
                        if new_html:
                            st.session_state.current_html = new_html
                            st.session_state.history[0]["html"] = new_html
                            st.rerun()
    else:
        st.info("⬆️ Formu doldurup **OMEGA MOTORLA TASARIM OLUŞTUR** butonuna basın.")

# ─────────────────────────────────────────────
# 14. TAB 2 — VARYASYONLAR
# ─────────────────────────────────────────────
with tab_variations:
    st.markdown("### 🔀 Aynı Metni Farklı Stillerle Üret")
    if not st.session_state.current_html:
        st.info("Önce bir tasarım oluşturun.")
    else:
        var_count = st.radio("Kaç varyasyon?", [2, 3, 4], horizontal=True, index=1)
        var_fonts = st.multiselect("Varyasyon fontları:", list(FONTS.keys()),
                                    default=list(FONTS.keys())[:var_count])

        if st.button("🎲 Varyasyonları Üret", use_container_width=True):
            entry = st.session_state.history[0]
            var_htmls = []
            cols = st.columns(var_count)

            for i, vf_label in enumerate(var_fonts[:var_count]):
                vf_name = FONTS[vf_label]
                with cols[i]:
                    with st.spinner(f"Varyasyon {i+1} üretiliyor..."):
                        vhtml, _ = call_ai(
                            entry["nick"], vf_name, entry["size"],
                            entry["desc"] + f" varyasyon {i+1}",
                            palette_name, anim_type, text_effect, selected_preset,
                            add_bg_anim, False, False, False,
                            model_choice, temperature, max_tokens
                        )
                        if vhtml:
                            st.markdown(f"**{vf_label}**")
                            st.components.v1.html(wrap_html(vhtml, vf_name, custom_bg), height=280)
                            b64v = base64.b64encode(wrap_html(vhtml, vf_name).encode()).decode()
                            st.markdown(f'<a href="data:text/html;base64,{b64v}" download="var_{i+1}.html" '
                                        f'style="color:#00ffcc;font-size:.8rem;">⬇️ İndir</a>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 15. TAB 3 — GEÇMİŞ
# ─────────────────────────────────────────────
with tab_history:
    st.markdown("### 📜 Üretim Geçmişi")
    if not st.session_state.history:
        st.info("Henüz tasarım üretilmedi.")
    else:
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"#{i+1} — **{item['nick']}** | {item['font']} | {item['ts']}"):
                hc1, hc2 = st.columns([1.5, 1])
                with hc1:
                    st.components.v1.html(wrap_html(item["html"], item["font"]), height=220)
                with hc2:
                    st.code(item["html"][:600] + ("..." if len(item["html"])>600 else ""), language="html")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("⭐ Favoriye", key=f"fav_{i}"):
                            st.session_state.favorites.insert(0, item.copy())
                            st.success("Eklendi!")
                    with col_b:
                        b64h = base64.b64encode(wrap_html(item["html"], item["font"]).encode()).decode()
                        st.markdown(f'<a href="data:text/html;base64,{b64h}" download="gecmis_{i}.html" '
                                    f'style="color:#3333ff;font-size:.85rem;">⬇️ HTML İndir</a>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 16. TAB 4 — FAVORİLER
# ─────────────────────────────────────────────
with tab_favorites:
    st.markdown("### ⭐ Favori Tasarımlarım")
    if not st.session_state.favorites:
        st.info("Henüz favori eklenmedi. Önizleme sekmesinden ⭐ butonuna basın.")
    else:
        fav_cols = st.columns(2)
        for i, fav in enumerate(st.session_state.favorites):
            with fav_cols[i % 2]:
                st.markdown(f"**{fav['nick']}** — `{fav['font']}` — {fav.get('ts','')}")
                st.components.v1.html(wrap_html(fav["html"], fav["font"]), height=200)
                fc1, fc2 = st.columns(2)
                with fc1:
                    b64f = base64.b64encode(wrap_html(fav["html"], fav["font"]).encode()).decode()
                    st.markdown(f'<a href="data:text/html;base64,{b64f}" download="favori_{i}.html" '
                                f'style="color:#ffcc00;font-size:.8rem;">⬇️ HTML İndir</a>', unsafe_allow_html=True)
                with fc2:
                    if st.button("🗑️ Kaldır", key=f"del_fav_{i}"):
                        st.session_state.favorites.pop(i)
                        st.rerun()

# ─────────────────────────────────────────────
# 17. TAB 5 — EXPORT
# ─────────────────────────────────────────────
with tab_export:
    st.markdown("### 📦 Export & Paylaşım")
    if not st.session_state.current_html:
        st.info("Önce bir tasarım oluşturun.")
    else:
        entry = st.session_state.history[0] if st.session_state.history else {}

        ec1, ec2 = st.columns(2)
        with ec1:
            st.markdown("**🌐 Standalone HTML Dosyası**")
            st.markdown("Tüm fontlar ve stiller gömülü, çevrimdışı çalışan tek dosya.")
            full_export = wrap_html(st.session_state.current_html, entry.get("font", "Orbitron"))
            b64_export = base64.b64encode(full_export.encode()).decode()
            fname = f"kenan_{entry.get('nick','design').replace(' ','_')}.html"
            st.markdown(f"""
            <a href="data:text/html;base64,{b64_export}" download="{fname}"
               style="display:inline-block;background:linear-gradient(135deg,#3333ff,#6600cc);
                      color:#fff;padding:12px 28px;border-radius:10px;text-decoration:none;
                      font-family:Orbitron;font-size:.85rem;font-weight:700;">
                ⬇️ HTML DOSYASI İNDİR
            </a>""", unsafe_allow_html=True)

        with ec2:
            st.markdown("**📋 JSON Geçmiş Dışa Aktar**")
            st.markdown("Tüm üretim geçmişini JSON formatında indirin.")
            json_data = json.dumps(
                [{"nick":h["nick"],"font":h["font"],"size":h["size"],"desc":h["desc"],"ts":h["ts"]}
                 for h in st.session_state.history],
                ensure_ascii=False, indent=2
            )
            b64_json = base64.b64encode(json_data.encode()).decode()
            st.markdown(f"""
            <a href="data:application/json;base64,{b64_json}" download="gecmis.json"
               style="display:inline-block;background:linear-gradient(135deg,#006600,#00cc44);
                      color:#fff;padding:12px 28px;border-radius:10px;text-decoration:none;
                      font-family:Orbitron;font-size:.85rem;font-weight:700;">
                ⬇️ JSON OLARAK İNDİR
            </a>""", unsafe_allow_html=True)

        st.divider()
        st.markdown("**🔗 Embed Kodu**")
        st.markdown("Bu kodu herhangi bir web sitesine göm:")
        embed_b64 = base64.b64encode(full_export.encode()).decode()
        embed_code = f'<iframe src="data:text/html;base64,{embed_b64[:200]}..." width="800" height="400" frameborder="0"></iframe>'
        st.code(f'<!-- data:text/html formatında iframe olarak gömülebilir -->\n<!-- Ham HTML kodu kopyalayarak kullanın -->', language="html")
        st.code(full_export, language="html")

# ─────────────────────────────────────────────
# 18. ALT BİLGİ
# ─────────────────────────────────────────────
st.divider()
st.markdown(f"""
<div style="text-align:center;color:#333;font-family:Orbitron;font-size:.7rem;letter-spacing:2px;padding:12px 0;">
K3N4N VOICE Ω v30.0 &nbsp;|&nbsp; {len(FONTS)} Font &nbsp;|&nbsp; {len(EFFECT_PRESETS)} Preset &nbsp;|&nbsp; Groq AI Powered
</div>
""", unsafe_allow_html=True)
