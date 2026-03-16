import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configurare Pagina
st.set_page_config(page_title="Arhitect Solar AI v7", layout="wide")

# --- INITIALIZARE STATE (Memoria aplicatiei) ---
if 'pos_echipamente' not in st.session_state:
    st.session_state.pos_echipamente = "dreapta"
if 'last_cmd' not in st.session_state:
    st.session_state.last_cmd = ""

st.title("🌱 Arhitect Solar AI: Control Vocal/Text Optimizat")

# --- SIDEBAR: CONTROL PARAMETRI ---
with st.sidebar:
    st.header("🤖 Control AI Receptiv")
    # Folosim on_change pentru ca AI-ul sa raspunda imediat ce scrii
    user_cmd = st.text_input("Comandă (ex: 'stanga', 'dreapta', 'reset'):", key="input_cmd")
    
    if st.button("Execută Comanda AI") or (st.session_state.input_cmd != st.session_state.last_cmd):
        cmd = st.session_state.input_cmd.lower()
        if "stanga" in cmd or "stânga" in cmd:
            st.session_state.pos_echipamente = "stanga"
            st.success("Configurație mutată pe STÂNGA")
        elif "dreapta" in cmd:
            st.session_state.pos_echipamente = "dreapta"
            st.success("Configurație mutată pe DREAPTA")
        st.session_state.last_cmd = st.session_state.input_cmd

    st.divider()
    st.header("📏 Setări Manuale")
    L_solar = st.number_input("Lungime Solar (m)", value=23.5, step=0.5)
    l_solar = st.number_input("Latime Solar (m)", value=7.0, step=0.5)
    
    st.divider()
    max_turnuri = st.slider("Limită Turnuri", 10, 500, 150)
    diametru = st.slider("Diametru Turn (m)", 0.3, 0.8, 0.5)
    dist_pe_rand = st.slider("Spațiu între turnuri (m)", 0.1, 1.0, 0.5)
    culoar_acces = st.slider("Culoar Acces (m)", 0.8, 2.5, 1.2)

# --- MOTORUL DE CALCUL ---
def genereaza_plan_tehnic(L, l, d, d_rand, d_teh, d_acc, max_t, pos_echip):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_xlim(-1, L + 1)
    ax.set_ylim(-1, l + 1)
    
    # Fundal si Contur
    ax.add_patch(patches.Rectangle((0, 0), L, l, linewidth=3, edgecolor='black', facecolor='#fdfdfd', zorder=1))
    
    m_teava, m_cablu = 0, 0
    
    # Logică Poziționare AI
    if pos_echip == "dreapta":
        ibc_x, germ_x, tablou_x, mag_x = L-1.3, L-2.3, L-0.2, L-3.0
    else:
        ibc_x, germ_x, tablou_x, mag_x = 0.3, 0.3, 0.2, 3.0

    # Desenare Echipamente Fixe
    ax.add_patch(patches.Rectangle((ibc_x, l-1.3), 1, 1, color='blue', alpha=0.3, zorder=2)) # IBC 1
    ax.add_patch(patches.Rectangle((ibc_x, l-2.8), 1, 1, color='blue', alpha=0.3, zorder=2)) # IBC 2
    ax.add_patch(patches.Rectangle((germ_x, 0.3), 2, 3, color='#e67e22', alpha=0.2, zorder=2)) # Germinare
    ax.plot(tablou_x, l-0.5, 'rs', markersize=12, zorder=10) # Tablou

    # Magistrale
    ax.plot([ibc_x+0.5, mag_x], [l-0.8, l-0.8], color='blue', linewidth=2, zorder=3)
    ax.plot([mag_x, tablou_x], [l-0.5, l-0.5], color='red', linestyle='--', linewidth=2, zorder=3)

    # Calcul Turnuri
    count, y_ptr = 0, 0.5
    while y_ptr + d <= l - 0.3 and count < max_t:
        y1 = y_ptr + d/2
        y2 = y1 + d + d_teh
        pereche = [y1, y2] if y2 + d/2 <= l - 0.3 else [y1]
        
        for y_pos in pereche:
            x_start = 0.8 if pos_echip == "dreapta" else 3.5
            limita_x = L-3.5 if pos_echip == "dreapta" else L-0.8
            
            # Utilități rând
            ax.plot([x_start, mag_x], [y_pos, y_pos], color='blue', alpha=0.1, lw=1)
            ax.plot([x_start, mag_x], [y_pos+0.05, y_pos+0.05], color='red', alpha=0.1, ls='--', lw=1)
            
            m_teava += abs(mag_x - x_start)
            m_cablu += abs(mag_x - x_start)

            x_pos = x_start
            while x_pos <= limita_x and count < max_t:
                ax.add_patch(patches.Circle((x_pos, y_pos), d/2, color='#2ecc71', edgecolor='#27ae60', zorder=4))
                count += 1
                x_pos += d + d_rand
        
        y_ptr = (pereche[-1] + d/2) + d_acc

    ax.set_aspect('equal')
    return fig, count, m_teava, m_cablu

# --- AFIȘARE ---
col1, col2 = st.columns([4, 1])
with col1:
    fig, total, t_m, c_m = genereaza_plan_tehnic(L_solar, l_solar, diametru, dist_pe_rand, 0.3, culoar_acces, max_turnuri, st.session_state.pos_echipamente)
    st.pyplot(fig, use_container_width=True)

with col2:
    st.metric("Turnuri Totale", total)
    st.divider()
    st.subheader("📋 Necesar Materiale")
    st.write(f"💧 Teavă: **{t_m:.1f} m**")
    st.write(f"⚡ Cablu: **{c_m * 1.1:.1f} m**")
    st.caption("Configurație: " + st.session_state.pos_echipamente.upper())
