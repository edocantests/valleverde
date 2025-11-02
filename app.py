import streamlit as st
from datetime import datetime
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from PIL import Image
except ImportError as e:
    st.error("""
    ⚠️ **Error de dependencias**
    
    Por favor instala los paquetes necesarios:
    
    ```bash
    pip install reportlab Pillow
    ```
    
    O crea un archivo `requirements.txt` con:
    ```
    streamlit
    reportlab
    Pillow
    ```
    """)
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Recibos - Valle Verde",
    page_icon="🏘️",
    layout="centered"
)

# CSS personalizado
st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: black !important;
    }
    .stButton>button {
        background-color: #98D8C8;
        color: black;
        border: none;
        border-radius: 5px;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #7BC4B4;
        color: black;
    }
    .section-header {
        background-color: #98D8C8;
        padding: 10px;
        border-radius: 5px;
        margin: 20px 0 10px 0;
        font-weight: bold;
        color: black !important;
    }
    .info-box {
        background-color: #f0f0f0;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        border-left: 4px solid #98D8C8;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'propietarios' not in st.session_state:
    st.session_state.propietarios = {}
if 'logo' not in st.session_state:
    st.session_state.logo = None
if '_syncing' not in st.session_state:
    st.session_state['_syncing'] = False

# Función para cargar propietarios desde TXT
def cargar_propietarios_txt(archivo):
    try:
        contenido = archivo.read().decode('utf-8')
        propietarios = {}
        for linea in contenido.strip().split('\n'):
            if ',' in linea:
                casa, nombre = linea.split(',', 1)
                casa = casa.strip()
                nombre = nombre.strip()
                if casa:
                    propietarios[casa] = nombre
        return propietarios
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return {}

# Función para generar PDF
def generar_pdf(datos):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Top margin
    top_margin = height - 30

    # Prepare positions depending on logo
    header_y = top_margin - 10  # default
    logo_drawn = False

    if st.session_state.logo:
        try:
            img = st.session_state.logo.convert("RGBA")
            iw, ih = img.size  # original pixels
            desired_w = 100.0
            scale = desired_w / float(iw)
            desired_h = float(ih) * scale
            logo_x = 50
            logo_y = top_margin - desired_h  # y-coordinate where logo bottom will be

            logo_reader = ImageReader(img)
            # draw the image
            c.drawImage(logo_reader, logo_x, logo_y, width=desired_w, height=desired_h, preserveAspectRatio=True, mask='auto')
            logo_drawn = True

            # center header vertically with logo
            header_y = logo_y + desired_h / 2 + 6
            # ensure header_y doesn't go too high/low
            header_y = min(header_y, top_margin - 6)
        except Exception:
            # fallback to default header_y
            header_y = top_margin - 10

    # Encabezado del condominio
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, header_y, "Asociación Civil Valle Verde")

    c.setFont("Helvetica", 10)
    y_position = header_y - 20
    c.drawString(200, y_position, "Calle 7 N° 79, Valle Verde, Morita 1")
    y_position -= 15
    c.drawString(200, y_position, "Turmero, Estado Aragua")
    y_position -= 15
    c.drawString(200, y_position, "RIF: J-298826738")

    # Línea separadora
    y_position -= 30
    c.line(50, y_position, width - 50, y_position)

    # Título del recibo
    y_position -= 40
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, y_position, "RECIBO DE PAGO")

    # Número de recibo
    y_position -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, f"Recibo N°: {datos.get('numero_recibo','')}")

    # Información del recibo
    y_position -= 40
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y_position, "Datos del Pago:")

    y_position -= 25
    c.setFont("Helvetica", 11)
    c.drawString(70, y_position, f"Propietario: {datos.get('propietario','')}")

    y_position -= 20
    c.drawString(70, y_position, f"Casa N°: {datos.get('numero_casa','')}")

    y_position -= 20
    c.drawString(70, y_position, f"Fecha de Pago: {datos.get('dia_pago','')}")

    y_position -= 20
    c.drawString(70, y_position, f"Mes Cancelado: {datos.get('mes_cancelado','')}")

    y_position -= 20
    c.drawString(70, y_position, f"Año Cancelado: {datos.get('año_cancelado','')}")

    y_position -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(70, y_position, f"Monto Pagado: Bs. {datos.get('monto_pago','')}")

    if datos.get('referencia'):
        y_position -= 25
        c.setFont("Helvetica", 11)
        c.drawString(70, y_position, f"Referencia: {datos.get('referencia')}")

    # Recibido por
    y_position -= 40
    c.setFont("Helvetica-Bold", 11)
    c.drawString(70, y_position, f"Recibido por: {datos.get('recibido_por','')}")

    # Línea de firma
    y_position -= 60
    c.line(70, y_position, 300, y_position)
    y_position -= 15
    c.setFont("Helvetica", 9)
    c.drawString(70, y_position, "Firma y Sello")

    # Nota al pie
    footer_y = 50
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, footer_y, "Gracias por su pago puntual")

    c.save()
    buffer.seek(0)
    return buffer

# Título principal
st.title("🏘️ Sistema de Recibos - Valle Verde")
st.markdown("---")

# Sección 1: Configuración
st.markdown('<div class="section-header">📋 CONFIGURACIÓN INICIAL</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Logo del Condominio")
    logo_file = st.file_uploader("Cargar logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'], key="logo_upload")
    if logo_file:
        try:
            st.session_state.logo = Image.open(logo_file)
            st.image(st.session_state.logo, width=150)
        except Exception as e:
            st.error(f"Error al leer la imagen: {e}")

with col2:
    st.markdown("#### Lista de Propietarios")
    txt_file = st.file_uploader("Cargar lista (TXT)", type=['txt'], key="propietarios_txt")
    if txt_file:
        nuevos_propietarios = cargar_propietarios_txt(txt_file)
        if nuevos_propietarios:
            st.session_state.propietarios.update(nuevos_propietarios)
            st.success(f"✅ {len(nuevos_propietarios)} propietarios cargados")
    
    st.markdown('<small>Formato: Casa,Nombre (ej: 1,Juan Pérez)</small>', unsafe_allow_html=True)

# Agregar propietario manualmente
st.markdown("#### Agregar Propietario Manualmente")
col_a, col_b, col_c = st.columns([2, 3, 1])
with col_a:
    nueva_casa = st.text_input("N° de Casa", key="nueva_casa", placeholder="Ej: 15")
with col_b:
    nuevo_nombre = st.text_input("Nombre Completo", key="nuevo_nombre", placeholder="Ej: María González")
with col_c:
    st.write("")
    st.write("")
    if st.button("➕ Agregar"):
        if nueva_casa and nuevo_nombre:
            st.session_state.propietarios[str(nueva_casa).strip()] = nuevo_nombre.strip()
            st.success("✅ Propietario agregado")
            st.experimental_rerun()

# Mostrar propietarios cargados
if st.session_state.propietarios:
    with st.expander(f"👥 Ver Propietarios Registrados ({len(st.session_state.propietarios)})"):
        for casa, nombre in sorted(st.session_state.propietarios.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
            st.text(f"Casa {casa}: {nombre}")

st.markdown("---")

# Sección 2: Generar Recibo
st.markdown('<div class="section-header">🧾 GENERAR RECIBO</div>', unsafe_allow_html=True)

# Fila 1: Propietario y Casa
col1, col2 = st.columns(2)

# prepare ordered lists
def sort_key(x):
    return int(x) if str(x).isdigit() else str(x)

propietario_list = ["Escribir manualmente..."] + [v for k, v in sorted(st.session_state.propietarios.items(), key=lambda x: sort_key(x[0]))]
casa_list = ["Escribir manualmente..."] + [k for k in sorted(st.session_state.propietarios.keys(), key=sort_key)]

with col1:
    st.markdown("#### Propietario")
    propietario_seleccion = st.selectbox(
        "Seleccione o escriba el nombre",
        propietario_list,
        key="propietario_select",
        label_visibility="collapsed"
    )
    if propietario_seleccion == "Escribir manualmente...":
        propietario_manual = st.text_input("Nombre del propietario", key="propietario_manual", placeholder="Escriba el nombre")
    else:
        propietario_manual = ""  # clear manual field for clarity

with col2:
    st.markdown("#### Número de Casa")
    casa_seleccion = st.selectbox(
        "Seleccione o escriba el número",
        casa_list,
        key="casa_select",
        label_visibility="collapsed"
    )
    if casa_seleccion == "Escribir manualmente...":
        casa_manual = st.text_input("Número de casa", key="casa_manual", placeholder="Ej: 25")
    else:
        casa_manual = ""

# Sincronización bidireccional (Propietario <-> Casa)
if not st.session_state['_syncing']:
    st.session_state['_syncing'] = True
    try:
        # Si seleccionaron propietario desde la lista, buscar la casa y actualizar la selectbox de casa
        if propietario_seleccion != "Escribir manualmente..." and propietario_seleccion:
            found_casa = next((k for k, v in st.session_state.propietarios.items() if v == propietario_seleccion), None)
            if found_casa:
                # actualizamos el value de la caja casa_select
                st.session_state['casa_select'] = found_casa
        # Si seleccionaron casa desde la lista, buscar el propietario y actualizar la selectbox de propietario
        if casa_seleccion != "Escribir manualmente..." and casa_seleccion:
            owner = st.session_state.propietarios.get(casa_seleccion)
            if owner:
                st.session_state['propietario_select'] = owner
    finally:
        st.session_state['_syncing'] = False

# Determinar valores finales para propietario y numero_casa (ya sincronizados)
if st.session_state.get('propietario_select') and st.session_state['propietario_select'] != "Escribir manualmente...":
    propietario = st.session_state['propietario_select']
else:
    propietario = st.session_state.get('propietario_manual', '').strip()

if st.session_state.get('casa_select') and st.session_state['casa_select'] != "Escribir manualmente...":
    numero_casa = st.session_state['casa_select']
else:
    numero_casa = st.session_state.get('casa_manual', '').strip()

# Fila 2: Mes y Año
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### Mes Cancelado")
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_cancelado = st.selectbox("Seleccione el mes", meses, label_visibility="collapsed")

with col4:
    st.markdown("#### Año Cancelado")
    años = list(range(2025, 2031))
    año_cancelado = st.selectbox("Seleccione el año", años, label_visibility="collapsed")

# Fila 3: Día y Monto
col5, col6 = st.columns(2)

with col5:
    st.markdown("#### Día del Pago")
    dia_pago = st.date_input("Fecha del pago", datetime.now(), label_visibility="collapsed")

with col6:
    st.markdown("#### Monto del Pago (Bs.)")
    monto_pago = st.number_input("Monto en bolívares", min_value=0.0, step=0.01, format="%.2f", label_visibility="collapsed")

# Fila 4: Referencia
st.markdown("#### Referencia del Pago")
referencia = st.text_input("Número de referencia o método de pago", placeholder="Ej: Transferencia 123456789", label_visibility="collapsed")

# Recibido por (fijo)
recibido_por = "Eleida Ontiveros"

# Generar número de recibo automáticamente (si hay casa, mes y año)
numero_recibo = ""
if numero_casa and mes_cancelado and año_cancelado:
    mes_num = str(meses.index(mes_cancelado) + 1).zfill(2)
    numero_recibo = f"VV-{mes_num}-{año_cancelado}-{numero_casa}"
    
    st.markdown("#### Número de Recibo")
    st.markdown(f'<div class="info-box"><strong>{numero_recibo}</strong></div>', unsafe_allow_html=True)

# Botón de generar
st.markdown("---")

if st.button("📥 GENERAR Y DESCARGAR RECIBO PDF", use_container_width=True):
    if not propietario:
        st.error("⚠️ Debe ingresar el nombre del propietario")
    elif not numero_casa:
        st.error("⚠️ Debe ingresar el número de casa")
    elif monto_pago <= 0:
        st.error("⚠️ Debe ingresar un monto válido")
    else:
        datos_recibo = {
            'propietario': propietario,
            'numero_casa': numero_casa,
            'dia_pago': dia_pago.strftime("%d/%m/%Y"),
            'monto_pago': f"{monto_pago:,.2f}",
            'numero_recibo': numero_recibo,
            'mes_cancelado': mes_cancelado,
            'año_cancelado': año_cancelado,
            'recibido_por': recibido_por,
            'referencia': referencia
        }
        
        pdf = generar_pdf(datos_recibo)
        
        st.success("✅ Recibo generado exitosamente")
        st.download_button(
            label="💾 Descargar PDF",
            data=pdf,
            file_name=f"Recibo_{numero_recibo}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; padding: 20px;">'
    '💼 Diseñado por Lic. Eduardo Canquiz<br>'
    '📱 04145875710'
    '</div>',
    unsafe_allow_html=True
)
