import streamlit as st
from groq import Groq
import re

# --- 1. GLOBAL UI & SİSTEM KONFİGÜRASYONU ---
st.set_page_config(
    page_title="K3N4N VOICE OMEGA v27.0",
    layout="wide",
    page_icon="🎙️"
)

# Web Speech API ve Kenan Style Tasarım Kodları
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Nabla&family=Bungee+Spice&family=Rampart+One&family=Sofia&family=Faster+One&family=Nosifer&family=Creepster&family=Righteous&display=swap');
    
    .stApp { background-color: #020205; color: #ffffff; }
    
    /* Sesli Komut Buton Stili */
    .mic-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    .mic-btn {
        background: linear-gradient(135deg, #ff0000 0%, #880000 100%);
        color: white; border: none; padding: 20px 40px;
        border-radius: 50px; font-weight: bold; cursor: pointer;
        font-family: 'Orbitron', sans-serif; transition: 0.4s;
        box-shadow: 0 0 25px rgba(255,0,0,0.5);
        font-size: 1.2rem;
    }
    .mic-btn:hover { box-shadow: 0 0 50px #ff0000; transform: scale(1.05); }
    .mic-active { animation: breathing 1s infinite alternate; background: #ff4444; }
    
    @keyframes breathing {
        from { transform: scale(1.05); box-shadow: 0 0 20px #ff0000; }
        to { transform: scale(1.1); box-shadow: 0 0 60px #ff0000; }
    }

    /* Beyaz Canvas (Önizleme) */
    iframe {
        background-color: #FFFFFF !important;
        border-radius: 20px;
        box-shadow: 0 25px 70px rgba(0,0,0,0.6);
        border: 4px solid #7000ff;
    }
    </style>

    <script>
    function startVoice() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'tr-TR';
        recognition.interimResults = false;
        
        const micBtn = document.getElementById('mic-trigger');
        micBtn.innerHTML = "🔴 DİNLİYORUM... KONUŞUN";
        micBtn.classList.add('mic-active');

        recognition.onresult = function(event) {
            const result = event.results[0][0].transcript;
            // Streamlit textarea'yı bulup sesi metin olarak yazdırıyoruz
            const ta = window.parent.document.querySelector('textarea[aria-label="Tasarım Tarifi:"]');
            if (ta) {
                ta.value = result;
                ta.dispatchEvent(new Event('input', { bubbles: true }));
            }
            micBtn.innerHTML = "🎤 SESLİ KOMUT VER (Tıkla)";
            micBtn.classList.remove('mic-active');
        };

        recognition.onerror = function() {
            micBtn.innerHTML = "❌ HATA OLUŞTU (Tekrar Dene)";
            micBtn.classList.remove('mic-active');
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
    st.info("Devam etmek için API Key giriniz.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. ANA PANEL ---
st.markdown("<h1 style='text-align: center; font-family: Orbitron; color: #ff00cc;'>QUANTUM <span style='color:#3333ff'>VOICE</span> v27.0</h1>", unsafe_allow_html=True)

# Mikrofon Butonu
st.markdown('<div class="mic-container"><button id="mic-trigger" class="mic-btn" onclick="startVoice()">🎤 SESLİ KOMUT VER (Tıkla ve Konuş)</button></div>', unsafe_allow_html=True)

with st.form("voice_render_form"):
    c1, c2 = st.columns([1, 1])
    with c1:
        nick_val = st.text_input("Görünecek Metin:", value="K3N4N")
    with c2:
        font_choice = st.selectbox("Baz Font:", ["Nabla", "Bungee Spice", "Sofia", "Rampart One", "Faster One", "Righteous"])

    user_prompt = st.text_area(
        "Tasarım Tarifi:", 
        placeholder="Mikrofon butonuna basıp konuşun veya buraya manuel yazın...",
        height=120
    )
    
    render_go = st.form_submit_button("⚡ TASARIMI OMEGA MOTORLA İŞLE")

# --- 4. RENDER ÇALIŞMASI ---
if render_go:
    with st.spinner("AI Sesinizi Arşiv DNA'sı ile birleştiriyor..."):
        
        system_logic = f"""
        Sen 'K3N4N OMEGA' sistemisin. Kullanıcının tarifine göre SADECE HTML/CSS üret.
        - Arşiv: Ken1-Ken8, Colors, Nostalji.
        - Nick: '{nick_val}'
        - Font: {font_choice}
        - Zemin: BEYAZ (#FFFFFF).
        - Efekt: yanson, parla, rainbow, gold_sparkle dokuları ve gölgeler kullan.
        Sadece kodu ver, açıklama yapma.
        """

        try:
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_logic},
                          {"role": "user", "content": user_prompt}]
            )
            
            raw_code = res.choices[0].message.content
            clean_code = re.sub(r"```(html|css)?", "", raw_code).replace("```", "").strip()

            st.divider()
            prev_col, source_col = st.columns([1.5, 1])
            
            with prev_col:
                st.subheader("🖼️ Sesli Render Sonucu")
                f_link = font_choice.replace(" ", "+")
                
                full_html = f"""
                <link href="https://fonts.googleapis.com/css2?family={f_link}&family=Nabla&family=Bungee+Spice&family=Sofia&family=Righteous&display=swap" rel="stylesheet">
                <style>
                    body {{ 
                        margin: 0; background: #FFFFFF; 
                        display: flex; justify-content: center; align-items: center; 
                        height: 100vh; width: 100vw; overflow: hidden; 
                    }}
                </style>
                {clean_code}
                """
                st.components.v1.html(full_html, height=550)
            
            with source_col:
                st.subheader("📄 Tasarım Kodu")
                st.code(clean_code, language="html")
                st.download_button("Kodları İndir", full_html, file_name=f"{nick_val}_voice_design.html")

        except Exception as e:
            st.error(f"Sistem Hatası: {e}")
