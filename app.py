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
    .main {
        background-color: white;
    }
    .stButton>button {
        background-color: #98D8C8;
        color: black;
        font-weight: bold;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #7BC4B4;
    }
    h1, h2, h3 {
        color: black;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: black;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #ddd;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.title("🏠 Sistema de Recibos - Valle Verde")

# Inicializar session state
if 'propietarios' not in st.session_state:
    st.session_state.propietarios = [
        "Juan Pérez",
        "María González",
        "Carlos Rodríguez",
        "Ana Martínez",
        "Luis Fernández"
    ]

# Sidebar para gestión de propietarios
with st.sidebar:
    st.header("📋 Gestión de Propietarios")
    
    # Mostrar lista actual
    st.markdown("**Lista actual:**")
    for prop in st.session_state.propietarios:
        st.text(f"• {prop}")
    
    st.markdown("---")
    
    # Agregar nuevo propietario
    st.subheader("Agregar Propietario")
    nuevo_prop = st.text_input("Nombre completo")
    if st.button("➕ Agregar", key="add_prop"):
        if nuevo_prop and nuevo_prop not in st.session_state.propietarios:
            st.session_state.propietarios.append(nuevo_prop)
            st.success(f"✓ {nuevo_prop} agregado")
            st.rerun()
    
    # Eliminar propietario
    st.subheader("Eliminar Propietario")
    prop_eliminar = st.selectbox("Seleccionar", st.session_state.propietarios, key="del_select")
    if st.button("🗑️ Eliminar", key="del_prop"):
        st.session_state.propietarios.remove(prop_eliminar)
        st.success(f"✓ {prop_eliminar} eliminado")
        st.rerun()

# Sección principal
st.markdown("---")

# Logo del condominio
st.markdown('<div class="section-title">Logo del Condominio</div>', unsafe_allow_html=True)
logo_file = st.file_uploader("Cargar logo (PNG o JPG)", type=['png', 'jpg', 'jpeg'])

st.markdown("---")

# Formulario de recibo
st.header("📝 Datos del Recibo")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">Propietario</div>', unsafe_allow_html=True)
    tipo_prop = st.radio("", ["Seleccionar de lista", "Ingresar manualmente"], label_visibility="collapsed", horizontal=True)
    
    if tipo_prop == "Seleccionar de lista":
        propietario = st.selectbox("", st.session_state.propietarios, label_visibility="collapsed")
    else:
        propietario = st.text_input("", placeholder="Nombre del propietario", label_visibility="collapsed")

with col2:
    st.markdown('<div class="section-title">Número de Casa</div>', unsafe_allow_html=True)
    tipo_casa = st.radio("", ["Lista predefinida", "Ingresar manualmente"], label_visibility="collapsed", horizontal=True, key="radio_casa")
    
    if tipo_casa == "Lista predefinida":
        casas = [f"Casa {i}" for i in range(1, 51)]
        num_casa = st.selectbox("", casas, label_visibility="collapsed")
    else:
        num_casa = st.text_input("", placeholder="Ej: Casa 15", label_visibility="collapsed", key="casa_manual")

col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-title">Día del Pago</div>', unsafe_allow_html=True)
    dia_pago = st.number_input("", min_value=1, max_value=31, value=datetime.now().day, label_visibility="collapsed")

with col4:
    st.markdown('<div class="section-title">Monto del Pago (Bs.)</div>', unsafe_allow_html=True)
    monto = st.number_input("", min_value=0.0, step=0.01, format="%.2f", label_visibility="collapsed")

col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="section-title">Mes Cancelado</div>', unsafe_allow_html=True)
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_cancelado = st.selectbox("", meses, label_visibility="collapsed")

with col6:
    st.markdown('<div class="section-title">Año Cancelado</div>', unsafe_allow_html=True)
    anio_cancelado = st.selectbox("", list(range(2025, 2031)), label_visibility="collapsed")

st.markdown('<div class="section-title">Referencia del Pago</div>', unsafe_allow_html=True)
referencia = st.text_input("", placeholder="Ej: Transferencia, Pago móvil, Efectivo", label_visibility="collapsed", key="ref_pago")

# Generar número de recibo automático
num_mes = str(meses.index(mes_cancelado) + 1).zfill(2)
casa_num = num_casa.split()[-1] if "Casa" in num_casa else num_casa
num_recibo = f"VV-{num_mes}-{anio_cancelado}-{casa_num}"

st.markdown('<div class="section-title">Número de Recibo (Generado automáticamente)</div>', unsafe_allow_html=True)
st.text_input("", value=num_recibo, disabled=True, label_visibility="collapsed", key="num_recibo_display")

st.markdown("---")

# Botón de generar recibo
if st.button("📄 GENERAR RECIBO", use_container_width=True):
    if not propietario or not num_casa or monto <= 0:
        st.error("⚠️ Por favor complete todos los campos obligatorios")
    else:
        # Crear recibo
        img_width = 800
        img_height = 1000
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            # Intentar cargar fuentes
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        except:
            font_title = ImageFont.load_default()
            font_header = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        y_pos = 30
        
        # Logo si existe
        if logo_file:
            logo = Image.open(logo_file)
            logo.thumbnail((150, 150))
            logo_x = (img_width - logo.width) // 2
            img.paste(logo, (logo_x, y_pos))
            y_pos += logo.height + 20
        
        # Encabezado del condominio
        draw.text((img_width//2, y_pos), "ASOCIACIÓN CIVIL VALLE VERDE", 
                  fill='black', font=font_title, anchor="mm")
        y_pos += 40
        
        draw.text((img_width//2, y_pos), "RIF: J-298826738", 
                  fill='black', font=font_normal, anchor="mm")
        y_pos += 25
        
        direccion = "Calle Trave N° 19, Valle Verde, Morita 1"
        draw.text((img_width//2, y_pos), direccion, 
                  fill='black', font=font_small, anchor="mm")
        y_pos += 20
        
        draw.text((img_width//2, y_pos), "Turmero, Estado Aragua", 
                  fill='black', font=font_small, anchor="mm")
        y_pos += 40
        
        # Línea separadora
        draw.line([(50, y_pos), (img_width-50, y_pos)], fill='black', width=2)
        y_pos += 30
        
        # Título RECIBO
        draw.text((img_width//2, y_pos), "RECIBO DE PAGO", 
                  fill='black', font=font_header, anchor="mm")
        y_pos += 40
        
        # Número de recibo
        draw.text((100, y_pos), f"Recibo N°: {num_recibo}", 
                  fill='black', font=font_normal)
        y_pos += 35
        
        # Fecha
        draw.text((100, y_pos), f"Fecha: {dia_pago} de {mes_cancelado} de {anio_cancelado}", 
                  fill='black', font=font_normal)
        y_pos += 50
        
        # Datos del pago
        draw.text((100, y_pos), f"Recibido de:", fill='black', font=font_header)
        y_pos += 30
        draw.text((120, y_pos), f"{propietario}", fill='black', font=font_normal)
        y_pos += 35
        
        draw.text((100, y_pos), f"Casa N°: {num_casa}", fill='black', font=font_normal)
        y_pos += 50
        
        draw.text((100, y_pos), f"La cantidad de:", fill='black', font=font_header)
        y_pos += 30
        draw.text((120, y_pos), f"Bs. {monto:,.2f}", fill='black', font=font_normal)
        y_pos += 50
        
        draw.text((100, y_pos), f"Por concepto de:", fill='black', font=font_header)
        y_pos += 30
        draw.text((120, y_pos), f"Cuota de condominio - {mes_cancelado} {anio_cancelado}", 
                  fill='black', font=font_normal)
        y_pos += 50
        
        draw.text((100, y_pos), f"Referencia: {referencia}", fill='black', font=font_normal)
        y_pos += 60
        
        # Recibido por
        draw.line([(100, y_pos), (400, y_pos)], fill='black', width=1)
        y_pos += 5
        draw.text((100, y_pos), "Recibido por: Eleida Ontiveros", 
                  fill='black', font=font_normal)
        y_pos += 80
        
        # Línea separadora
        draw.line([(50, y_pos), (img_width-50, y_pos)], fill='#98D8C8', width=2)
        y_pos += 30
        
        # Footer
        draw.text((img_width//2, y_pos), "Diseñado por Lic. Eduardo Canquiz", 
                  fill='#666666', font=font_small, anchor="mm")
        y_pos += 20
        draw.text((img_width//2, y_pos), "04145875710", 
                  fill='#666666', font=font_small, anchor="mm")
        
        # Convertir a bytes para descarga
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        st.success("✓ Recibo generado exitosamente")
        
        # Mostrar preview
        st.image(img, caption="Vista previa del recibo", use_container_width=True)
        
        # Botón de descarga
        st.download_button(
            label="⬇️ DESCARGAR RECIBO",
            data=buf,
            file_name=f"Recibo_{num_recibo}.png",
            mime="image/png",
            use_container_width=True
        )

# Footer
st.markdown(
    '<div class="footer">Diseñado por Lic. Eduardo Canquiz • 04145875710</div>',
    unsafe_allow_html=True
)
