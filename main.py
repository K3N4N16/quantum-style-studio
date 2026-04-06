import streamlit as st
from groq import Groq
import random

# --- 1. SAYFA VE TEMA AYARLARI (En Üstte Olmalı!) ---
st.set_page_config(
    page_title="K3N4N QUANTUM STYLE STUDIO V20",
    layout="wide",
    page_icon="🎨"
)

# --- 2. GÖRSEL DOKUNUŞLAR (CYBERPUNK CSS) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp { background-color: #020205; color: #00f2ff; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Stili */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(#0a0a1a, #000000);
        border-right: 1px solid #00f2ff33;
    }

    /* Quantum Başlık Efekti */
    .quantum-header {
        background: linear-gradient(90deg, #00f2ff, #7000ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3.5rem;
        text-align: center;
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.4);
        margin-bottom: 20px;
    }
    
    /* Buton Tasarımı */
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #00f2ff, #7000ff);
        color: white; border: none; font-weight: bold;
        box-shadow: 0 4px 15px rgba(0, 242, 255, 0.3);
        transition: 0.3s;
        border-radius: 10px;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 30px #00f2ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. API KEY YÖNETİMİ (GÜVENLİK) ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    with st.sidebar:
        st.warning("⚠️ Secrets alanında API Key bulunamadı.")
        api_key = st.text_input("Groq API Key Manuel Girin:", type="password")

if not api_key:
    st.info("Lütfen Streamlit Secrets üzerinden veya Sidebar'dan API Key girin.")
    st.stop()

client = Groq(api_key=api_key)

# --- 4. KONTROL PANELİ (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🛡️ QUANTUM KONTROL")
    st.divider()
    
    # Metin ve Font Ayarları
    st.info("✍️ Metin Parametreleri")
    display_text = st.text_input("Görünecek Yazı:", value="K3N4N QUANTUM")
    font_family = st.selectbox("Font Seçimi", ["Orbitron", "Exo 2", "Righteous", "Monoton", "Bangers"])
    font_size = st.slider("Yazı Boyutu", 10, 150, 60)
    
    # Görsel Efektler
    st.divider()
    st.info("🌈 Görsel Efektler")
    glow_intensity = st.slider("Neon Parlaması", 0, 50, 15)
    border_radius = st.slider("Kenar Ovalleştirme", 0, 100, 15)
    bg_type = st.selectbox("Arka Plan Tipi", ["Transparan", "Gradyan", "GIF Arka Plan", "Cam Efekti"])
    
    # Chaos Modu
    st.divider()
    if st.button("🌀 QUANTUM CHAOS"):
        st.toast("Chaos Modu Aktif!", icon="🔥")
        # Chaos değerleri session_state üzerinden yönetilebilir

# --- 5. ANA EKRAN TASARIMI ---
st.markdown('<h1 class="quantum-header">QUANTUM STYLE STUDIO</h1>', unsafe_allow_html=True)
st.caption("AI Destekli Web Tasarım Laboratuvarı | Bursa Global Radio Hub")
st.divider()

col_input, col_output = st.columns([1, 1.2])

with col_input:
    st.markdown("### ✨ AI TASARIM SİHİRBAZI")
    user_prompt = st.text_area(
        "Hayalindeki tasarımı tarif et...",
        placeholder="Örn: Bursa'nın gece ışıkları gibi parlayan mor ve turkuaz bir çerçeve, içinde hareketli neon yazılar ve arka planda matrix yağmuru...",
        height=200
    )
    
    # Gelişmiş Filtreler
    c1, c2 = st.columns(2)
    with c1:
        is_animated = st.toggle("Hareketli Efektler", value=True)
        is_3d = st.toggle("3D Derinlik", value=False)
    with c2:
        add_gif = st.toggle("GIF Arka Plan", value=False)
        glass_mode = st.toggle("Cam (Glass) Efekti", value=True)

    generate_btn = st.button("🚀 TASARIMI OLUŞTUR")

# --- 6. AI MOTORU (GROQ GENERATION) ---
if generate_btn and user_prompt:
    with st.spinner("Quantum dalgalar kodlanıyor..."):
        try:
            # AI'ya verilen gizli yönetmen talimatı
            system_instruction = f"""
            Sen dünyanın en iyi CSS ve UI uzmanısın. Kullanıcının tarifine uygun muazzam bir tasarım yap.
            - Font: {font_family} (Google Fonts'tan otomatik çekilecek).
            - Yazı Boyutu: {font_size}px.
            - Kenar Yumuşatma: {border_radius}px.
            - Metin: '{display_text}'
            - Animasyon: {is_animated}.
            - 3D: {is_3d}.
            
            KURALLAR:
            1. Sadece TEK bir <div> içinde inline style veya <style> etiketiyle HTML ver.
            2. Arka plan tipine uygun (GIF: {add_gif}, Cam: {glass_mode}) modern CSS kullan.
            3. Metin animasyonları için CSS Keyframes ekle.
            4. Sadece kodu ver, açıklama yapma.
            """

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            generated_html = completion.choices[0].message.content

            with col_output:
                st.subheader("🖼️ Canlı Önizleme")
                # Google Fonts Import
                font_link = f'https://fonts.googleapis.com/css2?family={font_family.replace(" ", "+")}&display=swap'
                st.markdown(f'<link href="{font_link}" rel="stylesheet">', unsafe_allow_html=True)
                
                # HTML Render
                st.components.v1.html(generated_html, height=450, scrolling=True)
                
                with st.expander("📄 Kodu Kopyala (Okeyhane & Okey.com İçin)"):
                    st.code(generated_html, language="html")
        
        except Exception as e:
            st.error(f"📡 Quantum Hatası: {e}")

# --- 7. ALT BİLGİ ---
st.divider()
st.info("💡 **İpucu:** Prompt kısmına 'Kenarları parlayan bir cam kutu içinde altın rengi yazılar' gibi detaylar ekleyebilirsin.")
