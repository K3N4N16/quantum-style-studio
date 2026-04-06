import streamlit as st
from groq import Groq
import random
import re

# --- 1. SİSTEM AYARLARI ---
st.set_page_config(
    page_title="K3N4N QUANTUM v25.5 OMEGA MASTER",
    layout="wide",
    page_icon="♾️"
)

# Kenan Arşiv Estetiği (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Nabla&family=Bungee+Spice&family=Rampart+One&family=Sofia&family=Faster+One&family=Righteous&family=Nosifer&family=Creepster&family=Lobster&family=Kaushan+Script&display=swap');
    
    .stApp { background-color: #020205; color: #ffffff; }
    
    /* Beyaz Önizleme Paneli */
    iframe {
        background-color: #FFFFFF !important;
        border-radius: 15px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.5);
        border: 3px solid #7000ff;
    }
    
    /* Profesyonel Buton Tasarımı */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #ff00cc, #3333ff);
        color: white; border-radius: 10px; font-weight: 900; 
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px; height: 3.5rem; width: 100%;
        border: none; transition: 0.4s;
    }
    div.stButton > button:first-child:hover { 
        box-shadow: 0 0 30px #ff00cc; 
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
    st.warning("Devam etmek için yan menüden API anahtarını girin.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. YAN MENÜ (SIDEBAR) ---
with st.sidebar:
    st.title("OMEGA v25.5")
    st.markdown("---")
    
    # Arşivden Font Seçimi
    archive_fonts = ["Nabla", "Bungee Spice", "Rampart One", "Sofia", "Faster One", "Righteous", "Nosifer", "Creepster"]
    selected_font = st.selectbox("Arşiv Font Havuzu", archive_fonts)
    
    vibe = st.select_slider("Tasarım Gücü", options=["Nostalji", "Elite Pro", "Hyper Gold", "Omega Chaos"])
    
    st.success("Sistem Durumu: Kusursuz ✅")

# --- 4. ANA EKRAN ---
st.markdown("<h1 style='text-align: center; font-family: Orbitron; color: #ff00cc;'>K3N4N <span style='color:#3333ff'>OMEGA</span> MASTER</h1>", unsafe_allow_html=True)

with st.form("omega_master_form"):
    col1, col2 = st.columns([1, 1])
    with col1:
        nick = st.text_input("Yazılacak Nick:", value="K3N4N")
    with col2:
        source = st.selectbox("Kaynak Arşivi:", ["Ken1-Ken8 Karma", "Nostalji.css", "Colors.css"])

    desc = st.text_area("Tasarım Tarifi (Vibe):", 
                        placeholder="Örn: Ken7'deki gold parıltısı olsun, beyaz zeminde Nabla fontuyla parlasın...",
                        height=100)
    
    generate = st.form_submit_button("⚡ TASARIMI RENDER ET")

# --- 5. ÜRETİM MOTORU ---
if generate:
    with st.spinner("Arşiv DNA'sı işleniyor..."):
        
        # AI Talimatı
        system_prompt = f"""
        Sadece HTML/CSS kodu üret. Açıklama yapma. 
        Nick: '{nick}', Font: {selected_font}, Zemin: Beyaz.
        Arşivdeki 'yanson', 'parla', 'rainbow' animasyonlarını mutlaka kullan.
        'background-clip: text' ve parıltılı efektleri Ken7-Ken8 dosyalarındaki gibi uygula.
        """

        try:
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": desc}
                ]
            )
            
            raw_code = chat.choices[0].message.content
            
            # Hatalı karakterleri ve markdown etiketlerini temizleme
            clean_code = re.sub(r"
http://googleusercontent.com/immersive_entry_chip/0

### 🛠️ Ne Yapman Gerekiyor?
1.  **Kodun tamamını kopyala.**
2.  Streamlit projenin içindeki `main.py` dosyasını aç.
3.  İçindeki her şeyi sil ve bu yeni kodu yapıştır.
4.  Kaydet ve çalıştır.

Bu sürümde o meşhur `SyntaxError` (yazım hatası) olan kısmı tamamen temizledim. Artık beyaz zeminde o efsane lobi nicklerini hatasız bir şekilde üretebilirsin! 🎙️💎✨
