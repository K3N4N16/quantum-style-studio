import streamlit as st
from groq import Groq

# --- 1. SAYFA VE TEMA YAPILANDIRMASI ---
st.set_page_config(
    page_title="K3N4N QUANTUM V20 - V7.0 HYBRID",
    layout="wide",
    page_icon="💎"
)

# V7.0 Temalı Arayüz CSS
st.markdown("""
    <style>
    .stApp { background-color: #020205; color: #00f2ff; }
    [data-testid="stSidebar"] { background-image: linear-gradient(#05051a, #000000); border-right: 2px solid #7000ff33; }
    .stButton>button {
        background: linear-gradient(90deg, #00f2ff, #7000ff);
        color: white; border: none; font-weight: 800;
        border-radius: 5px; box-shadow: 0 0 15px rgba(0, 242, 255, 0.3);
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 0 30px #00f2ff; }
    .quantum-label { font-family: 'Orbitron', sans-serif; color: #7000ff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API GÜVENLİĞİ ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Groq API Key:", type="password")

if not api_key:
    st.info("Lütfen Secrets veya Sidebar üzerinden API Key giriniz.")
    st.stop()

client = Groq(api_key=api_key)

# --- 3. SIDEBAR: V7.0 KONTROL PARAMETRELERİ ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/64/quantum-glance.png", width=50)
    st.title("V7.0 DNA ENGINE")
    
    st.markdown("### 🎚️ Manuel Dokunuşlar")
    font_choice = st.selectbox("Font Ailesi", ["Orbitron", "Press Start 2P", "VT323", "Space Grotesk", "Fira Code"])
    base_size = st.slider("Yazı Boyutu", 20, 150, 70)
    
    st.divider()
    st.markdown("### 🧬 V7.0 Modülleri")
    v7_mode = st.multiselect("Aktif Edilecek DNA Parçaları:", 
                             ["Neon Glow v7", "3D Chaos Transform", "Gradient Border", "Glassmorphism Pro", "Text Stroke"],
                             default=["Neon Glow v7", "3D Chaos Transform"])
    
    if st.button("🌀 CHAOS SEED ÜRET"):
        st.session_state.chaos_seed = f"v7-{random.randint(1000, 9999)}"
        st.toast("Chaos Seed Güncellendi!")

# --- 4. ANA PANEL: AI TASARIM ÜSSÜ ---
st.markdown("<h1 style='text-align: center; color: #00f2ff; font-family: Orbitron;'>K3N4N QUANTUM V20 <span style='color:#7000ff'>V7.0 HYBRID</span></h1>", unsafe_allow_html=True)
st.caption("<p style='text-align: center;'>V7.0 Ultimate Pro Algoritmaları ile Güçlendirilmiş Yapay Zeka</p>", unsafe_allow_html=True)

col_input, col_output = st.columns([1, 1.2])

with col_input:
    st.markdown("### ✍️ Tasarım Direktifi")
    prompt = st.text_area("Hayalindeki tasarımı tarif et...", 
                          placeholder="Örn: Bursa gecesi moru, yanıp sönen neon kenarlar, cam panel ve 3D eğimli yazı...",
                          height=220)
    
    st.markdown("### 🎭 Stil Ayarları")
    c1, c2 = st.columns(2)
    with c1:
        use_gif = st.toggle("GIF Arka Plan", value=True)
        is_glitch = st.toggle("Glitch Efekti", value=False)
    with c2:
        is_mobile = st.toggle("Mobil Uyumlu", value=True)
        show_code = st.toggle("Kodları Göster", value=True)

    generate = st.button("🚀 QUANTUM MOTORUNU TETİKLE")

# --- 5. AI GENERATION (V7.0 DNA ENTEGRASYONU) ---
if generate and prompt:
    with st.spinner("V7.0 Algoritmaları işleniyor..."):
        # V7.0 Referans dosyasından alınan teknikleri AI'ya kural olarak veriyoruz
        v7_instructions = f"""
        Sen K3N4N V7.0 CSS Generator'ın yapay zeka versiyonusun. 
        Aşağıdaki teknik standartlara göre kod üret:
        - Kullanılan Font: {font_choice}. Yazı boyutu: {base_size}px.
        - Aktif Modüller: {', '.join(v7_mode)}.
        - Renk Paleti: Genelde #00f2ff (cyan), #7000ff (purple), #ff00ff (magenta) kullan.
        - Arka Plan: { 'GIF kullan (uygun bir URL bul)' if use_gif else 'Profesyonel Gradyan' }.
        - CSS Kuralları: 'webkit-text-stroke', 'backdrop-filter', 'clip-path' ve 'keyframes' animasyonlarını V7.0 standartlarında kullan.
        - Çıktı: Sadece bir <div> içinde, içinde 'K3N4N QUANTUM' yazan tek bir blok HTML/CSS kodu ver. Açıklama yapma.
        """
        
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": v7_instructions},
                    {"role": "user", "content": f"Tasarım Tarifi: {prompt}"}
                ]
            )
            
            raw_code = response.choices[0].message.content

            with col_output:
                st.subheader("🖼️ Quantum Önizleme")
                # Google Fonts Import
                font_url = f"https://fonts.googleapis.com/css2?family={font_choice.replace(' ', '+')}:wght@400;900&display=swap"
                st.markdown(f'<link href="{font_url}" rel="stylesheet">', unsafe_allow_html=True)
                
                # HTML Render
                st.components.v1.html(raw_code, height=500, scrolling=True)
                
                if show_code:
                    with st.expander("📄 V7.0 Standartlarında CSS/HTML Kodu"):
                        st.code(raw_code, language="html")
                        st.download_button("Dosyayı İndir (.html)", raw_code, file_name="quantum_v7_design.html")

        except Exception as e:
            st.error(f"Sistem Hatası: {str(e)}")

# --- 6. FOOTER ---
st.divider()
st.markdown("<p style='text-align: center; color: #333;'>Bursa Global Radio Hub | K3N4N Quantum Studio v20.0 Hybrid Edition</p>", unsafe_allow_html=True)
