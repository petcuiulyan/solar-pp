import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D

# Configurare Pagina
st.set_page_config(page_title="Arhitect Solar Hidroponic AI", layout="wide")

st.title("🌱 Arhitect Digital: Configurator Solar Hidroponic")
st.sidebar.header("Parametri Configurare")

# --- SIDEBAR - DATE DE INTRARE ---
with st.sidebar:
    L_solar = st.number_input("Lungime Solar (m)", value=20.0, step=0.5)
    l_solar = st.number_input("Latime Solar (m)", value=7.0, step=0.5)
    
    st.divider()
    diametru = st.slider("Diametru Turn (m)", 0.1, 1.0, 0.5)
    dist_pe_rand = st.slider("Distanta intre turnuri (m)", 0.1, 1.0, 0.5)
    dist_tehnica = st.slider("Spatiu Tehnic (m)", 0.2, 1.0, 0.3)
    culoar_acces = st.slider("Culoar Acces (m)", 0.8, 2.5, 1.2)
    
    st.divider()
    max_turnuri = st.number_input("Limita maxima turnuri", value=100)

# --- LOGICA DE CALCUL SI GENERARE PLAN ---
def genereaza_grafic():
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Contur
    ax.add_patch(patches.Rectangle((0, 0), L_solar, l_solar, linewidth=3, edgecolor='black', facecolor='#f9f9f9', zorder=1))
    
    # Germinare si IBC
    germinare_x, germinare_y = L_solar - 2.3, 0.3
    ax.add_patch(patches.Rectangle((germinare_x, germinare_y), 2, 3, color='#e67e22', alpha=0.3, zorder=2))
    
    ibc1_x, ibc1_y = L_solar - 1.3, l_solar - 1.3
    ax.add_patch(patches.Rectangle((ibc1_x, ibc1_y), 1, 1, color='blue', alpha=0.3, zorder=2))
    
    ibc2_x, ibc2_y = ibc1_x, ibc1_y - 1.5
    ax.add_patch(patches.Rectangle((ibc2_x, ibc2_y), 1, 1, color='blue', alpha=0.3, zorder=2))

    # Tablou si Intrare
    ax.plot(L_solar - 0.2, l_solar - 0.5, 'rs', markersize=12, zorder=10)
    ax.plot([L_solar, L_solar], [3.4, 4.6], color='white', linewidth=8, zorder=5)

    count_turnuri = 0
    y_ptr = 0.3 
    total_teava = 0
    total_cablu = 0
    dist_centre = diametru + dist_tehnica 

    while y_ptr + diametru <= l_solar - 0.3:
        y1 = y_ptr + diametru/2
        y2 = y1 + dist_centre
        y_pereche = [y1, y2] if y2 + diametru/2 <= l_solar - 0.3 else [y1]

        if len(y_pereche) == 2:
            y_apa, y_curent = y1 + diametru/2 + (dist_tehnica * 0.4), y1 + diametru/2 + (dist_tehnica * 0.6)
            ax.plot([0.5, L_solar - 3], [y_apa, y_apa], color='blue', ls='--', alpha=0.3)
            ax.plot([0.5, L_solar - 3], [y_curent, y_curent], color='red', ls=':', alpha=0.3)
            total_teava += (L_solar - 3.5)
            total_cablu += (L_solar - 3.5) + (l_solar - y_curent)

        for y_pos in y_pereche:
            x_pos = 0.5
            limita_x = L_solar - 3.5 if (y_pos < 3.5 or y_pos > l_solar - 4) else L_solar - 1.5
            while x_pos <= limita_x and count_turnuri < max_turnuri:
                ax.add_patch(patches.Circle((x_pos, y_pos), diametru/2, color='#2ecc71', edgecolor='#27ae60', alpha=0.8, zorder=4))
                count_turnuri += 1
                x_pos += diametru + dist_pe_rand
        
        y_ptr = (y_pereche[-1] + diametru/2) + culoar_acces

    ax.set_aspect('equal')
    plt.grid(True, linestyle=':', alpha=0.1)
    return fig, count_turnuri, total_teava, total_cablu

# --- AFISARE IN APLICATIE ---
col1, col2 = st.columns([3, 1])

with col1:
    fig, n_turnuri, l_teava, l_cablu = genereaza_grafic()
    st.pyplot(fig)

with col2:
    st.metric("Total Turnuri", n_turnuri)
    st.metric("Estimare Teava (m)", f"{l_teava:.1f}")
    st.metric("Estimare Cablu (m)", f"{l_cablu + 10:.1f}")
    
    st.info("💡 Sfat: Daca turnurile se suprapun cu IBC-ul, mareste culoarul de acces sau scade distanta tehnica.")
    
    if st.button("Salveaza Planul ca PNG"):
        fig.savefig("plan_solar.png", dpi=300)
        st.success("Plan salvat!")