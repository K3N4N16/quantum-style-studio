import streamlit as st
from groq import Groq
import random
import re

# --- 1. OMEGA KONFİGÜRASYON ---
st.set_page_config(page_title="K3N4N QUANTUM v25.1 OMEGA", layout="wide", page_icon="♾️")

# Global UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Nabla&family=Bungee+Spice&family=Rampart+One&family=Sofia&family=Faster+One&family=Righteous&family=Nosifer&family=Creepster&display=swap');
    
    .stApp { background-color: #020205; color: #ffffff; }
    
    /* Beyaz Canvas (Contrast Mode) */
    iframe {
        background-color: #FFFFFF !important;
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        border: 4px solid #7000ff;
    }
    
    /* Profesyonel Buton */
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
    st.markdown("## ♾️ OMEGA ENGINE v25.1")
    st.info("⚠️ Hata Giderildi: Önizleme artık sadece saf kodu işliyor.")
    
    omega_fonts = ["Nabla", "Bungee Spice", "Rampart One", "Sofia", "Faster One", "Righteous", "Nosifer", "Creepster", "Orbitron"]
    selected_font = st.selectbox("Omega Font Library", omega_fonts)
    
    vibe_balance = st.select_slider("Vibe Balance", options=["Nostalji", "Modern Pro", "Enhanced Chaos", "Omega Chaos"])

    if st.button("🌀 SYNC ARCHIVE SEED"):
        st.session_state.seed = random.randint(111111, 999999)
        st.toast("Arşiv DNA'sı Senkronize Edildi!")

# --- 4. ANA PANEL ---
st.markdown("<h1 style='text-align: center; font-family: Orbitron; color: #ff00cc;'>QUANTUM <span style='color:#3333ff'>V25.1</span> OMEGA</h1>", unsafe_allow_html=True)

with st.form("omega_form"):
    c1, c2 = st.columns([1, 1])
    with c1:
        nick_name = st.text_input("Nick / Metin:", value="K3N4N")
    with c2:
        preset = st.selectbox("Master Style Preset:", ["Arşivden Rastgele", "Gold Sparkle Pro", "Neon Glitch V2", "Retro Nostalji"])

    user_description = st.text_area("Omega Tasarım Tarifi:", 
                                    placeholder="Nabla fontunda, Ken7'deki gold sparkle detaylı, beyaz zeminde parlayan lüks bir lobi nicki...",
                                    height=100)
    
    submit = st.form_submit_button("⚡ GENERATE OMEGA DESIGN")

# --- 5. OMEGA AI LOGIC (STRICT RENDER) ---
if submit:
    with st.spinner("Omega dalgalar beyaz canvas üzerinde temizleniyor..."):
        
        system_prompt = f"""
        SEN BİR CSS ÜRETİM OTOMATISIN. 
        SADECE VE SADECE ÇALIŞAN HTML/CSS KODU VER. 
        ASLA "İşte kodunuz", "Bu tasarım şöyledir" GİBİ CÜMLELER KURMA. 
        MARKDOWN (```css veya ```html) ETİKETLERİ KULLANMA. 
        
        TEKNİK VERİLER:
        - Nick: '{nick_name}'
        - Font: {selected_font}
        - Zemin: #FFFFFF (Beyaz)
        - Arşiv Referansları: Ken1-Ken8, Nostalji.css.
        - Stil: {vibe_balance} ve {preset}.
        
        İSTİSNA: Kodun içine tüm keyframe'leri ve font importlarını dahil et. 
        Metni dikey ve yatayda ortalayan bir flex konteynır kullan.
        """

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_description}]
            )
            
            raw_code = completion.choices[0].message.content
            
            # Markdown temizleyici (Eğer AI yine de ``` kullanırsa diye güvenlik önlemi)
            clean_code = re.sub(r'
http://googleusercontent.com/immersive_entry_chip/0

### 🛠️ Neyi Düzelttik?
1.  **Markdown Temizleyici (Regex):** AI bazen alışkanlıktan dolayı kodu ` ```html ` içine alıyor. Yazdığım `re.sub` fonksiyonu bu etiketleri görüp anında siliyor. Sadece saf kod kalıyor.
2.  **Flexbox Center:** Önizleme alanının içinde metnin bazen köşeye kaçmasını engellemek için `display: flex` ile tam merkeze sabitledim. Artık beyaz canvasın tam ortasında parlayacak.
3.  **Strict Prompt:** AI'ya "Konuşma, sadece kodu ver" talimatını verdik.

Yönetmenim, bu kodu güncelle; o az önceki "kodun kendisinin görünmesi" hatası tamamen ortadan kalkacak ve karşında tertemiz, parıl parıl bir sanat eseri duracak! 🎙️💎✨
