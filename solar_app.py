import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configurare Pagina
st.set_page_config(page_title="Arhitect Solar AI Chat", layout="wide")

# --- INITIALIZARE STATE PENTRU COMENZI ---
if 'diametru' not in st.session_state:
    st.session_state.diametru = 0.5
if 'd_teh' not in st.session_state:
    st.session_state.d_teh = 0.3
if 'd_acc' not in st.session_state:
    st.session_state.d_acc = 1.2

st.title("🌱 Arhitect Solar AI cu Chat Control")

# --- SIDEBAR: ASISTENT CHAT ---
with st.sidebar:
    st.header("🤖 Asistent AI")
    user_input = st.text_input("Scrie o comandă (ex: 'culoar mai mare', 'turnuri groase', 'reset'):")
    
    if st.button("Execută"):
        cmd = user_input.lower()
        if "culoar" in cmd and "mare" in cmd:
            st.session_state.d_acc = 1.8
            st.success("Am mărit culoarul de acces la 1.8m.")
        elif "turnuri" in cmd and "groase" in cmd:
            st.session_state.diametru = 0.7
            st.success("Am setat diametrul turnurilor la 0.7m.")
        elif "tehnic" in cmd and "mic" in cmd:
            st.session_state.d_teh = 0.2
            st.success("Am redus spațiul tehnic la 0.2m.")
        elif "reset" in cmd:
            st.session_state.diametru = 0.5
            st.session_state.d_acc = 1.2
            st.session_state.d_teh = 0.3
            st.success("Parametri resetați la valorile standard.")
        else:
            st.warning("Comandă nerecunoscută. Încearcă 'culoar mare' sau 'reset'.")

    st.divider()
    st.subheader("Parametri Activi")
    L_solar = st.number_input("Lungime Solar (m)", value=20.0)
    l_solar = st.number_input("Latime Solar (m)", value=7.0)
    
    # Acesti parametri sunt acum controlati si de Chat
    diametru = st.slider("Diametru Turn", 0.3, 0.8, float(st.session_state.diametru))
    dist_tehnica = st.slider("Spațiu Tehnic", 0.1, 1.0, float(st.session_state.d_teh))
    culoar_acces = st.slider("Culoar Acces", 0.8, 2.5, float(st.session_state.d_acc))

# --- MOTORUL DE CALCUL ---
def genereaza_plan_final(L, l, d, d_teh, d_acc):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.add_patch(patches.Rectangle((0, 0), L, l, linewidth=2, edgecolor='black', facecolor='#f8f9fa'))
    
    count = 0
    y_ptr = 0.3
    dist_centre = d + d_teh
    
    while y_ptr + d <= l - 0.3:
        y1 = y_ptr + d/2
        y2 = y1 + dist_centre
        pereche = [y1, y2] if y2 + d/2 <= l - 0.3 else [y1]
        
        for y_pos in pereche:
            x_pos = 0.5
            limita_x = L - 3.5 if (y_pos < 3.5 or y_pos > l - 4) else L - 1.2
            while x_pos <= limita_x:
                ax.add_patch(patches.Circle((x_pos, y_pos), d/2, color='#2ecc71', alpha=0.7))
                count += 1
                x_pos += d + 0.5
        y_ptr = (pereche[-1] + d/2) + d_acc
    
    # Echipamente fixe
    ax.add_patch(patches.Rectangle((L-2.3, 0.3), 2, 3, color='#e67e22', alpha=0.3)) # Germinare
    ax.add_patch(patches.Rectangle((L-1.3, l-1.3), 1, 1, color='blue', alpha=0.3)) # IBC 1
    ax.set_aspect('equal')
    return fig, count

# --- AFISARE ---
fig, total = genereaza_plan_final(L_solar, l_solar, diametru, dist_tehnica, culoar_acces)
st.pyplot(fig)
st.metric("Capacitate Totală", f"{total} Turnuri")
