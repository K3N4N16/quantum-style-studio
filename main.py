import streamlit as st
from groq import Groq
import random
import re

# --- 1. SİSTEM YAPILANDIRMASI ---
st.set_page_config(
    page_title="K3N4N QUANTUM v25.6 OMEGA MASTER",
    layout="wide",
    page_icon="♾️"
)

# Kenan Tasarım DNA'sı (Global UI)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Nabla&family=Bungee+Spice&family=Rampart+One&family=Sofia&family=Faster+One&family=Righteous&family=Nosifer&family=Creepster&family=Lobster&family=Kaushan+Script&display=swap');
    
    .stApp { background-color: #020205; color: #ffffff; }
    
    /* Beyaz Canvas Önizleme */
    iframe {
        background-color: #FFFFFF !important;
        border-radius: 15px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.6);
        border: 3px solid #7000ff;
    }
    
    /* Omega Buton Tasarımı */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ff00cc, #3333ff);
        color: white; border-radius: 10px; font-weight: 900; 
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px; height: 3.5rem; width: 100%;
        border: none; transition: 0.4s;
    }
    div.stButton > button:first-child:hover { 
        box-shadow: 0 0 35px #ff00cc; 
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API BAĞLANTISI ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Groq Cloud Key:", type="password")

if not api_key:
    st.info("Lütfen sidebar (yan panel) üzerinden Groq API anahtarınızı girin.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. YAN PANEL (SIDEBAR) ---
with st.sidebar:
    st.markdown("## ♾️ OMEGA v25.6")
    st.markdown("---")
    
    # Arşiv Fontları
    archive_fonts = ["Nabla", "Bungee Spice", "Rampart One", "Sofia", "Faster One", "Righteous", "Nosifer", "Creepster"]
    selected_font = st.selectbox("Arşiv Font Seçimi", archive_fonts)
    
    vibe = st.select_slider("Stil Şiddeti", options=["Nostalji", "Elite Pro", "Hyper Gold", "Omega Chaos"])
    st.success("Sistem: Kusursuz Render ✅")

# --- 4. ANA PANEL ---
st.markdown("<h1 style='text-align: center; font-family: Orbitron; color: #ff00cc;'>K3N4N <span style='color:#3333ff'>OMEGA</span> MASTER</h1>", unsafe_allow_html=True)

with st.form("master_render_form"):
    c1, c2 = st.columns([1, 1])
    with c1:
        nick = st.text_input("Nick / Metin:", value="K3N4N")
    with c2:
        source_ref = st.selectbox("Arşiv Kaynağı:", ["Ken1-Ken8 Karma", "Nostalji Arşiv", "Colors Special"])

    user_desc = st.text_area("Tasarım Tarifi:", 
                             placeholder="Nabla fontunda, Ken7 gold sparkle efektli, beyaz zeminde parlayan lüks bir nick...",
                             height=100)
    
    submit_btn = st.form_submit_button("⚡ TASARIMI OLUŞTUR")

# --- 5. RENDER MOTORU ---
if submit_btn:
    with st.spinner("Omega Render işlemi başlatıldı..."):
        
        # AI Prompt
        prompt = f"""
        Sen 'K3N4N OMEGA' sistemisin. Sadece HTML/CSS üret. Açıklama yapma. 
        Metin: '{nick}', Font: {selected_font}, Zemin: Beyaz (#FFFFFF).
        Ken1-Ken8 arşivindeki 'yanson', 'parla', 'rainbow' animasyonlarını ve 
        'background-clip: text' efektlerini beyaz zemine uygun şekilde kullan.
        """

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_desc}
                ]
            )
            
            output = completion.choices[0].message.content
            
            # GÜVENLİ TEMİZLİK: Regex hatasını önleyen yeni yapı
            # Markdown etiketlerini güvenle siler
            clean_code = re.sub(r"```(html|css)?", "", output)
            clean_code = clean_code.replace("```", "").strip()

            st.divider()
            
            p_col, s_col = st.columns([1.5, 1])
            
            with p_col:
                st.subheader("🖼️ Master Preview")
                
                # Font Import
                f_link = selected_font.replace(" ", "+")
                
                # Nihai HTML (Beyaz Canvas Wrapper)
                full_html = f"""
                <link href="https://fonts.googleapis.com/css2?family={f_link}&family=Nabla&family=Bungee+Spice&family=Rampart+One&family=Sofia&family=Faster+One&family=Nosifer&family=Creepster&display=swap" rel="stylesheet">
                <style>
                    body {{ 
                        margin: 0; background: #FFFFFF; 
                        display: flex; justify-content: center; align-items: center; 
                        height: 100vh; width: 100vw; overflow: hidden; 
                    }}
                </style>
                {clean_code}
                """
                st.components.v1.html(full_html, height=500)
            
            with s_col:
                st.subheader("📄 Source Code")
                st.code(clean_code, language="html")
                st.download_button("Dosyayı İndir (.html)", full_html, file_name=f"{nick}_omega.html")
                
        except Exception as e:
            st.error(f"Render Hatası: {str(e)}")
