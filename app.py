import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io
import os

# Configuración de la página
st.set_page_config(
    page_title="Recibos Valle Verde",
    page_icon="🏘️",
    layout="wide"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        background-color: white;
    }
    .stButton>button {
        background-color: #98D8C8;
        color: black;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #7BC4B4;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #000000;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stNumberInput>div>div>input {
        border: 2px solid #98D8C8;
        border-radius: 5px;
    }
    .section-header {
        background-color: #E8F5F1;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        font-weight: bold;
        color: #000000;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'propietarios' not in st.session_state:
    st.session_state.propietarios = {}
if 'logo' not in st.session_state:
    st.session_state.logo = None

# Título principal
st.title("🏘️ Generador de Recibos - Valle Verde")
st.markdown("---")

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    st.markdown('<div class="section-header">📋 Lista de Propietarios</div>', unsafe_allow_html=True)
    
    # Opción para cargar archivo TXT
    archivo_txt = st.file_uploader(
        "Cargar archivo TXT (formato: Casa|Nombre)",
        type=['txt'],
        help="Cada línea debe tener el formato: Número|Nombre Completo"
    )
    
    if archivo_txt is not None:
        contenido = archivo_txt.read().decode('utf-8')
        lineas = contenido.strip().split('\n')
        for linea in lineas:
            if '|' in linea:
                casa, nombre = linea.split('|', 1)
                st.session_state.propietarios[casa.strip()] = nombre.strip()
        st.success(f"✅ {len(st.session_state.propietarios)} propietarios cargados")
    
    st.markdown("---")
    
    # Agregar propietarios manualmente
    st.markdown('<div class="section-header">➕ Agregar Propietario</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        nueva_casa = st.text_input("Número de Casa", key="nueva_casa")
    with col2:
        nuevo_nombre = st.text_input("Nombre Completo", key="nuevo_nombre")
    
    if st.button("Agregar", key="btn_agregar"):
        if nueva_casa and nuevo_nombre:
            st.session_state.propietarios[nueva_casa] = nuevo_nombre
            st.success("✅ Propietario agregado")
            st.rerun()
    
    st.markdown("---")
    
    # Logo del condominio
    st.markdown('<div class="section-header">🖼️ Logo del Condominio</div>', unsafe_allow_html=True)
    logo_file = st.file_uploader("Cargar logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    if logo_file is not None:
        st.session_state.logo = Image.open(logo_file)
        st.image(st.session_state.logo, width=150)

# Área principal - Formulario de recibo
st.header("📝 Generar Recibo de Pago")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">Datos del Propietario</div>', unsafe_allow_html=True)
    
    # Opción de seleccionar o escribir propietario
    modo_propietario = st.radio("Seleccionar modo:", ["Lista", "Manual"], horizontal=True)
    
    if modo_propietario == "Lista":
        if st.session_state.propietarios:
            casa_opciones = sorted(st.session_state.propietarios.keys())
            casa_seleccionada = st.selectbox("Número de Casa", casa_opciones)
            propietario = st.session_state.propietarios[casa_seleccionada]
            st.text_input("Propietario", value=propietario, disabled=True)
        else:
            st.warning("⚠️ No hay propietarios en la lista. Agregue propietarios en el panel lateral.")
            casa_seleccionada = st.text_input("Número de Casa")
            propietario = st.text_input("Nombre del Propietario")
    else:
        casa_seleccionada = st.text_input("Número de Casa")
        propietario = st.text_input("Nombre del Propietario")
    
    st.markdown('<div class="section-header">Detalles del Pago</div>', unsafe_allow_html=True)
    
    dia_pago = st.number_input("Día del Pago", min_value=1, max_value=31, value=datetime.now().day)
    monto_pago = st.number_input("Monto del Pago (Bs.)", min_value=0.0, format="%.2f", step=0.01)

with col2:
    st.markdown('<div class="section-header">Período Cancelado</div>', unsafe_allow_html=True)
    
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_cancelado = st.selectbox("Mes Cancelado", meses)
    
    años = list(range(2025, 2031))
    año_cancelado = st.selectbox("Año Cancelado", años)
    
    st.markdown('<div class="section-header">Información Adicional</div>', unsafe_allow_html=True)
    
    recibido_por = st.text_input("Recibido por", value="Eleida Ontiveros")
    referencia_pago = st.text_input("Referencia del Pago")

# Generar número de recibo automáticamente
mes_num = meses.index(mes_cancelado) + 1
numero_recibo = f"VV-{mes_num:02d}{año_cancelado}-{casa_seleccionada}"
st.info(f"📄 Número de Recibo: **{numero_recibo}**")

st.markdown("---")

# Función para generar el recibo
def generar_recibo():
    # Crear imagen del recibo
    ancho, alto = 800, 1000
    recibo = Image.new('RGB', (ancho, alto), 'white')
    draw = ImageDraw.Draw(recibo)
    
    try:
        # Intentar cargar fuentes del sistema
        fuente_titulo = ImageFont.truetype("arial.ttf", 24)
        fuente_subtitulo = ImageFont.truetype("arial.ttf", 22)
        fuente_normal = ImageFont.truetype("arial.ttf", 20)
        fuente_pequena = ImageFont.truetype("arial.ttf", 20)
    except:
        # Fuente por defecto si no encuentra Arial
        fuente_titulo = ImageFont.load_default()
        fuente_subtitulo = ImageFont.load_default()
        fuente_normal = ImageFont.load_default()
        fuente_pequena = ImageFont.load_default()
    
    y_pos = 30
    
    # Logo
    if st.session_state.logo:
        logo_resize = st.session_state.logo.copy()
        logo_resize.thumbnail((100, 100))
        recibo.paste(logo_resize, (50, y_pos))
        x_texto = 170
    else:
        x_texto = 50
    
    # Encabezado
    draw.text((x_texto, y_pos), "ASOCIACION CIVIL VALLE VERDE", fill='black', font=fuente_titulo)
    y_pos += 30
    draw.text((x_texto, y_pos), "Calle 7 N° 79, Valle Verde, Morita 1", fill='black', font=fuente_pequena)
    y_pos += 20
    draw.text((x_texto, y_pos), "Turmero, Estado Aragua", fill='black', font=fuente_pequena)
    y_pos += 20
    draw.text((x_texto, y_pos), "RIF: J-298826738", fill='black', font=fuente_pequena)
    y_pos += 40
    
    # Título del recibo
    draw.text((ancho//2 - 100, y_pos), "RECIBO DE PAGO", fill='black', font=fuente_titulo)
    y_pos += 50
    
    # Número de recibo
    draw.text((50, y_pos), f"Recibo N°: {numero_recibo}", fill='black', font=fuente_normal)
    y_pos += 40
    
    # Línea divisoria
    draw.line([(50, y_pos), (ancho-50, y_pos)], fill='black', width=2)
    y_pos += 30
    
    # Datos del pago
    draw.text((50, y_pos), f"Propietario: {propietario}", fill='black', font=fuente_normal)
    y_pos += 30
    draw.text((50, y_pos), f"Casa N°: {casa_seleccionada}", fill='black', font=fuente_normal)
    y_pos += 30
    draw.text((50, y_pos), f"Fecha de Pago: {dia_pago:02d}/{mes_num:02d}/{año_cancelado}", fill='black', font=fuente_normal)
    y_pos += 30
    draw.text((50, y_pos), f"Periodo Cancelado: {mes_cancelado} {año_cancelado}", fill='black', font=fuente_normal)
    y_pos += 40
    
    # Línea divisoria
    draw.line([(50, y_pos), (ancho-50, y_pos)], fill='black', width=2)
    y_pos += 30
    
    # Monto
    draw.text((50, y_pos), f"Monto Pagado: Bs. {monto_pago:,.2f}", fill='black', font=fuente_subtitulo)
    y_pos += 40
    
    if referencia_pago:
        draw.text((50, y_pos), f"Referencia: {referencia_pago}", fill='black', font=fuente_normal)
        y_pos += 40
    
    # Línea divisoria
    draw.line([(50, y_pos), (ancho-50, y_pos)], fill='black', width=2)
    y_pos += 40
    
    # Recibido por
    draw.text((50, y_pos), f"Recibido por: {recibido_por}", fill='black', font=fuente_normal)
    y_pos += 80
    
    # Firma
    draw.line([(50, y_pos), (300, y_pos)], fill='black', width=1)
    y_pos += 10
    draw.text((50, y_pos), "Firma y Sello", fill='black', font=fuente_pequena)
    
    return recibo

# Botón para generar recibo
if st.button("🎫 Generar y Descargar Recibo", use_container_width=True):
    if propietario and casa_seleccionada and monto_pago > 0:
        recibo_img = generar_recibo()
        
        # Convertir a bytes para descarga
        buf = io.BytesIO()
        recibo_img.save(buf, format='PNG')
        byte_im = buf.getvalue()
        
        st.success("✅ Recibo generado exitosamente")
        
        # Mostrar preview
        st.image(recibo_img, caption="Vista previa del recibo", use_column_width=True)
        
        # Botón de descarga
        st.download_button(
            label="⬇️ Descargar Recibo",
            data=byte_im,
            file_name=f"Recibo_{numero_recibo}.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.error("⚠️ Por favor complete todos los campos obligatorios")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px;'>"
    "Diseñado por <strong>Lic. Eduardo Canquiz</strong> - 04145875710"
    "</div>",
    unsafe_allow_html=True
)
