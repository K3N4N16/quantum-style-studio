import streamlit as st
from groq import Groq
import re

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(
    page_title="K3N4N VOICE v28.0",
    layout="wide",
    page_icon="🎙️"
)

# JAVASCRIPT & CSS: SESLİ KOMUT KÖPRÜSÜ
# Bu bölüm, tarayıcıyla doğrudan konuşur ve sesi textarea'ya zorla yazar.
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Nabla&family=Bungee+Spice&display=swap');
    
    .stApp { background-color: #020205; color: #ffffff; }
    
    .master-mic-container {
        background: rgba(255, 255, 255, 0.05);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #333;
        text-align: center;
        margin-bottom: 25px;
    }

    .mic-button-final {
        background: linear-gradient(135deg, #ff0000 0%, #770000 100%);
        color: white; border: none; padding: 25px 50px;
        border-radius: 60px; font-weight: bold; cursor: pointer;
        font-family: 'Orbitron', sans-serif;
        box-shadow: 0 0 30px rgba(255,0,0,0.4);
        font-size: 1.3rem;
        transition: all 0.3s;
    }

    .mic-button-final:hover { transform: scale(1.02); box-shadow: 0 0 50px #ff0000; }
    .is-listening { background: #ff4b4b !important; animation: blinker 1s linear infinite; }
    
    @keyframes blinker { 50% { opacity: 0.5; } }

    iframe { background-color: #FFFFFF !important; border-radius: 15px; border: 4px solid #7000ff; }
    </style>

    <script>
    function startVoiceEngine() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'tr-TR';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        const btn = document.getElementById('main-voice-btn');
        btn.innerHTML = "🔴 DİNLİYORUM... ŞİMDİ KONUŞUN";
        btn.classList.add('is-listening');

        recognition.onresult = function(event) {
            const resultText = event.results[0][0].transcript;
            // Streamlit'in textarea'sını DOM üzerinden bul ve değeri bas
            const streamlitDoc = window.parent.document;
            const textAreas = streamlitDoc.querySelectorAll('textarea');
            
            textAreas.forEach(area => {
                if(area.placeholder.includes("Nabla")) {
                    area.value = resultText;
                    // Streamlit'in değişikliği algılaması için event tetikle
                    area.dispatchEvent(new Event('input', { bubbles: true }));
                    area.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });

            btn.innerHTML = "🎤 SESLİ KOMUT BAŞARILI!";
            btn.classList.remove('is-listening');
            setTimeout(() => { btn.innerHTML = "🎤 SESLİ KOMUT VER"; }, 2000);
        };

        recognition.onerror = function(e) {
            console.error("Ses Hatası:", e.error);
            btn.innerHTML = "⚠️ HATA: " + e.error.toUpperCase();
            btn.classList.remove('is-listening');
            if(e.error === 'not-allowed') alert("Mikrofon izni reddedildi. Lütfen adres çubuğundaki kilit simgesinden izin verin.");
        };

        recognition.onend = function() {
            btn.classList.remove('is-listening');
        };

        recognition.start();
    }
    </script>
    """, unsafe_allow_html=True)

# --- 2. API YÖNETİMİ ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Groq Cloud Key:", type="password")

if not api_key:
    st.error("Lütfen API anahtarınızı girin.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. ARAYÜZ TASARIMI ---
st.markdown("<h1 style='text-align: center; font-family: Orbitron; color: #ff00cc;'>K3N4N <span style='color:#3333ff'>VOICE</span> OMEGA v28</h1>", unsafe_allow_html=True)

# Sesli Komut Alanı
st.markdown("""
    <div class="master-mic-container">
        <button id="main-voice-btn" class="mic-button-final" onclick="startVoiceEngine()">
            🎤 SESLİ KOMUT VER (Tıkla ve Konuş)
        </button>
        <p style="margin-top:15px; color:#aaa; font-family:sans-serif;">
            Not: Konuşmanız bittiğinde metin otomatik olarak aşağıya yazılacaktır.
        </p>
    </div>
    """, unsafe_allow_html=True)

with st.form("omega_render_form"):
    c1, c2 = st.columns([1, 1])
    with c1: 
        nick = st.text_input("Nick / Metin:", value="K3N4N")
    with c2: 
        font = st.selectbox("Baz Font:", ["Nabla", "Bungee Spice", "Sofia", "Faster One", "Righteous", "Nosifer"])

    # JS tarafından doldurulacak alan
    user_desc = st.text_area("Tasarım Tarifi:", placeholder="Nabla fontunda, Ken7 gibi gold sparkle parıltılı olsun...", height=120)
    
    submit = st.form_submit_button("⚡ TASARIMI OMEGA MOTORLA OLUŞTUR")

# --- 4. RENDER MOTORU ---
if submit:
    with st.spinner("AI Arşivden stilleri çekiyor..."):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sadece HTML/CSS üret. Açıklama yapma. Zemin BEYAZ. Ken1-Ken8 arşiv efektlerini kullan."},
                    {"role": "user", "content": f"Metin: {nick}, Font: {font}, Stil: {user_desc}"}
                ]
            )
            raw_code = completion.choices[0].message.content
            clean_code = re.sub(r"```(html|css)?", "", raw_code).replace("```", "").strip()

            st.divider()
            p_col, s_col = st.columns([1.5, 1])
            
            with p_col:
                st.subheader("🖼️ Önizleme (Beyaz Canvas)")
                f_url = font.replace(" ", "+")
                full_html = f"""
                <link href="https://fonts.googleapis.com/css2?family={f_url}&family=Nabla&family=Bungee+Spice&display=swap" rel="stylesheet">
                <style>body{{margin:0; background:#FFF; display:flex; justify-content:center; align-items:center; height:100vh; overflow:hidden;}}</style>
                {clean_code}
                """
                st.components.v1.html(full_html, height=550)
            
            with s_col:
                st.subheader("📄 Kaynak Kod")
                st.code(clean_code, language="html")
        except Exception as e:
            st.error(f"Hata: {e}")
