# --- 4. KONTROL PANELİ (SİDEBAR) ---
with st.sidebar:
    st.markdown("### 🎚️ TASARIM PARAMETRELERİ")
    
    # 1. Yazı Ayarları
    st.info("✍️ Metin Kontrolleri")
    custom_text = st.text_input("Yazılacak Metin:", value="K3N4N QUANTUM")
    font_size = st.slider("Yazı Boyutu (px):", 12, 120, 45)
    letter_spacing = st.slider("Harf Aralığı (px):", -5, 20, 2)
    
    # 2. Renk ve Işık
    st.divider()
    st.info("🌈 Renk & Işık")
    text_color = st.color_picker("Yazı Rengi:", "#00f2ff")
    glow_color = st.color_picker("Neon Rengi:", "#7000ff")
    glow_spread = st.slider("Neon Yayılımı (px):", 0, 50, 15)
    
    # 3. Arka Plan ve Çerçeve
    st.divider()
    st.info("🖼️ Arka Plan & Kenarlık")
    bg_mode = st.selectbox("Arka Plan Tipi:", ["Düz Renk", "Gradyan", "GIF / Video", "Cam (Glass)"])
    border_width = st.slider("Çerçeve Kalınlığı (px):", 0, 20, 2)
    border_radius = st.slider("Kenar Ovalleştirme (px):", 0, 100, 15)
    
    # 4. CHAOS MODU (Rastgelelik)
    st.divider()
    chaos_mode = st.button("🌀 CHAOS MODUNU TETİKLE")
    if chaos_mode:
        import random
        # Chaos modunda renkler ve boyutlar rastgele savrulur
        st.session_state.chaos_color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        st.toast("Quantum Chaos Aktif Edildi!", icon="🌀")

# --- 5. AI TASARIM ALANI (ANA EKRAN) ---
col_prompt, col_preview = st.columns([1, 1.2])

with col_prompt:
    st.markdown("### ✨ AI TASARIM SİHİRBAZI")
    ai_prompt = st.text_area(
        "Tasarımı Yapay Zekaya Tarif Et:",
        placeholder="Örn: Bursa'nın gece mavisi tonlarında, parlayan kenarlıklı, Matrix yağmuru efektli bir yazı stili...",
        height=200
    )
    
    # Gelişmiş Fonksiyon Anahtarları
    is_animated = st.toggle("Yazı Hareketli Olsun mu? (Pulse/Glitch)", value=True)
    add_particles = st.toggle("Arka Plana Parçacık Efekti Ekle", value=False)
    
    generate_btn = st.button("🚀 QUANTUM KODU ÜRET")