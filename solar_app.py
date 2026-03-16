import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configurare Pagina
st.set_page_config(page_title="Arhitect Solar AI v6", layout="wide")

if 'pos_echipamente' not in st.session_state:
    st.session_state.pos_echipamente = "dreapta"

st.title("🌱 Proiect Tehnic: Configurator Utilități & Deviz Materiale")

# --- SIDEBAR: CONTROL PARAMETRI ---
with st.sidebar:
    st.header("📏 Dimensiuni Solar")
    L_solar = st.number_input("Lungime (m)", value=23.5, step=0.5)
    l_solar = st.number_input("Latime (m)", value=7.0, step=0.5)
    
    st.divider()
    st.header("🚜 Configurare Turnuri")
    max_turnuri = st.slider("Limită Turnuri", 10, 500, 150)
    diametru = st.slider("Diametru Turn (m)", 0.3, 0.8, 0.5)
    dist_pe_rand = st.slider("Spațiu între turnuri (m)", 0.1, 1.0, 0.5)
    
    st.divider()
    st.header("🤖 Control Poziție AI")
    user_cmd = st.text_input("Comandă (stânga/dreapta):")
    if st.button("Aplică Poziția"):
        if "stanga" in user_cmd.lower() or "stânga" in user_cmd.lower():
            st.session_state.pos_echipamente = "stanga"
        else:
            st.session_state.pos_echipamente = "dreapta"

# --- MOTORUL DE CALCUL ---
def genereaza_plan_tehnic(L, l, d, d_rand, d_teh, d_acc, max_t, pos_echip):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_xlim(-1, L + 1)
    ax.set_ylim(-1, l + 1)
    
    # Structura Solar
    ax.add_patch(patches.Rectangle((0, 0), L, l, linewidth=3, edgecolor='black', facecolor='#fdfdfd', zorder=1))
    
    # Variabile Materiale
    m_teava = 0
    m_cablu = 0
    
    # Poziționare Echipamente
    dist_margine = 0.3
    if pos_echip == "dreapta":
        ibc1_x, ibc1_y = L - 1.3, l - 1.3
        ibc2_x, ibc2_y = ibc1_x, ibc1_y - 1.5
        germ_x, germ_y = L - 2.3, dist_margine
        tablou_x, tablou_y = L - 0.2, l - 0.5
        magistrala_x = L - 3.0
    else:
        ibc1_x, ibc1_y = dist_margine, l - 1.3
        ibc2_x, ibc2_y = ibc1_x, ibc1_y - 1.5
        germ_x, germ_y = dist_margine, dist_margine
        tablou_x, tablou_y = 0.2, l - 0.5
        magistrala_x = 3.0

    # Desenare Echipamente
    ax.add_patch(patches.Rectangle((ibc1_x, ibc1_y), 1, 1, color='blue', alpha=0.3, zorder=2))
    ax.add_patch(patches.Rectangle((ibc2_x, ibc2_y), 1, 1, color='blue', alpha=0.3, zorder=2))
    ax.add_patch(patches.Rectangle((germ_x, germ_y), 2, 3, color='#e67e22', alpha=0.2, zorder=2))
    ax.plot(tablou_x, tablou_y, 'rs', markersize=12, zorder=10)

    # Magistrale Principale
    # Apă: de la IBC1 la magistrala verticală
    ax.plot([ibc1_x + 0.5, magistrala_x], [ibc1_y + 0.5, ibc1_y + 0.5], color='blue', linewidth=2, zorder=3)
    m_teava += abs(ibc1_x + 0.5 - magistrala_x)
    
    # Curent: de la magistrală la Tablou
    ax.plot([magistrala_x, tablou_x], [tablou_y, tablou_y], color='red', linestyle='--', linewidth=2, zorder=3)
    m_cablu += abs(magistrala_x - tablou_x)

    # Plasare Turnuri
    count = 0
    y_ptr = 0.5
    dist_centre_y = d + d_teh
    
    while y_ptr + d <= l - 0.3 and count < max_t:
        y1 = y_ptr + d/2
        y2 = y1 + dist_centre_y
        pereche = [y1, y2] if y2 + d/2 <= l - 0.3 else [y1]
        
        for y_pos in pereche:
            x_start = 0.8 if pos_echip == "dreapta" else 3.5
            limita_x = L - 3.5 if pos_echip == "dreapta" else L - 0.8
            
            # Conexiuni pe rând
            ax.plot([x_start, magistrala_x], [y_pos, y_pos], color='blue', alpha=0.2, linewidth=1)
            ax.plot([x_start, magistrala_x], [y_pos + 0.05, y_pos + 0.05], color='red', alpha=0.2, linestyle='--', linewidth=1)
            
            lungime_rand = abs(magistrala_x - x_start)
            m_teava += lungime_rand
            m_cablu += lungime_rand

            x_pos = x_start
            while x_pos <= limita_x and count < max_t:
                ax.add_patch(patches.Circle((x_pos, y_pos), d/2, color='#2ecc71', edgecolor='#27ae60', zorder=4))
                count += 1
                x_pos += d + d_rand
        
        # Magistrala verticală (legătura între rânduri)
        ax.plot([magistrala_x, magistrala_x], [y1, ibc1_y], color='blue', alpha=0.3)
        m_teava += abs(ibc1_y - y1)
        m_cablu += abs(tablou_y - y1)
        
        y_ptr = (pereche[-1] + d/2) + d_acc

    ax.set_aspect('equal')
    plt.grid(True, linestyle=':', alpha=0.2)
    return fig, count, m_teava, m_cablu

# --- AFIȘARE REZULTATE ---
col1, col2 = st.columns([4, 1])
with col1:
    fig, total, teava, cablu = genereaza_plan_tehnic(L_solar, l_solar, diametru, dist_pe_rand, 0.3, 1.2, max_turnuri, st.session_state.pos_echipamente)
    st.pyplot(fig, use_container_width=True)

with col2:
    st.metric("Total Turnuri", total)
    st.divider()
    st.subheader("📋 Deviz Estimativ")
    st.write(f"🔵 **Țeavă Apă:** {teava:.1f} m")
    st.write(f"🔴 **Cablu Electric:** {cablu * 1.1:.1f} m") # Adaos 10% conexiuni
    st.caption("Nota: Cablul include marjă de 10% pentru legături în doze.")
    
    st.divider()
    st.write("### Legendă")
    st.info("Linia albastră continuă = Magistrală apă. Linia roșie punctată = Traseu curent.")
