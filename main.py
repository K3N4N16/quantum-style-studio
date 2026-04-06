import streamlit as st
from groq import Groq
import re

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(
    page_title="K3N4N VOICE OMEGA v27.2",
    layout="wide",
    page_icon="🎙️"
)

# HTML/JS: Sesli Komut ve Arayüz Tasarımı
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Nabla&family=Bungee+Spice&display=swap');
    
    .stApp { background-color: #020205; color: #ffffff; }
    
    /* Ses Butonu */
    .mic-wrap {
        text-align: center;
        padding: 20px;
    }
    .mic-button {
        background: linear-gradient(135deg, #ff0000 0%, #770000 100%);
        color: white; border: none; padding: 18px 40px;
        border-radius: 50px; font-weight: bold; cursor: pointer;
        font-family: 'Orbitron', sans-serif;
        box-shadow: 0 0 20px rgba(255,0,0,0.4);
        font-size: 1.1rem;
        transition: 0.3s;
    }
    .mic-button:active { transform: scale(0.95); background: #ff4444; }
    .listening { animation: pulse-red 1.5s infinite; background: #ff0000 !important; }
    
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 20px rgba(255, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
    }

    /* Beyaz Canvas */
    iframe { background-color: #FFFFFF !important; border-radius: 15px; border: 3px solid #7000ff; }
    </style>

    <script>
    function runVoice() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'tr-TR';
        
        const btn = document.getElementById('voice-btn');
        btn.innerHTML = "🔴 DİNLENİYOR...";
        btn.classList.add('listening');

        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            // Metin kutusunu bul ve doldur
            const inputs = window.parent.document.querySelectorAll('textarea');
            inputs.forEach(el => {
                if(el.placeholder.includes("Nabla")) {
                    el.value = text;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
            });
            btn.innerHTML = "🎤 SESLİ KOMUT VER";
            btn.classList.remove('listening');
        };

        recognition.onerror = function() {
            btn.innerHTML = "⚠️ TEKRAR DENE";
            btn.classList.remove('listening');
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
        api_key = st.text_input("Groq API Key:", type="password")

if not api_key:
    st.info("Lütfen sidebar'dan API Key girin.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. ARAYÜZ ---
st.markdown("<h1 style='text-align: center; font-family: Orbitron; color: #ff00cc;'>K3N4N <span style='color:#3333ff'>VOICE</span> OMEGA</h1>", unsafe_allow_html=True)

# Ses Butonu (Doğrudan HTML)
st.markdown('<div class="mic-wrap"><button id="voice-btn" class="mic-button" onclick="runVoice()">🎤 SESLİ KOMUT VER</button></div>', unsafe_allow_html=True)

with st.form("omega_form"):
    col1, col2 = st.columns([1, 1])
    with col1: nick = st.text_input("Nick:", value="K3N4N")
    with col2: font = st.selectbox("Font:", ["Nabla", "Bungee Spice", "Sofia", "Faster One", "Righteous"])

    desc = st.text_area("Tasarım Tarifi:", placeholder="Nabla fontunda, Ken7 gibi gold parlasın...", height=100)
    render = st.form_submit_button("⚡ TASARIMI OLUŞTUR")

# --- 4. RENDER ---
if render:
    with st.spinner("Ses işleniyor ve render ediliyor..."):
        try:
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Sadece HTML/CSS üret. Beyaz zemin. Ken1-Ken8 arşiv efektlerini kullan. Açıklama yapma."},
                    {"role": "user", "content": f"Metin: {nick}, Font: {font}, Tarif: {desc}"}
                ]
            )
            code = re.sub(r"```(html|css)?", "", chat.choices[0].message.content).replace("```", "").strip()
            
            st.divider()
            c1, c2 = st.columns([1.5, 1])
            with c1:
                f_url = font.replace(" ", "+")
                full_html = f"""
                <link href="https://fonts.googleapis.com/css2?family={f_url}&family=Nabla&family=Bungee+Spice&display=swap" rel="stylesheet">
                <style>body{{margin:0; background:#FFF; display:flex; justify-content:center; align-items:center; height:100vh; overflow:hidden;}}</style>
                {code}
                """
                st.components.v1.html(full_html, height=500)
            with c2:
                st.code(code, language="html")
        except Exception as e:
            st.error(f"Hata: {e}")
