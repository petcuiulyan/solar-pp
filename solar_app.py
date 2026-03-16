import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configurare Pagina
st.set_page_config(page_title="Arhitect Solar AI v4", layout="wide")

# --- INITIALIZARE STATE ---
if 'pos_echipamente' not in st.session_state:
    st.session_state.pos_echipamente = "dreapta"

st.title("🌱 Sistem Optimizat: Control Manual & Arhitect AI")

# --- SIDEBAR: CONTROL RAPID ---
with st.sidebar:
    st.header("📏 Dimensiuni de Bază")
    L_solar = st.number_input("Lungime Solar (m)", value=20.0, step=0.5)
    l_solar = st.number_input("Latime Solar (m)", value=7.0, step=0.5)
    
    st.divider()
    st.header("🚜 Configurare Turnuri")
    max_turnuri = st.slider("Număr maxim turnuri", 10, 200, 100)
    diametru = st.slider("Diametru Turn (m)", 0.3, 0.8, 0.5)
    dist_pe_rand = st.slider("Distanță între turnuri (m)", 0.1, 1.0, 0.5)
    
    st.divider()
    st.header("🛤️ Spațiere și Acces")
    dist_tehnica = st.slider("Spațiu Tehnic (m)", 0.1, 1.0, 0.3)
    culoar_acces = st.slider("Culoar Acces (m)", 0.8, 2.5, 1.2)

    st.divider()
    st.header("🤖 Poziționare AI")
    user_cmd = st.text_input("Comandă AI (ex: 'mută în stânga', 'densitate mare'):")
    if st.button("Execută"):
        cmd = user_cmd.lower()
        if "stânga" in cmd:
            st.session_state.pos_echipamente = "stanga"
        elif "dreapta" in cmd:
            st.session_state.pos_echipamente = "dreapta"
        elif "dens" in cmd or "maxim" in cmd:
            # AI-ul forțează cele mai mici distanțe sigure
            st.info("AI a optimizat distanțele pentru densitate maximă.")
            # Nota: Acestea vor suprascrie vizual glisoarele la urmatoarea rulare daca dorim
            dist_tehnica, culoar_acces = 0.2, 0.9

# --- MOTORUL DE CALCUL ---
def genereaza_plan(L, l, d, d_rand, d_teh, d_acc, max_t, pos_echip):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.add_patch(patches.Rectangle((0, 0), L, l, linewidth=2, edgecolor='black', facecolor='#f8f9fa'))
    
    count = 0
    y_ptr = 0.3
    dist_centre = d + d_teh
    
    # Definire zone obstacole în funcție de AI (stânga sau dreapta)
    echip_x = L - 2.5 if pos_echip == "dreapta" else 0.5
    
    while y_ptr + d <= l - 0.3 and count < max_t:
        y1 = y_ptr + d/2
        y2 = y1 + dist_centre
        pereche = [y1, y2] if y2 + d/2 <= l - 0.3 else [y1]
        
        for y_pos in pereche:
            x_pos = 0.5 if pos_echip == "dreapta" else 3.0
            # Limitare X dinamică
            if pos_echip == "dreapta":
                limita_x = L - 3.5 if (y_pos < 3.5 or y_pos > l - 4) else L - 1.2
            else:
                limita_x = L - 0.5 if (y_pos < 3.5 or y_pos > l - 4) else L - 0.5
                
            while x_pos <= limita_x and count < max_t:
                ax.add_patch(patches.Circle((x_pos, y_pos), d/2, color='#2ecc71', alpha=0.7, zorder=4))
                count += 1
                x_pos += d + d_rand
        
        y_ptr = (pereche[-1] + d/2) + d_acc
    
    # Echipamente (Poziționate de AI)
    if pos_echip == "dreapta":
        ax.add_patch(patches.Rectangle((L-2.3, 0.3), 2, 3, color='#e67e22', alpha=0.3)) # Germinare
        ax.add_patch(patches.Rectangle((L-1.3, l-1.3), 1, 1, color='blue', alpha=0.3)) # IBC 1
    else:
        ax.add_patch(patches.Rectangle((0.3, 0.3), 2, 3, color='#e67e22', alpha=0.3)) # Germinare
        ax.add_patch(patches.Rectangle((0.3, l-1.3), 1, 1, color='blue', alpha=0.3)) # IBC 1

    ax.set_aspect('equal')
    return fig, count

# --- AFIȘARE ---
col1, col2 = st.columns([4, 1])

with col1:
    fig, total = genereaza_plan(L_solar, l_solar, diametru, dist_pe_rand, dist_tehnica, culoar_acces, max_turnuri, st.session_state.pos_echipamente)
    st.pyplot(fig)

with col2:
    st.metric("Turnuri Plasate", total)
    if total < max_turnuri:
        st.warning(f"S-au putut plasa doar {total} turnuri în acest spațiu.")
    else:
        st.success("Toate turnurile au fost plasate!")
    
    st.write(f"**Poziție Echipamente:** {st.session_state.pos_echipamente.capitalize()}")
