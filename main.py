import streamlit as st
from groq import Groq
import random

# --- 1. GLOBAL KONFİGÜRASYON ---
st.set_page_config(page_title="K3N4N QUANTUM v24.0 DOUBLE-ENGINE", layout="wide", page_icon="⚡")

# Profesyonel UI/UX Teması (Kaos & Pro Hibrit)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Black+Ops+One&family=Creepster&family=Nosifer&family=Audiowide&display=swap');
    
    .stApp { background-color: #010103; color: #ffffff; }
    
    /* Beyaz Önizleme Alanı İyileştirmesi */
    iframe {
        background-color: #FFFFFF !important;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,242,255,0.2);
        border: 2px solid #7000ff;
    }
    
    /* Buton ve Input Tasarımları */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #7000ff 0%, #00f2ff 100%);
        color: white; border-radius: 12px; font-weight: 800; font-family: 'Orbitron', sans-serif;
        text-transform: uppercase; letter-spacing: 2px; width: 100%; transition: 0.4s;
    }
    div.stButton > button:first-child:hover { box-shadow: 0 0 50px rgba(0, 242, 255, 0.7); transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API YÖNETİMİ ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Groq Cloud Key:", type="password")

if not api_key:
    st.stop()

client = Groq(api_key=api_key)

# --- 3. SIDEBAR: DOUBLE-ENGINE CONTROLS ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/64/experimental-clover.png", width=50)
    st.title("ENGINE v24.0")
    
    engine_mode = st.radio("Aktif Motor:", ["Hybrid (v7.0 + v4.5)", "v7.0 Ultimate Pro", "v4.5 Enhanced Kaos"])
    
    st.divider()
    font_pool = ["Orbitron", "Black Ops One", "Creepster", "Nosifer", "Audiowide", "Space Grotesk"]
    selected_font = st.selectbox("Font DNA Havuzu", font_pool)
    
    chaos_intensity = st.select_slider("Kaos Şiddeti", options=["Soft", "Medium", "Hardcore", "Insane"])

    if st.button("🌀 REGENERATE CHAOS SEED"):
        st.session_state.seed = random.randint(100000, 999999)
        st.toast(f"Yeni Seed: {st.session_state.seed}")

# --- 4. ANA PANEL ---
st.markdown("<h1 style='text-align: center; font-family: Orbitron; color: #00f2ff;'>QUANTUM <span style='color:#7000ff'>V24.0</span> HYBRID</h1>", unsafe_allow_html=True)

with st.form("pro_design_form"):
    c1, c2 = st.columns([1, 1])
    with c1:
        nick_name = st.text_input("Nick / Metin:", value="K3N4N")
    with c2:
        output_format = st.selectbox("Tasarım Amacı:", ["Web Nick", "Logo Design", "Button Art", "Glitch Banner"])

    user_description = st.text_area("Tasarım Vizyonu (V4.5 & V7.0 Hibrit):", 
                                    placeholder="Örn: Nosifer fontunda, akan kan efektli ama v7.0 cam panel içinde, neon vuruşlu bir tasarım...",
                                    height=100)
    
    submit_button = st.form_submit_button("⚡ GENERATE HYBRID DESIGN")

# --- 5. DOUBLE-ENGINE AI LOGIC ---
if submit_button:
    with st.spinner("İki motor senkronize ediliyor..."):
        
        system_prompt = f"""
        Sen 'K3N4N V7.0 PRO' ve 'V4.5 ENHANCED KAOS' projelerinin birleşiminden oluşan bir yapay zekasın. 
        
        GÖREVİN:
        - Kullanıcının tarifini bu iki projenin tekniklerini harmanlayarak hayata geçir.
        - Zemin her zaman BEYAZ (#FFFFFF) olacak, kontrastı buna göre ayarla.
        - Motor Modu: {engine_mode}
        - Font Havuzu: {selected_font} (V4.5'ten gelen Nosifer/Creepster gibi fontları çılgın tasarımlarda çekinmeden kullan).
        - Kaos Şiddeti: {chaos_intensity}.
        
        TEKNİK TALİMATLAR:
        1. V4.5'in 'Enhanced Kaos' ruhunu (rastgele renkler, titreyen yazılar) ve V7.0'ın 'Professional' dokunuşunu (3D, cam, keskin stroke) birleştir.
        2. CSS Keyframes ile akışkan animasyonlar ekle.
        3. Sadece kodu ver, konuşma yapma.
        """

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_description}]
            )
            
            result_code = completion.choices[0].message.content

            st.divider()
            p_col, s_col = st.columns([1.3, 1])
            
            with p_col:
                st.subheader("🖼️ Hybrid Preview (Contrast Mode)")
                st.markdown(f'<link href="https://fonts.googleapis.com/css2?family={selected_font.replace(" ", "+")}&display=swap" rel="stylesheet">', unsafe_allow_html=True)
                st.components.v1.html(result_code, height=500, scrolling=True)
            
            with s_col:
                st.subheader("📄 Hybrid Code")
                st.code(result_code, language="html")
                st.download_button("İndir (.html)", result_code, file_name=f"{nick_name}_hybrid_v24.html")
        
        except Exception as e:
            st.error(f"Engine Failure: {e}")
