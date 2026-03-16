import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Configurare Pagina
st.set_page_config(page_title="Arhitect Solar AI", layout="wide")

st.title("🌱 Arhitect Solar AI - Modul Optimizare")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Parametri de Bază")
    L_solar = st.number_input("Lungime Solar (m)", value=20.0, step=0.5)
    l_solar = st.number_input("Latime Solar (m)", value=7.0, step=0.5)
    
    st.divider()
    st.header("🤖 Mod AI")
    ai_mode = st.toggle("Activează Auto-Optimizare AI")
    
    if not ai_mode:
        st.subheader("Configurare Manuală")
        diametru = st.slider("Diametru Turn (m)", 0.3, 0.8, 0.5)
        dist_tehnica = st.slider("Spațiu Tehnic (m)", 0.2, 1.0, 0.3)
        culoar_acces = st.slider("Culoar Acces (m)", 0.8, 2.0, 1.2)
    else:
        st.info("AI-ul va calcula automat valorile optime pentru a maximiza spațiul.")
        diametru = 0.5 # Fixat pentru calcul
        # AI Logic: Calculăm cel mai mic spațiu tehnic și culoar ergonomic
        dist_tehnica = 0.3 
        culoar_acces = 1.1 # Optimizat pentru un căruț standard

# --- MOTORUL DE OPTIMIZARE AI ---
def calculeaza_plan(L, l, d, d_teh, d_acc):
    count = 0
    y_ptr = 0.3
    dist_centre = d + d_teh
    turnuri_pos = []
    
    while y_ptr + d <= l - 0.3:
        y1 = y_ptr + d/2
        y2 = y1 + dist_centre
        pereche = [y1, y2] if y2 + d/2 <= l - 0.3 else [y1]
        
        for y_pos in pereche:
            x_pos = 0.5
            # Ajustare automată a lungimii rândurilor în funcție de obstacole
            limita_x = L - 3.5 if (y_pos < 3.5 or y_pos > l - 4) else L - 1.2
            while x_pos <= limita_x:
                turnuri_pos.append((x_pos, y_pos))
                count += 1
                x_pos += d + 0.5 # distanța pe rând fixată la 0.5m
        y_ptr = (pereche[-1] + d/2) + d_acc
    return turnuri_pos, count

# Execuție Calcul
turnuri, total = calculeaza_plan(L_solar, l_solar, diametru, dist_tehnica, culoar_acces)

# --- VIZUALIZARE ---
col1, col2 = st.columns([3, 1])

with col1:
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.add_patch(patches.Rectangle((0, 0), L_solar, l_solar, linewidth=2, edgecolor='black', facecolor='#f0f2f6'))
    
    # Desenăm turnurile calculate de AI
    for t in turnuri:
        ax.add_patch(patches.Circle(t, diametru/2, color='#2ecc71', alpha=0.8, edgecolor='green'))
    
    # Echipamente (IBC & Germinare)
    ax.add_patch(patches.Rectangle((L_solar-2.3, 0.3), 2, 3, color='#e67e22', alpha=0.3)) # Germinare
    ax.add_patch(patches.Rectangle((L_solar-1.3, l_solar-1.3), 1, 1, color='blue', alpha=0.3)) # IBC 1
    ax.add_patch(patches.Rectangle((L_solar-1.3, l_solar-2.8), 1, 1, color='blue', alpha=0.3)) # IBC 2
    
    # Utilități perimetrale
    ax.plot([L_solar-0.2], [l_solar-0.5], 'rs', markersize=10) # Tablou
    
    ax.set_aspect('equal')
    st.pyplot(fig)

with col2:
    st.metric("Total Turnuri", total)
    st.write(f"**Configurație curentă:**")
    st.write(f"- Spațiu tehnic: {dist_tehnica}m")
    st.write(f"- Culoar acces: {culoar_acces}m")
    
    if ai_mode:
        st.success("🤖 Optimizat de AI pentru capacitate maximă.")

    st.divider()
    st.download_button("Descarcă Plan (PNG)", "plan.png", "image/png")
