import streamlit as st

# ===============================
# 🔧 CONFIGURACIÓN INICIAL
# ===============================

st.set_page_config(page_title="Gestor de Propietarios", layout="centered")

# Inicializar session_state
if "propietarios" not in st.session_state:
    st.session_state.propietarios = {}

if "propietario_select" not in st.session_state:
    st.session_state.propietario_select = "Escribir manualmente..."

if "casa_select" not in st.session_state:
    st.session_state.casa_select = "Escribir manualmente..."

# ===============================
# 📂 CARGAR DATOS DESDE TXT
# ===============================
# Estructura esperada del archivo:
# 1, Juan Pérez
# 2, Ana Gómez
# 3, Carlos Rivas

DATA_PATH = "propietarios.txt"

try:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        st.session_state.propietarios = {
            casa.strip(): nombre.strip()
            for casa, nombre in (line.split(",", 1) for line in lines)
        }
except FileNotFoundError:
    st.warning(f"No se encontró el archivo '{DATA_PATH}'. Crea uno con formato: `1, Juan Pérez`.")
    st.session_state.propietarios = {}

# ===============================
# 🔁 CALLBACKS DE SINCRONIZACIÓN
# ===============================

def on_propietario_change():
    """Cuando cambia el propietario, actualiza la casa asociada."""
    if st.session_state.propietario_select == "Escribir manualmente...":
        return
    for casa, nombre in st.session_state.propietarios.items():
        if nombre == st.session_state.propietario_select:
            st.session_state.casa_select = casa
            st.experimental_rerun()

def on_casa_change():
    """Cuando cambia la casa, actualiza el propietario asociado."""
    if st.session_state.casa_select == "Escribir manualmente...":
        return
    nombre = st.session_state.propietarios.get(st.session_state.casa_select)
    if nombre:
        st.session_state.propietario_select = nombre
        st.experimental_rerun()

# ===============================
# 🏡 INTERFAZ PRINCIPAL
# ===============================

st.title("🏡 Gestor de Propietarios y Casas")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Propietario")
    propietario_list = ["Escribir manualmente..."] + sorted(
        list(set(st.session_state.propietarios.values()))
    )
    st.selectbox(
        "Seleccione o escriba el nombre",
        propietario_list,
        key="propietario_select",
        on_change=on_propietario_change,
        label_visibility="collapsed"
    )

    if st.session_state.propietario_select == "Escribir manualmente...":
        propietario_manual = st.text_input(
            "Nombre del propietario", key="propietario_manual", placeholder="Ej: Juan Pérez"
        )
    else:
        propietario_manual = ""

with col2:
    st.markdown("#### Número de Casa")
    casa_list = ["Escribir manualmente..."] + sorted(
        list(st.session_state.propietarios.keys()), key=lambda x: int(x) if x.isdigit() else x
    )
    st.selectbox(
        "Seleccione o escriba el número",
        casa_list,
        key="casa_select",
        on_change=on_casa_change,
        label_visibility="collapsed"
    )

    if st.session_state.casa_select == "Escribir manualmente...":
        casa_manual = st.text_input(
            "Número de casa", key="casa_manual", placeholder="Ej: 25"
        )
    else:
        casa_manual = ""

# ===============================
# ✅ RESULTADO FINAL
# ===============================

propietario = (
    st.session_state.propietario_manual.strip()
    if st.session_state.propietario_select == "Escribir manualmente..."
    else st.session_state.propietario_select
)

numero_casa = (
    st.session_state.casa_manual.strip()
    if st.session_state.casa_select == "Escribir manualmente..."
    else st.session_state.casa_select
)

if propietario and numero_casa:
    st.success(f"Propietario: **{propietario}** 🏠 Casa Nº **{numero_casa}**")
