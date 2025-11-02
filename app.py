import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Recibos Valle Verde",
    page_icon="🏠",
    layout="centered"
)

# CSS personalizado
st.markdown("""
    <style>
    .stApp {
        background-color: white;
    }
    .stButton>button {
        background-color: #98D8C8;
        color: black;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #7BC4B4;
    }
    h1, h2, h3 {
        color: black;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #666;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# Título
st.title("🏠 Sistema de Recibos")
st.subheader("Asociación Civil Valle Verde")

# Inicializar session state
if 'propietarios_dict' not in st.session_state:
    st.session_state.propietarios_dict = {}
if 'logo_img' not in st.session_state:
    st.session_state.logo_img = None

# Sidebar para gestión de datos
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Cargar lista de propietarios desde TXT
    st.subheader("Cargar Propietarios")
    archivo_txt = st.file_uploader("Subir archivo TXT con propietarios", type=['txt'])
    if archivo_txt:
        contenido = archivo_txt.read().decode('utf-8')
        lineas = contenido.split('\n')
        propietarios_temp = {}
        
        for linea in lineas[1:]:  # Saltar encabezado
            if linea.strip():
                partes = linea.split('\t')
                if len(partes) >= 2:
                    casa = partes[0].strip()
                    propietario = partes[1].strip().rstrip(',')
                    if casa and propietario:
                        propietarios_temp[casa] = propietario
        
        st.session_state.propietarios_dict = propietarios_temp
        st.success(f"✅ {len(propietarios_temp)} propietarios cargados")
    
    # Agregar propietario manual
    st.subheader("Agregar Propietario")
    col_a, col_b = st.columns(2)
    with col_a:
        nueva_casa_manual = st.text_input("Casa", key="casa_manual")
    with col_b:
        nuevo_propietario_manual = st.text_input("Propietario", key="prop_manual")
    
    if st.button("➕ Agregar", use_container_width=True):
        if nueva_casa_manual and nuevo_propietario_manual:
            st.session_state.propietarios_dict[nueva_casa_manual] = nuevo_propietario_manual
            st.success(f"✅ Casa {nueva_casa_manual} agregada")
            st.rerun()
    
    # Cargar logo
    st.subheader("Logo del Condominio")
    logo_file = st.file_uploader("Subir logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    if logo_file:
        st.session_state.logo_img = Image.open(logo_file)
        st.image(st.session_state.logo_img, width=100)

# Formulario principal
st.header("📝 Generar Recibo")

col1, col2 = st.columns(2)

with col1:
    # Número de casa
    tipo_casa = st.radio("Número de casa:", ["Seleccionar de lista", "Ingresar manualmente"], horizontal=True)
    if tipo_casa == "Seleccionar de lista":
        casas_disponibles = sorted(st.session_state.propietarios_dict.keys(), key=lambda x: int(x) if x.isdigit() else 0)
        if casas_disponibles:
            num_casa = st.selectbox("Seleccione casa:", casas_disponibles)
            propietario_auto = st.session_state.propietarios_dict.get(num_casa, "")
        else:
            st.warning("No hay casas cargadas")
            num_casa = ""
            propietario_auto = ""
    else:
        num_casa = st.text_input("Número de casa:")
        propietario_auto = st.session_state.propietarios_dict.get(num_casa, "")
    
    # Propietario
    tipo_propietario = st.radio("Propietario:", ["Automático", "Ingresar manualmente"], horizontal=True)
    if tipo_propietario == "Automático":
        propietario = st.text_input("Propietario (automático):", value=propietario_auto, disabled=False)
    else:
        propietario = st.text_input("Nombre del propietario:")
    
    # Día del pago
    dia_pago = st.number_input("Día del pago:", min_value=1, max_value=31, value=datetime.now().day)
    
    # Monto del pago
    monto_pago = st.number_input("Monto del pago (Bs.):", min_value=0.0, step=0.01, format="%.2f")

with col2:
    # Mes cancelado
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_cancelado = st.selectbox("Mes cancelado:", meses, index=datetime.now().month - 1)
    
    # Año cancelado
    anio_cancelado = st.selectbox("Año cancelado:", list(range(2025, 2031)), index=0)
    
    # Recibido por (fijo)
    recibido_por = st.text_input("Recibido por:", value="Eleida Ontiveros", disabled=True)
    
    # Referencia del pago
    referencia_pago = st.text_input("Referencia del pago:")

# Generar número de recibo automático
mes_num = str(meses.index(mes_cancelado) + 1).zfill(2)
num_recibo = f"VV-{mes_num}-{anio_cancelado}-{num_casa}"
st.info(f"📄 Número de recibo: **{num_recibo}**")

# Botón para generar recibo
if st.button("🖨️ GENERAR RECIBO", use_container_width=True):
    if not propietario:
        st.error("❌ Debe ingresar un propietario")
    elif not num_casa:
        st.error("❌ Debe ingresar un número de casa")
    elif monto_pago <= 0:
        st.error("❌ Debe ingresar un monto válido")
    else:
        # Crear imagen del recibo
        ancho, alto = 850, 1100
        img = Image.new('RGB', (ancho, alto), 'white')
        draw = ImageDraw.Draw(img)
        
        # Agregar borde
        draw.rectangle([(20, 20), (ancho-20, alto-20)], outline='black', width=3)
        
        y_pos = 50
        
        # Logo si existe
        if st.session_state.logo_img:
            logo_resized = st.session_state.logo_img.copy()
            logo_resized.thumbnail((120, 120))
            img.paste(logo_resized, (50, y_pos))
            y_pos += 140
        
        # Encabezado del condominio
        draw.text((ancho//2, y_pos), "ASOCIACIÓN CIVIL VALLE VERDE", 
                 fill='black', anchor='mt', font=None)
        y_pos += 25
        
        draw.text((ancho//2, y_pos), "RIF: J-298826738", 
                 fill='black', anchor='mt', font=None)
        y_pos += 25
        
        draw.text((ancho//2, y_pos), "Calle Trave N° 19, Valle Verde", 
                 fill='black', anchor='mt', font=None)
        y_pos += 20
        
        draw.text((ancho//2, y_pos), "Morita 1, Turmero, Estado Aragua", 
                 fill='black', anchor='mt', font=None)
        y_pos += 40
        
        # Título RECIBO
        draw.text((ancho//2, y_pos), "RECIBO DE PAGO", 
                 fill='black', anchor='mt', font=None)
        y_pos += 40
        
        # Número de recibo
        draw.text((ancho//2, y_pos), f"N° {num_recibo}", 
                 fill='black', anchor='mt', font=None)
        y_pos += 50
        
        # Datos del recibo
        margen_izq = 80
        
        draw.text((margen_izq, y_pos), f"Fecha: {dia_pago:02d}/{mes_num}/{anio_cancelado}", 
                 fill='black', font=None)
        y_pos += 35
        
        draw.text((margen_izq, y_pos), f"Propietario: {propietario}", 
                 fill='black', font=None)
        y_pos += 35
        
        draw.text((margen_izq, y_pos), f"Casa N°: {num_casa}", 
                 fill='black', font=None)
        y_pos += 35
        
        draw.text((margen_izq, y_pos), f"Concepto: Cuota de condominio", 
                 fill='black', font=None)
        y_pos += 35
        
        draw.text((margen_izq, y_pos), f"Mes cancelado: {mes_cancelado} {anio_cancelado}", 
                 fill='black', font=None)
        y_pos += 50
        
        # Monto
        draw.text((margen_izq, y_pos), f"Monto: Bs. {monto_pago:,.2f}", 
                 fill='black', font=None)
        y_pos += 50
        
        # Referencia
        if referencia_pago:
            draw.text((margen_izq, y_pos), f"Referencia: {referencia_pago}", 
                     fill='black', font=None)
            y_pos += 50
        
        # Recibido por
        y_pos += 30
        draw.text((margen_izq, y_pos), f"Recibido por: {recibido_por}", 
                 fill='black', font=None)
        y_pos += 40
        
        draw.line([(margen_izq, y_pos), (ancho - margen_izq, y_pos)], fill='black', width=2)
        y_pos += 10
        draw.text((ancho//2, y_pos), "Firma", 
                 fill='black', anchor='mt', font=None)
        
        # Footer
        y_pos = alto - 60
        draw.text((ancho//2, y_pos), "Diseñado por Lic. Eduardo Canquiz", 
                 fill='gray', anchor='mt', font=None)
        y_pos += 20
        draw.text((ancho//2, y_pos), "04145875710", 
                 fill='gray', anchor='mt', font=None)
        
        # Convertir imagen a bytes para descarga
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Mostrar preview
        st.success("✅ Recibo generado exitosamente")
        st.image(img, caption="Vista previa del recibo", use_container_width=True)
        
        # Botón de descarga
        st.download_button(
            label="📥 DESCARGAR RECIBO",
            data=buffer,
            file_name=f"Recibo_{num_recibo}.png",
            mime="image/png",
            use_container_width=True
        )

# Footer
st.markdown("""
    <div class="footer">
        <p>Diseñado por Lic. Eduardo Canquiz | 04145875710</p>
    </div>
    """, unsafe_allow_html=True)
