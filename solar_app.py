import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

st.set_page_config(page_title="Arhitect Solar Planner v2", layout="wide")
st.title("🌱 Arhitect Solar Planner: Layout Compact pe Colț")

# --- Sidebar ---
st.sidebar.header("📏 Setări Solar")
L_solar = st.sidebar.number_input("Lungime Solar (m)", value=23.5, step=0.5)
l_solar = st.sidebar.number_input("Latime Solar (m)", value=7.0, step=0.5)

st.sidebar.header("⚙️ Parametri Turnuri")
max_turnuri = st.sidebar.slider("Limită Turnuri", 10, 500, 150)
diametru = st.sidebar.slider("Diametru Turn (m)", 0.3, 0.8, 0.5)
dist_pe_rand = st.sidebar.slider("Spațiu între turnuri (m)", 0.1, 1.0, 0.5)
culoar_acces = st.sidebar.slider("Culoar Acces (m)", 0.8, 2.5, 1.2)

st.sidebar.header("🟦 Poziție echipamente fixe")
pos_echip = st.sidebar.radio("IBC / Germinare / Tablou:", ("dreapta-sus", "stanga-sus"))

# --- Functie layout inteligent ---
def genereaza_plan_compact(L, l, d, d_rand, d_teh=0.3, d_acc=1.2, max_t=150, pos_echip="dreapta-sus"):
    fig, ax = plt.subplots(figsize=(16,8))
    ax.set_xlim(0, L)
    ax.set_ylim(0, l)
    ax.add_patch(patches.Rectangle((0,0), L, l, linewidth=3, edgecolor='black', facecolor='#fdfdfd', zorder=1))
    
    # --- Pozitie echipamente fixe ---
    if pos_echip.startswith("dreapta"):
        ibc_x = L - 2.5
        tablou_x = L - 0.5
        germ_x = ibc_x - 1.5
    else:
        ibc_x = 0.5
        tablou_x = 0.2
        germ_x = ibc_x + 1.0

    if pos_echip.endswith("sus"):
        ibc_y = l - 1.3
        tablou_y = l - 0.5
        germ_y = 0.3
    else:
        ibc_y = 0.2
        tablou_y = 0.5
        germ_y = l - 3.0

    # Desenare IBC-uri
    ax.add_patch(patches.Rectangle((ibc_x, ibc_y),1,1, color='blue', alpha=0.3, zorder=2))
    ax.add_patch(patches.Rectangle((ibc_x, ibc_y - 1.5 if pos_echip.endswith("sus") else ibc_y + 1.5),1,1, color='blue', alpha=0.3, zorder=2))
    # Masa germinare
    ax.add_patch(patches.Rectangle((germ_x, germ_y), 2, 3, color='#e67e22', alpha=0.2, zorder=2))
    # Tablou
    ax.plot(tablou_x, tablou_y, 'rs', markersize=12, zorder=10)

    # --- Zona ocupata de echipamente ---
    zone_occupate = [
        (ibc_x - d/2, ibc_y - d/2, ibc_x + 1 + d/2, ibc_y + 1 + d/2),
        (ibc_x - d/2, ibc_y - 0.5, ibc_x + 1 + d/2, ibc_y + 1.5),
        (germ_x - d/2, germ_y - d/2, germ_x + 2 + d/2, germ_y + 3 + d/2)
    ]
    
    # --- Calcul rânduri/coloane pentru turnuri ---
    # spațiu disponibil evitând echipamentele
    x_min = 0
    x_max = L
    y_min = 0
    y_max = l

    # ajustare spatiu pe baza zonei ocupate
    for z in zone_occupate:
        zx_min, zy_min, zx_max, zy_max = z
        # pentru layout compact, doar excludem zona echipamentelor
        if pos_echip.startswith("dreapta"):
            x_max = min(x_max, zx_min - 0.2)
        else:
            x_min = max(x_min, zx_max + 0.2)
        if pos_echip.endswith("sus"):
            y_max = min(y_max, zy_min - 0.2)
        else:
            y_min = max(y_min, zy_max + 0.2)

    # nr rânduri/coloane
    n_col = int(np.floor((x_max - x_min + d_rand) / (d + d_rand)))
    n_row = int(np.floor((y_max - y_min + culoar_acces) / (d + culoar_acces)))
    n_col = max(1, min(n_col, max_turnuri))
    n_row = max(1, min(n_row, max_turnuri))

    x_positions = np.linspace(x_min + d/2, x_max - d/2, n_col)
    y_positions = np.linspace(y_min + d/2, y_max - d/2, n_row)

    turn_positions = []
    for y in y_positions:
        for x in x_positions:
            turn_positions.append((x,y))
            ax.add_patch(patches.Circle((x,y), d/2, color='#2ecc71', edgecolor='#27ae60', zorder=4))

    # --- Linii electrice si teava ---
    mag_x = ibc_x if pos_echip.startswith("stanga") else ibc_x + 1
    m_teava = 0
    m_cablu = 0
    for y in y_positions:
        for x in x_positions:
            ax.plot([x, mag_x], [y, y], color='blue', alpha=0.3, lw=1, zorder=2)
            ax.plot([x, mag_x], [y+0.05, y+0.05], color='red', alpha=0.3, lw=1, ls='--', zorder=2)
            m_teava += abs(x - mag_x)
            m_cablu += abs(x - mag_x)

    # --- Distante unice intre turnuri ---
    distante_unice = set()
    for y in y_positions:
        diffs = np.diff(np.sort(x_positions))
        for d_val in diffs:
            distante_unice.add(round(d_val,3))
    distante_unice = sorted(list(distante_unice))

    ax.set_aspect('equal')
    return fig, len(turn_positions), m_teava, m_cablu, distante_unice

# --- Generare figura ---
fig, total, t_m, c_m, distante_unice = genereaza_plan_compact(
    L_solar, l_solar, diametru, dist_pe_rand, d_teh=0.3, d_acc=culoar_acces, max_t=max_turnuri, pos_echip=pos_echip
)

# --- Afisare ---
col1, col2 = st.columns([4,1])
with col1:
    st.pyplot(fig, use_container_width=True)
with col2:
    st.metric("Turnuri Totale", total)
    st.divider()
    st.subheader("📋 Necesar Materiale")
    st.write(f"💧 Teavă: **{t_m:.1f} m**")
    st.write(f"⚡ Cablu: **{c_m * 1.1:.1f} m**")
    st.caption("Configurație: " + pos_echip.upper())
    st.divider()
    st.subheader("📏 Distante între turnuri (unice)")
    st.write(distante_unice)
