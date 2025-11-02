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
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import io
from datetime import datetime

def generar_recibo_pdf(datos, logo=None):
    """
    Genera un recibo en formato PDF con diseño profesional
    
    Parámetros:
    - datos: diccionario con todos los datos del recibo
    - logo: imagen PIL del logo (opcional)
    """
    
    buffer = io.BytesIO()
    
    # Crear el canvas PDF
    ancho, alto = letter  # 612 x 792 puntos
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Configuración de márgenes
    margen_izq = 50
    margen_der = ancho - 50
    y_pos = alto - 50
    
    # ============================================
    # ENCABEZADO CON LOGO
    # ============================================
    
    if logo:
        try:
            # Guardar logo temporalmente
            logo_buffer = io.BytesIO()
            logo.save(logo_buffer, format='PNG')
            logo_buffer.seek(0)
            
            # Dibujar logo (esquina superior izquierda)
            c.drawImage(logo_buffer, margen_izq, y_pos - 80, width=80, height=80, 
                       preserveAspectRatio=True, mask='auto')
            x_texto = margen_izq + 100
        except:
            x_texto = margen_izq
    else:
        x_texto = margen_izq
    
    # Información del condominio
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(HexColor("#2C5F2D"))
    c.drawString(x_texto, y_pos - 20, "ASOCIACIÓN CIVIL VALLE VERDE")
    
    c.setFont("Helvetica", 11)
    c.setFillColor(black)
    c.drawString(x_texto, y_pos - 40, "Calle 7 N° 79, Valle Verde, Morita 1")
    c.drawString(x_texto, y_pos - 55, "Turmero, Estado Aragua")
    c.drawString(x_texto, y_pos - 70, "RIF: J-298826738")
    
    y_pos -= 110
    
    # ============================================
    # TÍTULO DEL RECIBO
    # ============================================
    
    # Fondo verde menta para el título
    c.setFillColor(HexColor("#98D8C8"))
    c.rect(margen_izq, y_pos - 35, margen_der - margen_izq, 40, fill=True, stroke=False)
    
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 24)
    titulo = "RECIBO DE PAGO"
    ancho_titulo = c.stringWidth(titulo, "Helvetica-Bold", 24)
    c.drawString((ancho - ancho_titulo) / 2, y_pos - 25, titulo)
    
    y_pos -= 60
    
    # ============================================
    # NÚMERO DE RECIBO Y FECHA
    # ============================================
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen_izq, y_pos, f"Recibo N°:")
    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor("#D32F2F"))
    c.drawString(margen_izq + 90, y_pos, datos['numero_recibo'])
    
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 14)
    fecha_texto = f"Fecha: {datos['dia_pago']:02d}/{datos['mes_num']:02d}/{datos['año_cancelado']}"
    ancho_fecha = c.stringWidth(fecha_texto, "Helvetica-Bold", 14)
    c.drawString(margen_der - ancho_fecha, y_pos, fecha_texto)
    
    y_pos -= 40
    
    # Línea divisoria decorativa
    c.setStrokeColor(HexColor("#98D8C8"))
    c.setLineWidth(3)
    c.line(margen_izq, y_pos, margen_der, y_pos)
    
    y_pos -= 35
    
    # ============================================
    # DATOS DEL PROPIETARIO (SECCIÓN CON FONDO)
    # ============================================
    
    c.setFillColor(HexColor("#F5F5F5"))
    c.rect(margen_izq, y_pos - 85, margen_der - margen_izq, 95, fill=True, stroke=True)
    
    c.setFillColor(black)
    y_pos -= 20
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margen_izq + 15, y_pos, "DATOS DEL PROPIETARIO")
    
    y_pos -= 25
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margen_izq + 15, y_pos, "Propietario:")
    c.setFont("Helvetica", 13)
    c.drawString(margen_izq + 110, y_pos, datos['propietario'])
    
    y_pos -= 22
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margen_izq + 15, y_pos, "Casa N°:")
    c.setFont("Helvetica", 13)
    c.drawString(margen_izq + 110, y_pos, str(datos['casa']))
    
    y_pos -= 22
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margen_izq + 15, y_pos, "Período:")
    c.setFont("Helvetica", 13)
    c.drawString(margen_izq + 110, y_pos, f"{datos['mes_cancelado']} {datos['año_cancelado']}")
    
    y_pos -= 45
    
    # ============================================
    # MONTO A PAGAR (DESTACADO)
    # ============================================
    
    c.setFillColor(HexColor("#E8F5F1"))
    c.rect(margen_izq, y_pos - 55, margen_der - margen_izq, 65, fill=True, stroke=True)
    
    y_pos -= 20
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margen_izq + 15, y_pos, "MONTO PAGADO:")
    
    y_pos -= 30
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(HexColor("#2C5F2D"))
    monto_texto = f"Bs. {datos['monto']:,.2f}"
    ancho_monto = c.stringWidth(monto_texto, "Helvetica-Bold", 28)
    c.drawString((ancho - ancho_monto) / 2, y_pos, monto_texto)
    
    y_pos -= 45
    
    # ============================================
    # REFERENCIA DEL PAGO
    # ============================================
    
    if datos.get('referencia'):
        c.setFillColor(black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margen_izq, y_pos, "Referencia del Pago:")
        c.setFont("Helvetica", 12)
        c.drawString(margen_izq + 140, y_pos, datos['referencia'])
        y_pos -= 30
    
    # Línea divisoria
    c.setStrokeColor(HexColor("#98D8C8"))
    c.setLineWidth(2)
    c.line(margen_izq, y_pos, margen_der, y_pos)
    
    y_pos -= 40
    
    # ============================================
    # RECIBIDO POR
    # ============================================
    
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(margen_izq, y_pos, "Recibido por:")
    c.setFont("Helvetica", 13)
    c.drawString(margen_izq + 100, y_pos, datos['recibido_por'])
    
    y_pos -= 70
    
    # ============================================
    # LÍNEA DE FIRMA
    # ============================================
    
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.line(margen_izq, y_pos, margen_izq + 250, y_pos)
    
    y_pos -= 15
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(HexColor("#666666"))
    c.drawString(margen_izq + 80, y_pos, "Firma y Sello")
    
    # ============================================
    # NOTA AL PIE
    # ============================================
    
    y_pos = 80
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(HexColor("#888888"))
    nota = "Este recibo es válido como comprobante de pago de cuota de condominio"
    ancho_nota = c.stringWidth(nota, "Helvetica-Oblique", 9)
    c.drawString((ancho - ancho_nota) / 2, y_pos, nota)
    
    # Línea decorativa inferior
    y_pos -= 15
    c.setStrokeColor(HexColor("#98D8C8"))
    c.setLineWidth(2)
    c.line(margen_izq, y_pos, margen_der, y_pos)
    
    # ============================================
    # BORDE DECORATIVO DE LA PÁGINA
    # ============================================
    
    c.setStrokeColor(HexColor("#98D8C8"))
    c.setLineWidth(3)
    c.rect(30, 30, ancho - 60, alto - 60, fill=False, stroke=True)
    
    # Finalizar y guardar
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer


# ============================================
# FUNCIÓN DE INTEGRACIÓN CON STREAMLIT
# ============================================

def generar_recibo_para_streamlit(propietario, casa, dia_pago, mes_cancelado, 
                                  año_cancelado, monto, recibido_por, 
                                  referencia, numero_recibo, mes_num, logo=None):
    """
    Función wrapper para integrar fácilmente con Streamlit
    """
    
    datos = {
        'propietario': propietario,
        'casa': casa,
        'dia_pago': dia_pago,
        'mes_cancelado': mes_cancelado,
        'año_cancelado': año_cancelado,
        'monto': monto,
        'recibido_por': recibido_por,
        'referencia': referencia,
        'numero_recibo': numero_recibo,
        'mes_num': mes_num
    }
    
    return generar_recibo_pdf(datos, logo)


# ============================================
# EJEMPLO DE USO
# ============================================
"""
# En tu código de Streamlit, reemplaza la función generar_recibo() con:

if st.button("🎫 Generar y Descargar Recibo", use_container_width=True):
    if propietario and casa_seleccionada and monto_pago > 0:
        
        # Generar el PDF
        pdf_buffer = generar_recibo_para_streamlit(
            propietario=propietario,
            casa=casa_seleccionada,
            dia_pago=dia_pago,
            mes_cancelado=mes_cancelado,
            año_cancelado=año_cancelado,
            monto=monto_pago,
            recibido_por=recibido_por,
            referencia=referencia_pago,
            numero_recibo=numero_recibo,
            mes_num=mes_num,
            logo=st.session_state.logo
        )
        
        st.success("✅ Recibo generado exitosamente")
        
        # Botón de descarga
        st.download_button(
            label="⬇️ Descargar Recibo PDF",
            data=pdf_buffer,
            file_name=f"Recibo_{numero_recibo}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.error("⚠️ Por favor complete todos los campos obligatorios")
"""
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
