import streamlit as st
from groq import Groq
import random

# --- 1. GLOBAL KONFİGÜRASYON ---
st.set_page_config(
    page_title="K3N4N QUANTUM v22.0 PRO",
    layout="wide",
    page_icon="💎"
)

# Profesyonel UI/UX Teması
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Space+Grotesk:wght@300;700&display=swap');
    
    .stApp { background-color: #010103; color: #ffffff; }
    
    /* Input Alanları */
    .stTextArea textarea, .stTextInput input {
        background-color: #080812 !important;
        color: #00f2ff !important;
        border: 1px solid #1a1a3a !important;
        border-radius: 8px !important;
    }
    
    /* Parlayan Buton Efekti */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #00f2ff 0%, #7000ff 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: 800;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.2);
        width: 100%;
        transition: 0.4s all;
    }
    
    div.stButton > button:first-child:hover {
        box-shadow: 0 0 40px rgba(112, 0, 255, 0.6);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API YÖNETİMİ ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Groq Cloud Key:", type="password")

if not api_key:
    st.info("Sistemi başlatmak için API Key gereklidir.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. SIDEBAR: PROFESSIONAL ENGINE ---
with st.sidebar:
    st.markdown("### 🧬 QUANTUM CORE")
    font_family = st.selectbox("Font Core", ["Orbitron", "Space Grotesk", "Press Start 2P", "Fira Code"])
    complexity = st.select_slider("Chaos Level", options=["Balanced", "High", "Ultra", "God Mode"])
    
    st.divider()
    if st.button("🌀 RESET SEED"):
        st.session_state.seed = random.randint(1000, 9999)
        st.toast("Chaos Seed Yenilendi!")

# --- 4. ANA PANEL: DESIGN STUDIO ---
st.markdown("<h1 style='text-align: center; font-family: Orbitron; color: #00f2ff;'>QUANTUM <span style='color:#7000ff'>V22.0</span> STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.6;'>Professional Nick & Text Art Engine</p>", unsafe_allow_html=True)

# Form yapısı kullanımı: Enter veya butona basıldığında tek seferde çalışır
with st.form("design_form"):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        nick_name = st.text_input("Metin / Nickname:", value="K3N4N")
        
    with col2:
        style_preset = st.selectbox("Stil Şablonu (Opsiyonel):", ["Özel Tarif", "Cyberpunk Glitch", "Glassmorphism Pro", "Liquid Metal", "Neon Strike"])

    user_description = st.text_area("Tasarım Detayları (Vibe):", 
                                    placeholder="Örn: Siyah zemin üzerine, parlayan zümrüt yeşili kenarlar, 3D derinlik ve neon titremesi...",
                                    height=120)
    
    submit_button = st.form_submit_button("⚡ GENERATE DESIGN")

# --- 5. AI ENGINE (V7.0 HYBRID) ---
if submit_button:
    if not user_description:
        st.error("Lütfen bir stil tarifi yazın.")
    else:
        with st.spinner("Quantum dalgalar şekilleniyor..."):
            
            # V7.0 DNA'sını içeren profesyonel talimat
            system_prompt = f"""
            Sen dünyanın en gelişmiş UI/UX tasarımcısısın. 
            Müşterin için sadece CSS ve HTML kullanarak profesyonel bir metin sanatı üret.
            
            TEKNİK KRİTERLER:
            - Nick: '{nick_name}'
            - Tarif: {user_description}
            - Font: {font_family}
            - Karmaşıklık: {complexity}
            - Şablon: {style_preset}
            
            TASARIM KURALLARI:
            1. 'K3N4N V7.0' standartlarında 'text-stroke', 'clip-path' ve katmanlı 'drop-shadow' kullan.
            2. Arka planı her zaman fütüristik yap (Dark, Gradient veya uyumlu GIF).
            3. Metin animasyonları (Pulse, Hue-Rotate, Glitch) ekleyerek canlılık kat.
            4. Kod tek bir <div> bloğu içinde olmalı. Sadece kodu ver, asla konuşma.
            """

            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt},
                              {"role": "user", "content": user_description}]
                )
                
                result_code = completion.choices[0].message.content

                # ÇIKTI ALANI
                st.divider()
                prev_col, code_col = st.columns([1.2, 1])
                
                with prev_col:
                    st.subheader("🖼️ Studio Preview")
                    # Google Fonts Import
                    st.markdown(f'<link href="https://fonts.googleapis.com/css2?family={font_family.replace(" ", "+")}:wght@400;900&display=swap" rel="stylesheet">', unsafe_allow_html=True)
                    st.components.v1.html(result_code, height=450, scrolling=True)
                
                with code_col:
                    st.subheader("📄 Source Code")
                    st.code(result_code, language="html")
                    st.download_button("İndir (.html)", result_code, file_name=f"{nick_name}_quantum.html")
            
            except Exception as e:
                st.error(f"Engine Hatası: {e}")

# Footer
st.markdown("<p style='text-align: center; margin-top: 50px; opacity: 0.3;'>V22.0 Professional Edition | Powered by V7.0 DNA</p>", unsafe_allow_html=True)
