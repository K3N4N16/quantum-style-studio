import streamlit as st
from groq import Groq
import random

# --- 1. PRO KONFİGÜRASYON ---
st.set_page_config(
    page_title="K3N4N QUANTUM PRO v21",
    layout="wide",
    page_icon="⚡"
)

# Profesyonel Dark Mod & Mobil Uyum CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=Orbitron:wght@400;900&display=swap');
    
    .stApp { background-color: #050508; color: #ffffff; }
    
    /* Mobil Öncelikli Butonlar */
    .stButton>button {
        width: 100%;
        height: 3.5rem;
        background: linear-gradient(135deg, #00f2ff 0%, #7000ff 100%);
        color: white; border: none; font-weight: 700;
        border-radius: 12px; font-size: 1.1rem;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:active { transform: scale(0.95); }
    
    /* Text Area Optimizasyonu */
    .stTextArea textarea {
        background-color: #0a0a15 !important;
        color: #00f2ff !important;
        border: 1px solid #1a1a3a !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API & AUTH ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Groq Cloud Key:", type="password")

if not api_key:
    st.stop()

client = Groq(api_key=api_key)

# --- 3. SİSTEM HAFIZASI (SESSION STATE) ---
if 'chaos_seed' not in st.session_state:
    st.session_state.chaos_seed = "QUANTUM-001"

# --- 4. SIDEBAR: PROFESSIONAL CONTROLS ---
with st.sidebar:
    st.markdown("## ⚙️ STUDIO SETTINGS")
    
    selected_font = st.selectbox("Font Library", ["Orbitron", "Inter", "Space Grotesk", "Fira Code", "Bangers"])
    design_depth = st.select_slider("Design Depth", options=["Flat", "Layered", "3D Ultra", "Hyper-Chaos"])
    
    st.divider()
    # Chaos Seed Motoru (Tamir Edildi)
    if st.button("🌀 REGENERATE CHAOS SEED"):
        st.session_state.chaos_seed = f"QS-{random.randint(100000, 999999)}"
        st.success(f"Seed: {st.session_state.chaos_seed}")

# --- 5. ANA PANEL ---
st.markdown("<h1 style='text-align: center; letter-spacing: 5px; font-family: Orbitron;'>QUANTUM <span style='color:#00f2ff'>PRO</span> v21</h1>", unsafe_allow_html=True)

col_input, col_output = st.columns([1, 1.3])

with col_input:
    st.markdown("### 🧬 DESIGN PROMPT")
    # Kullanıcı sadece yazar ve aşağıdaki butona basar (Enter/Ctrl+Enter bağımlılığı yok)
    user_input = st.text_area("Tasarım stilini belirtin:", 
                              placeholder="Örn: Cyberpunk lila tonlarında, glitch efektli, keskin borderlı bir nick tasarımı...",
                              height=150, help="Mobil kullanıcılar için metni yazıp direkt aşağıdaki butona basmanız yeterlidir.")
    
    display_name = st.text_input("Nick / Metin:", value="K3N4N")
    
    generate_btn = st.button("⚡ GENERATE DESIGN")

# --- 6. AI ENGINE (V7.0 DNA + PRO UX) ---
if generate_btn and user_input:
    with st.spinner("Quantum Engine Processing..."):
        
        # AI'ya verilen "Professional Global" Talimatı
        pro_instruction = f"""
        Sen üst düzey bir dijital tasarımcı ve CSS mühendisisin. 
        Müşteri için 'Global High-End' standartlarında bir nick tasarımı üret.
        - Nick: '{display_name}'
        - Ana Stil: {user_input}
        - Font: {selected_font}
        - Karmaşıklık Seviyesi: {design_depth}
        - Seed: {st.session_state.chaos_seed}

        TEKNİK ŞARTLAR:
        1. Sadece TEK BİR <div> içinde, modern CSS (Glassmorphism, 3D Transforms, Keyframe Animations) kullanarak tasarım yap.
        2. K3N4N V7.0 mimarisindeki 'clip-path' ve 'text-stroke' tekniklerini mutlaka uygula.
        3. Sonuç tamamen mobil uyumlu (responsive) olsun.
        4. Sadece kodu ver, konuşma yapma.
        """

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": pro_instruction},
                          {"role": "user", "content": user_input}]
            )
            
            output_code = completion.choices[0].message.content

            with col_output:
                st.subheader("🖼️ STUDIO PREVIEW")
                # Font Import
                st.markdown(f'<link href="https://fonts.googleapis.com/css2?family={selected_font.replace(" ", "+")}:wght@400;900&display=swap" rel="stylesheet">', unsafe_allow_html=True)
                
                # HTML Render
                st.components.v1.html(output_code, height=550, scrolling=True)
                
                with st.expander("📋 VIEW SOURCE CODE"):
                    st.code(output_code, language="html")
        
        except Exception as e:
            st.error(f"Engine Error: {e}")

# --- 7. FOOTER ---
st.divider()
st.markdown("<p style='text-align: center; color: #444; font-size: 0.8rem;'>QUANTUM PRO v21.0 | POWERED BY GROQ & V7.0 DNA</p>", unsafe_allow_html=True)
