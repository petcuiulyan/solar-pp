import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# --- CONFIGURARE PAGINA ---
st.set_page_config(page_title="Arhitect Solar AI v7", layout="wide")
st.title("🌱 Arhitect Solar AI: Control Vocal/Text Optimizat")

# --- INITIALIZARE STATE ---
if 'pos_echipamente' not in st.session_state:
    st.session_state.pos_echipamente = "dreapta"
if 'last_cmd' not in st.session_state:
    st.session_state.last_cmd = ""
if 'last_params' not in st.session_state:
    st.session_state.last_params = ""

# --- SIDEBAR ---
with st.sidebar:
    st.header("🤖 Control AI Receptiv")
    user_cmd = st.text_input("Comandă (ex: 'stanga', 'dreapta', 'reset'):", key="input_cmd")
    
    if st.button("Execută Comanda AI") or (st.session_state.input_cmd != st.session_state.last_cmd):
        cmd = st.session_state.input_cmd.lower()
        if "stanga" in cmd or "stânga" in cmd:
            st.session_state.pos_echipamente = "stanga"
            st.success("Configurație mutată pe STÂNGA")
        elif "dreapta" in cmd:
            st.session_state.pos_echipamente = "dreapta"
            st.success("Configurație mutată pe DREAPTA")
        elif "reset" in cmd:
            st.session_state.pos_echipamente = "dreapta"
            st.info("Configurație RESETATĂ la DREAPTA")
        st.session_state.last_cmd = cmd

    st.divider()
    st.header("📏 Setări Manuale")
    L_solar = st.number_input("Lungime Solar (m)", value=23.5, step=0.5)
    l_solar = st.number_input("Latime Solar (m)", value=7.0, step=0.5)
    
    st.divider()
    max_turnuri = st.slider("Limită Turnuri", 10, 500, 150)
    diametru = st.slider("Diametru Turn (m)", 0.3, 0.8, 0.5)
    dist_pe_rand = st.slider("Spațiu între turnuri (m)", 0.1, 1.0, 0.5)
    culoar_acces = st.slider("Culoar Acces (m)", 0.8, 2.5, 1.2)

# --- FUNCTII UTILE ---
def deseneaza_echipamente(ax, pos_echip, L, l):
    """Deseneaza echipamente fixe și returnează coordonata magistralei"""
    if pos_echip == "dreapta":
        ibc_x, germ_x, tablou_x, mag_x = L-1.3, L-2.3, L-0.2, L-3.0
    else:
        ibc_x, germ_x, tablou_x, mag_x = 0.3, 0.3, 0.2, 3.0

    # IBC-uri
    ax.add_patch(patches.Rectangle((ibc_x, l-1.3), 1, 1, color='blue', alpha=0.3, zorder=2))
    ax.add_patch(patches.Rectangle((ibc_x, l-2.8), 1, 1, color='blue', alpha=0.3, zorder=2))
    # Germinare
    ax.add_patch(patches.Rectangle((germ_x, 0.3), 2, 3, color='#e67e22', alpha=0.2, zorder=2))
    # Tablou
    ax.plot(tablou_x, l-0.5, 'rs', markersize=12, zorder=10)
    # Magistrala
    ax.plot([ibc_x+0.5, mag_x], [l-0.8, l-0.8], color='blue', linewidth=2, zorder=3)
    ax.plot([mag_x, tablou_x], [l-0.5, l-0.5], color='red', linestyle='--', linewidth=2, zorder=3)
    return mag_x

def genereaza_plan_tehnic(L, l, d, d_rand, d_teh=0.3, d_acc=1.2, max_t=150, pos_echip="dreapta"):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_xlim(-1, L + 1)
    ax.set_ylim(-1, l + 1)
    ax.add_patch(patches.Rectangle((0, 0), L, l, linewidth=3, edgecolor='black', facecolor='#fdfdfd', zorder=1))

    mag_x = deseneaza_echipamente(ax, pos_echip, L, l)

    # Calcul turnuri vectorial
    count = 0
    m_teava, m_cablu = 0, 0
    y_ptr = 0.5
    while y_ptr + d <= l - 0.3 and count < max_t:
        # Pereche rânduri
        y1 = y_ptr + d/2
        y2 = y1 + d + d_teh
        pereche = [y1] if y2 + d/2 > l - 0.3 else [y1, y2]

        for y_pos in pereche:
            x_start = 0.8 if pos_echip == "dreapta" else 3.5
            limita_x = L-3.5 if pos_echip == "dreapta" else L-0.8

            # Utilități rând
            ax.plot([x_start, mag_x], [y_pos, y_pos], color='blue', alpha=0.1, lw=1)
            ax.plot([x_start, mag_x], [y_pos+0.05, y_pos+0.05], color='red', alpha=0.1, ls='--', lw=1)
            m_teava += abs(mag_x - x_start)
            m_cablu += abs(mag_x - x_start)

            # Poziții turnuri vectorial
            x_positions = np.arange(x_start, limita_x+d, d+d_rand)
            for x in x_positions:
                if count >= max_t:
                    break
                ax.add_patch(patches.Circle((x, y_pos), d/2, color='#2ecc71', edgecolor='#27ae60', zorder=4))
                count += 1

        y_ptr = (pereche[-1] + d/2) + d_acc

    ax.set_aspect('equal')
    return fig, count, m_teava, m_cablu

# --- GENERARE / MEMORARE FIGURA ---
params_key = f"{L_solar}_{l_solar}_{diametru}_{dist_pe_rand}_{culoar_acces}_{max_turnuri}_{st.session_state.pos_echipamente}"

if st.session_state.last_params != params_key:
    fig, total, t_m, c_m = genereaza_plan_tehnic(
        L_solar, l_solar, diametru, dist_pe_rand, d_teh=0.3, d_acc=culoar_acces, max_t=max_turnuri,
        pos_echip=st.session_state.pos_echipamente
    )
    st.session_state.fig = fig
    st.session_state.total = total
    st.session_state.t_m = t_m
    st.session_state.c_m = c_m
    st.session_state.last_params = params_key
else:
    fig = st.session_state.fig
    total = st.session_state.total
    t_m = st.session_state.t_m
    c_m = st.session_state.c_m

# --- AFISARE ---
col1, col2 = st.columns([4,1])
with col1:
    st.pyplot(fig, use_container_width=True)
with col2:
    st.metric("Turnuri Totale", total)
    st.divider()
    st.subheader("📋 Necesar Materiale")
    st.write(f"💧 Teavă: **{t_m:.1f} m**")
    st.write(f"⚡ Cablu: **{c_m * 1.1:.1f} m**")
    st.caption("Configurație: " + st.session_state.pos_echipamente.upper())
