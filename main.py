import streamlit as st
from groq import Groq
import random

# --- 1. GLOBAL KONFİGÜRASYON ---
st.set_page_config(
    page_title="K3N4N QUANTUM v23.0 CONTRAST",
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
        color: white; border: none; padding: 1rem 2rem;
        border-radius: 12px; font-weight: 800;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase; letter-spacing: 2px;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.2);
        width: 100%; transition: 0.4s all;
    }
    
    div.stButton > button:first-child:hover {
        box-shadow: 0 0 40px rgba(112, 0, 255, 0.6);
        transform: translateY(-2px);
    }

    /* ÖNİZLEME ALANI BEYAZLAŞTIRMA (ÖZEL İSTEK) */
    iframe {
        background-color: #FFFFFF !important; /* Tertemiz Beyaz */
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border: 5px solid #1a1a3a;
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
    st.markdown("### 🧬 QUANTUM CORE v23")
    font_family = st.selectbox("Font Core", ["Orbitron", "Space Grotesk", "Press Start 2P", "Fira Code", "Kaushan Script"])
    complexity = st.select_slider("Chaos Level", options=["Balanced", "High", "Ultra", "God Mode"])
    
    st.divider()
    if st.button("🌀 RESET SEED"):
        st.session_state.seed = random.randint(1000, 9999)
        st.toast("Chaos Seed Yenilendi!")
    
    st.info("ℹ️ Önizleme alanı beyaz (Contrast Mode) olarak ayarlandı.")

# --- 4. ANA PANEL: DESIGN STUDIO ---
st.markdown("<h1 style='text-align: center; font-family: Orbitron; color: #00f2ff;'>QUANTUM <span style='color:#7000ff'>V23.0</span> STUDIO</h1>", unsafe_allow_html=True)

with st.form("design_form"):
    col1, col2 = st.columns([1, 1])
    with col1:
        nick_name = st.text_input("Metin / Nickname:", value="K3N4N")
    with col2:
        style_preset = st.selectbox("Stil Şablonu:", ["Özel Tarif", "Cyberpunk Glitch", "Liquid Metal", "Neon Strike", "Gold Luxury"])

    user_description = st.text_area("Tasarım Detayları (Vibe):", 
                                    placeholder="Beyaz zeminde parlayacak, keskin hatlı, 3D neon bir tasarım istiyorum...",
                                    height=100)
    
    submit_button = st.form_submit_button("⚡ GENERATE DESIGN")

# --- 5. AI ENGINE (V7.0 + MULTI-REF READY) ---
if submit_button:
    with st.spinner("Quantum dalgalar beyaz canvas üzerinde şekilleniyor..."):
        
        # Beyaz zemin için AI'ya kontrast uyarısı ekledim
        system_prompt = f"""
        Sen dünyanın en gelişmiş UI/UX tasarımcısısın. 
        K3N4N V7.0 mimarisini kullanarak profesyonel bir metin sanatı üret.
        
        KRİTİK NOT: Tasarım BEYAZ (#FFFFFF) bir zemin üzerinde sergilenecek. 
        Bu yüzden renk seçimlerini ve gölgeleri beyaz zeminde en net görünecek (kontrastı yüksek) şekilde ayarla.
        
        TEKNİK:
        - Nick: '{nick_name}'
        - Font: {font_family}
        - Karmaşıklık: {complexity}
        - Standartlar: 'text-stroke', 'clip-path', '3D transform' ve 'layered-shadows'.
        - Sadece kodu ver, konuşma yapma.
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
                st.subheader("🖼️ Contrast Studio Preview")
                st.markdown(f'<link href="https://fonts.googleapis.com/css2?family={font_family.replace(" ", "+")}:wght@400;900&display=swap" rel="stylesheet">', unsafe_allow_html=True)
                st.components.v1.html(result_code, height=450, scrolling=True)
            
            with code_col:
                st.subheader("📄 Source Code")
                st.code(result_code, language="html")
                st.download_button("İndir (.html)", result_code, file_name=f"{nick_name}_v23.html")
        
        except Exception as e:
            st.error(f"Engine Hatası: {e}")
