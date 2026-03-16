import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# --- CONFIGURARE PAGINA ---
st.set_page_config(page_title="Arhitect Solar AI v8", layout="wide")
st.title("🌱 Arhitect Solar AI: Control Vocal/Text Optimizat + Distante")

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
def genereaza_plan_tehnic(L, l, d, d_rand, d_teh=0.3, d_acc=1.2, max_t=150, pos_echip="dreapta"):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_xlim(-1, L + 1)
    ax.set_ylim(-1, l + 1)
    ax.add_patch(patches.Rectangle((0, 0), L, l, linewidth=3, edgecolor='black', facecolor='#fdfdfd', zorder=1))

    # --- Magistrala dinamică ---
    if pos_echip == "dreapta":
        mag_x = L-3.0
        x_start = 0.8
        x_stop  = L-3.5
    else:
        mag_x = 3.0
        x_start = 3.5
        x_stop  = L-0.8

    # Echipamente fixe
    if pos_echip == "dreapta":
        ibc_x, germ_x, tablou_x = L-1.3, L-2.3, L-0.2
    else:
        ibc_x, germ_x, tablou_x = 0.3, 0.3, 0.2
    # IBC-uri
    ax.add_patch(patches.Rectangle((ibc_x, l-1.3), 1, 1, color='blue', alpha=0.3, zorder=2))
    ax.add_patch(patches.Rectangle((ibc_x, l-2.8), 1, 1, color='blue', alpha=0.3, zorder=2))
    # Germinare
    ax.add_patch(patches.Rectangle((germ_x, 0.3), 2, 3, color='#e67e22', alpha=0.2, zorder=2))
    # Tablou
    ax.plot(tablou_x, l-0.5, 'rs', markersize=12, zorder=10)
    # Magistrala vizibilă
    ax.plot([ibc_x+0.5, mag_x], [l-0.8, l-0.8], color='blue', linewidth=2, zorder=3)
    ax.plot([mag_x, tablou_x], [l-0.5, l-0.5], color='red', linestyle='--', linewidth=2, zorder=3)

    # --- Generare turnuri ---
    y_ptr = 0.5
    turn_positions = []
    while y_ptr + d <= l - 0.3 and len(turn_positions) < max_t:
        y1 = y_ptr + d/2
        y2 = y1 + d + d_teh
        pereche = [y1] if y2 + d/2 > l - 0.3 else [y1, y2]
        for y_pos in pereche:
            x_positions = np.arange(x_start, x_stop+d, d+d_rand) if pos_echip=="dreapta" else np.arange(x_stop, x_start-d, -(d+d_rand))
            for x in x_positions:
                if len(turn_positions) >= max_t:
                    break
                ax.add_patch(patches.Circle((x, y_pos), d/2, color='#2ecc71', edgecolor='#27ae60', zorder=4))
                turn_positions.append((x, y_pos))
        y_ptr = (pereche[-1] + d/2) + d_acc

    # --- Linii electrice și țeavă între turnuri și magistrală ---
    turn_positions = np.array(turn_positions)
    unique_y = np.unique(turn_positions[:,1])
    m_teava, m_cablu = 0, 0

    for y in unique_y:
        x_row = np.sort(turn_positions[turn_positions[:,1]==y,0])
        segments = []
        if pos_echip == "dreapta":
            segments.append((x_start, x_row[0]-d/2))
            for i in range(len(x_row)-1):
                segments.append((x_row[i]+d/2, x_row[i+1]-d/2))
            segments.append((x_row[-1]+d/2, mag_x))
        else:
            segments.append((x_row[-1]+d/2, x_start))
            for i in range(len(x_row)-1):
                segments.append((x_row[i+1]-d/2, x_row[i]+d/2))
            segments.append((mag_x, x_row[0]-d/2))
        for seg_start, seg_end in segments:
            if seg_end <= seg_start:
                continue
            ax.plot([seg_start, seg_end], [y, y], color='blue', alpha=0.3, lw=1, zorder=2)
            ax.plot([seg_start, seg_end], [y+0.05, y+0.05], color='red', alpha=0.3, lw=1, ls='--', zorder=2)
            m_teava += abs(seg_end - seg_start)
            m_cablu += abs(seg_end - seg_start)

    # --- Calcul distante unice între turnuri ---
    distante_unice = set()
    for y in unique_y:
        x_row = np.sort(turn_positions[turn_positions[:,1]==y,0])
        diffs = np.diff(x_row)
        for d_val in diffs:
            distante_unice.add(round(d_val,3))
    distante_unice = sorted(list(distante_unice))

    ax.set_aspect('equal')
    return fig, len(turn_positions), m_teava, m_cablu, distante_unice

# --- GENERARE / MEMORARE FIGURA ---
params_key = f"{L_solar}_{l_solar}_{diametru}_{dist_pe_rand}_{culoar_acces}_{max_turnuri}_{st.session_state.pos_echipamente}"

if st.session_state.last_params != params_key:
    fig, total, t_m, c_m, distante_unice = genereaza_plan_tehnic(
        L_solar, l_solar, diametru, dist_pe_rand, d_teh=0.3, d_acc=culoar_acces, max_t=max_turnuri,
        pos_echip=st.session_state.pos_echipamente
    )
    st.session_state.fig = fig
    st.session_state.total = total
    st.session_state.t_m = t_m
    st.session_state.c_m = c_m
    st.session_state.distante_unice = distante_unice
    st.session_state.last_params = params_key
else:
    fig = st.session_state.fig
    total = st.session_state.total
    t_m = st.session_state.t_m
    c_m = st.session_state.c_m
    distante_unice = st.session_state.distante_unice

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
    st.divider()
    st.subheader("📏 Distante între turnuri (unice)")
    st.write(distante_unice)
