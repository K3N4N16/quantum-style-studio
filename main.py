import streamlit as st
from groq import Groq
import random

# --- 1. OMEGA KONFİGÜRASYON ---
st.set_page_config(page_title="K3N4N QUANTUM v25.0 OMEGA", layout="wide", page_icon="♾️")

# Global UI (Omega Mode)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Nabla&family=Bungee+Spice&family=Rampart+One&family=Sofia&family=Faster+One&family=Righteous&display=swap');
    
    .stApp { background-color: #020205; color: #ffffff; }
    
    /* Beyaz Canvas (Contrast Mode) */
    iframe {
        background-color: #FFFFFF !important;
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        border: 4px solid #7000ff;
    }
    
    /* Profesyonel Kontrol Paneli */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ff00cc, #3333ff);
        color: white; border-radius: 50px; font-weight: 900; font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px; height: 3.5rem; transition: 0.5s;
    }
    div.stButton > button:first-child:hover { box-shadow: 0 0 40px #ff00cc; transform: scale(1.03); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API & ENGINE ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    with st.sidebar: api_key = st.text_input("Groq Cloud Key:", type="password")

if not api_key: st.stop()
client = Groq(api_key=api_key)

# --- 3. SIDEBAR: MASTER ARCHIVE CONTROLS ---
with st.sidebar:
    st.markdown("## ♾️ OMEGA ENGINE")
    archive_mode = st.toggle("Arşiv DNA'sını Kullan (Ken1-Ken8)", value=True)
    
    st.divider()
    # Arşivden süzülen en ikonik fontlar
    omega_fonts = ["Nabla", "Bungee Spice", "Rampart One", "Sofia", "Faster One", "Righteous", "Nosifer", "Orbitron"]
    selected_font = st.selectbox("Omega Font Library", omega_fonts)
    
    # Chaos & Nostalji Dengesi
    vibe_balance = st.select_slider("Vibe Balance", options=["Nostalji", "Modern Pro", "Enhanced Chaos", "Omega Chaos"])

    if st.button("🌀 SYNC ARCHIVE SEED"):
        st.session_state.seed = random.randint(111111, 999999)
        st.toast("Arşiv verileriyle senkronize edildi!")

# --- 4. ANA PANEL ---
st.markdown("<h1 style='text-align: center; font-family: Orbitron; color: #ff00cc;'>QUANTUM <span style='color:#3333ff'>V25.0</span> OMEGA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.5;'>Master Archive & Style Library Integration</p>", unsafe_allow_html=True)

with st.form("omega_form"):
    c1, c2 = st.columns([1, 1])
    with c1:
        nick_name = st.text_input("Nick / Metin:", value="K3N4N")
    with c2:
        preset = st.selectbox("Master Style Preset:", ["Arşivden Rastgele (Ken Style)", "Gold Sparkle Pro", "Neon Glitch V2", "Retro Nostalji"])

    user_description = st.text_area("Omega Tasarım Tarifi:", 
                                    placeholder="Örn: Ken7 dosyasındaki gold efektli, Nabla fontunda, beyaz zeminde parlayan bir lobi nicki...",
                                    height=100)
    
    submit = st.form_submit_button("⚡ GENERATE OMEGA DESIGN")

# --- 5. OMEGA AI LOGIC (ARŞİV ANALİZİ ENTEGRELİ) ---
if submit:
    with st.spinner("Arşiv dosyaları taranıyor ve Omega tasarım üretiliyor..."):
        
        # AI'ya tüm o CSS dosyalarındaki profesyonelliği talimat olarak veriyoruz
        omega_instruction = f"""
        Sen 'K3N4N OMEGA' tasarım motorusun. Elinde Ken1-Ken8, Colors ve Nostalji CSS arşivleri var.
        
        GÖREVİN:
        - '{nick_name}' için BEYAZ zeminde parlayacak bir sanat eseri üret.
        - Arşiv DNA'sı: {archive_mode} Aktif.
        - Stil Dengesi: {vibe_balance}.
        - Font: {selected_font}.
        
        TEKNİK KURALLAR (ARŞİVDEN):
        1. 'webkit-background-clip: text' ve 'color: transparent' kullanarak arşivdeki gradient/GIF efektlerini simüle et.
        2. Arşivdeki özel 'text-shadow' katmanlarını (örneğin Ken2'deki derinlikleri) kullan.
        3. Animasyonlarda '@keyframes yanson' ve 'parla' mantığını mutlaka ekle.
        4. Modern ve lüks bir görünüm için 'Gold Sparkle' ve 'Cyan Glow' tonlarını tercih et.
        5. Sadece kodu ver.
        """

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": omega_instruction},
                          {"role": "user", "content": user_description}]
            )
            
            result_code = completion.choices[0].message.content

            st.divider()
            p_col, s_col = st.columns([1.3, 1])
            
            with p_col:
                st.subheader("🖼️ Omega Preview (White Canvas)")
                # Arşivdeki tüm fontları import et
                st.markdown(f'<link href="https://fonts.googleapis.com/css2?family={selected_font.replace(" ", "+")}&family=Nabla&family=Bungee+Spice&family=Rampart+One&family=Sofia&family=Faster+One&display=swap" rel="stylesheet">', unsafe_allow_html=True)
                st.components.v1.html(result_code, height=550, scrolling=True)
            
            with s_col:
                st.subheader("📄 Omega Source")
                st.code(result_code, language="html")
                st.download_button("Dosyayı İndir (.html)", result_code, file_name=f"{nick_name}_omega.html")
        
        except Exception as e:
            st.error(f"Omega Engine Hatası: {e}")
