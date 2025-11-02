import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import re

# ==================== CONFIGURACIÓN INICIAL ====================
st.set_page_config(
    page_title="Generador de Recibos - Condominio",
    page_icon="🏢",
    layout="wide"
)

# Inicializar session_state
if 'residentes' not in st.session_state:
    st.session_state.residentes = []
if 'contador_recibos' not in st.session_state:
    st.session_state.contador_recibos = 1
if 'logo_condominio' not in st.session_state:
    st.session_state.logo_condominio = None

# ==================== FUNCIONES AUXILIARES ====================

def parse_residentes_txt(contenido):
    """
    Parsea el contenido de un archivo .txt con residentes.
    Formato aceptado por línea:
    - Nombre
    - Nombre|NúmeroCasa
    """
    residentes = []
    lineas = contenido.strip().split('\n')
    
    for idx, linea in enumerate(lineas, 1):
        linea = linea.strip()
        if not linea or linea.startswith('FORMATO'):  # Ignorar líneas vacías o de formato
            continue
        
        if '|' in linea:
            partes = linea.split('|')
            if len(partes) >= 2:
                nombre = partes[0].strip()
                casa = partes[1].strip()
                residentes.append({'nombre': nombre, 'casa': casa})
            else:
                st.warning(f"Línea {idx} mal formateada: {linea}")
        else:
            residentes.append({'nombre': linea, 'casa': ''})
    
    return residentes

def limpiar_nombre_archivo(texto):
    """Limpia un texto para usarlo como nombre de archivo"""
    texto = re.sub(r'[^\w\s-]', '', texto)
    texto = re.sub(r'[\s]+', '_', texto)
    return texto[:50]  # Limitar longitud

def generar_placeholder_logo():
    """Genera un logo placeholder usando Pillow"""
    img = Image.new('RGB', (200, 100), color=(70, 130, 180))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    texto = "LOGO\nCONDOMINIO"
    bbox = draw.textbbox((0, 0), texto, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (200 - text_width) / 2
    y = (100 - text_height) / 2
    draw.text((x, y), texto, fill='white', font=font)
    
    return img

def generar_pdf_recibo(datos_recibo, logo_img=None):
    """
    Genera un PDF del recibo con los datos proporcionados.
    
    Args:
        datos_recibo: dict con claves: nombre, casa, monto, fecha, concepto, 
                     numero_recibo, nombre_condominio, pie_pagina
        logo_img: PIL Image o None
    
    Returns:
        bytes del PDF generado
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Guardar logo temporalmente si existe
    logo_path = None
    if logo_img:
        logo_bytes = BytesIO()
        logo_img.save(logo_bytes, format='PNG')
        logo_bytes.seek(0)
        # FPDF necesita un path, lo guardamos temporalmente
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp.write(logo_bytes.read())
            logo_path = tmp.name
    
    # ===== ENCABEZADO =====
    # Logo
    if logo_path:
        try:
            pdf.image(logo_path, x=10, y=8, w=40)
        except:
            pass
    
    # Título
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, '', 0, 1)  # Espacio para logo
    pdf.cell(0, 10, f"RECIBO DE PAGO - {datos_recibo.get('nombre_condominio', 'CONDOMINIO')}", 0, 1, 'C')
    pdf.ln(5)
    
    # Número de recibo y fecha en la esquina superior derecha
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, f"Recibo N°: {datos_recibo['numero_recibo']}", 0, 1, 'R')
    pdf.cell(0, 5, f"Fecha: {datos_recibo['fecha']}", 0, 1, 'R')
    pdf.ln(5)
    
    # ===== DATOS DEL RESIDENTE =====
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'DATOS DEL RESIDENTE', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    # Tabla de datos
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(50, 8, 'Nombre:', 1, 0, 'L', True)
    pdf.cell(0, 8, datos_recibo['nombre'], 1, 1, 'L')
    pdf.cell(50, 8, 'Casa/Apartamento:', 1, 0, 'L', True)
    pdf.cell(0, 8, str(datos_recibo['casa']), 1, 1, 'L')
    pdf.ln(5)
    
    # ===== DETALLE DEL PAGO =====
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'DETALLE DEL PAGO', 0, 1, 'L')
    pdf.set_font('Arial', '', 11)
    
    pdf.cell(50, 8, 'Concepto:', 1, 0, 'L', True)
    pdf.cell(0, 8, datos_recibo['concepto'], 1, 1, 'L')
    pdf.cell(50, 8, 'Monto:', 1, 0, 'L', True)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, f"${datos_recibo['monto']:.2f}", 1, 1, 'L')
    pdf.set_font('Arial', '', 11)
    pdf.cell(50, 8, 'Fecha de cancelación:', 1, 0, 'L', True)
    pdf.cell(0, 8, datos_recibo['fecha'], 1, 1, 'L')
    pdf.ln(10)
    
    # ===== ESPACIO PARA FIRMA =====
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 8, 'FIRMA Y SELLO', 0, 1, 'C')
    pdf.ln(15)
    pdf.set_font('Arial', '', 9)
    pdf.cell(0, 5, '_' * 50, 0, 1, 'C')
    pdf.cell(0, 5, 'Firma autorizada', 0, 1, 'C')
    pdf.ln(10)
    
    # ===== PIE DE PÁGINA =====
    pdf.set_y(-30)
    pdf.set_font('Arial', 'I', 8)
    pie_texto = datos_recibo.get('pie_pagina', 'Gracias por su pago puntual.')
    pdf.multi_cell(0, 5, pie_texto, 0, 'C')
    
    # Limpiar archivo temporal del logo
    if logo_path:
        try:
            import os
            os.unlink(logo_path)
        except:
            pass
    
    # Retornar PDF como bytes
    return pdf.output(dest='S').encode('latin-1')

# ==================== INTERFAZ DE USUARIO ====================

st.title("🏢 Generador de Recibos para Condominio")
st.markdown("---")

# ===== SIDEBAR: GESTIÓN DE RESIDENTES =====
with st.sidebar:
    st.header("📋 Gestión de Residentes")
    
    # Agregar residente manualmente
    st.subheader("➕ Agregar Residente")
    with st.form("form_agregar_residente"):
        nuevo_nombre = st.text_input("Nombre completo*")
        nueva_casa = st.text_input("Número de casa/apto")
        submit_agregar = st.form_submit_button("Agregar")
        
        if submit_agregar:
            if not nuevo_nombre.strip():
                st.error("El nombre es obligatorio")
            else:
                st.session_state.residentes.append({
                    'nombre': nuevo_nombre.strip(),
                    'casa': nueva_casa.strip()
                })
                st.success(f"✅ {nuevo_nombre} agregado")
                st.rerun()
    
    st.markdown("---")
    
    # Importar residentes desde archivo
    st.subheader("📁 Importar desde archivo")
    archivo_residentes = st.file_uploader(
        "Cargar archivo .txt",
        type=['txt'],
        help="Formato: Nombre o Nombre|Casa por línea"
    )
    
    if archivo_residentes:
        try:
            contenido = archivo_residentes.read().decode('utf-8')
            residentes_importados = parse_residentes_txt(contenido)
            
            if residentes_importados:
                if st.button("Importar residentes"):
                    st.session_state.residentes.extend(residentes_importados)
                    st.success(f"✅ {len(residentes_importados)} residentes importados")
                    st.rerun()
            else:
                st.warning("No se encontraron residentes válidos en el archivo")
        except Exception as e:
            st.error(f"Error al leer el archivo: {str(e)}")
    
    st.markdown("---")
    
    # Lista de residentes con opciones
    st.subheader(f"👥 Residentes registrados ({len(st.session_state.residentes)})")
    
    if st.session_state.residentes:
        with st.expander("Ver lista de residentes", expanded=False):
            for idx, residente in enumerate(st.session_state.residentes):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.text(residente['nombre'])
                with col2:
                    st.text(f"Casa: {residente['casa'] or 'N/A'}")
                with col3:
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.residentes.pop(idx)
                        st.rerun()
            
            if st.button("🗑️ Limpiar todos"):
                st.session_state.residentes = []
                st.rerun()
    else:
        st.info("No hay residentes registrados")

# ===== ÁREA PRINCIPAL: GENERAR RECIBO =====

st.header("📄 Generar Recibo")

# Configuración del condominio
with st.expander("⚙️ Configuración del condominio", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nombre_condominio = st.text_input(
            "Nombre del condominio",
            value="ASOCIACIÓN CIVIL VALLE VERDE",
            help="Aparecerá en el encabezado del recibo"
        )
    with col2:
        pie_pagina = st.text_area(
            "Pie de página",
            value="Gracias por su pago puntual.\nContacto: info@condominio.com | Tel: (123) 456-7890",
            height=80
        )
    
    # Subir logo
    logo_upload = st.file_uploader(
        "Logo del condominio (opcional)",
        type=['png', 'jpg', 'jpeg'],
        help="Se mostrará en la parte superior del recibo"
    )
    
    if logo_upload:
        st.session_state.logo_condominio = Image.open(logo_upload)
        st.image(st.session_state.logo_condominio, width=200)

st.markdown("---")

# Formulario para generar recibo
col_form1, col_form2 = st.columns(2)

with col_form1:
    st.subheader("Datos del residente")
    
    # Seleccionar residente existente o manual
    opciones_residentes = ['-- Ingresar manualmente --'] + [
        f"{r['nombre']} - Casa {r['casa']}" if r['casa'] else r['nombre']
        for r in st.session_state.residentes
    ]
    
    with st.expander("🔍 Seleccionar residente existente", expanded=True):
        residente_seleccionado = st.selectbox(
            "Residentes registrados",
            options=range(len(opciones_residentes)),
            format_func=lambda x: opciones_residentes[x]
        )
    
    # Campos del recibo
    if residente_seleccionado == 0:
        # Manual
        nombre_recibo = st.text_input("Nombre del residente*", key="nombre_manual")
        casa_recibo = st.text_input("Número de casa/apto*", key="casa_manual")
    else:
        # Autocompletar desde selección
        idx_real = residente_seleccionado - 1
        residente_data = st.session_state.residentes[idx_real]
        nombre_recibo = st.text_input(
            "Nombre del residente*",
            value=residente_data['nombre'],
            key="nombre_auto"
        )
        casa_recibo = st.text_input(
            "Número de casa/apto*",
            value=residente_data['casa'],
            key="casa_auto"
        )

with col_form2:
    st.subheader("Detalles del pago")
    
    # Concepto predefinido o manual
    with st.expander("💡 Conceptos predefinidos", expanded=False):
        conceptos_predefinidos = [
            "Mantenimiento mensual",
            "Cuota de agua",
            "Servicio de limpieza",
            "Servicio de seguridad",
            "Reparaciones comunes",
            "Fondo de reserva",
            "Otros"
        ]
        concepto_predefinido = st.selectbox("Seleccionar concepto", conceptos_predefinidos)
    
    concepto_recibo = st.text_input(
        "Concepto del pago*",
        value=concepto_predefinido,
        help="Puede modificar o escribir un concepto personalizado"
    )
    
    monto_recibo = st.number_input(
        "Monto ($)*",
        min_value=0.0,
        step=0.01,
        format="%.2f"
    )
    
    fecha_recibo = st.date_input(
        "Fecha de cancelación*",
        value=datetime.now()
    )
    
    numero_recibo = st.text_input(
        "Número de recibo",
        value=f"{datetime.now().strftime('%Y%m%d')}-{st.session_state.contador_recibos:04d}",
        help="Se genera automáticamente, pero puede modificarse"
    )

st.markdown("---")

# Botón para generar PDF
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])

with col_btn2:
    if st.button("🎯 GENERAR RECIBO PDF", type="primary", use_container_width=True):
        # Validaciones
        errores = []
        if not nombre_recibo.strip():
            errores.append("El nombre del residente es obligatorio")
        if not casa_recibo.strip():
            errores.append("El número de casa es obligatorio")
        if not concepto_recibo.strip():
            errores.append("El concepto del pago es obligatorio")
        if monto_recibo <= 0:
            errores.append("El monto debe ser mayor a 0")
        if not numero_recibo.strip():
            errores.append("El número de recibo es obligatorio")
        
        if errores:
            for error in errores:
                st.error(f"❌ {error}")
        else:
            try:
                # Preparar datos del recibo
                datos_recibo = {
                    'nombre': nombre_recibo,
                    'casa': casa_recibo,
                    'monto': monto_recibo,
                    'fecha': fecha_recibo.strftime('%d/%m/%Y'),
                    'concepto': concepto_recibo,
                    'numero_recibo': numero_recibo,
                    'nombre_condominio': nombre_condominio,
                    'pie_pagina': pie_pagina
                }
                
                # Logo (usar el cargado o generar placeholder)
                logo_img = st.session_state.logo_condominio
                if logo_img is None:
                    logo_img = generar_placeholder_logo()
                
                # Generar PDF
                pdf_bytes = generar_pdf_recibo(datos_recibo, logo_img)
                
                # Incrementar contador
                st.session_state.contador_recibos += 1
                
                # Nombre del archivo
                nombre_archivo = f"recibo_{limpiar_nombre_archivo(numero_recibo)}_{limpiar_nombre_archivo(nombre_recibo)}.pdf"
                
                # Mostrar éxito y botón de descarga
                st.success("✅ Recibo generado exitosamente")
                
                st.download_button(
                    label="⬇️ DESCARGAR RECIBO PDF",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Resumen del recibo
                with st.expander("📋 Resumen del recibo generado", expanded=True):
                    st.markdown(f"""
                    **Recibo N°:** {numero_recibo}  
                    **Residente:** {nombre_recibo}  
                    **Casa:** {casa_recibo}  
                    **Concepto:** {concepto_recibo}  
                    **Monto:** ${monto_recibo:.2f}  
                    **Fecha:** {fecha_recibo.strftime('%d/%m/%Y')}
                    """)
                
            except Exception as e:
                st.error(f"❌ Error al generar el recibo: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.9em;'>"
    "Generador de Recibos para Condominios | Desarrollado con Streamlit"
    "</div>",
    unsafe_allow_html=True
)
```

# requirements.txt
```
streamlit==1.31.0
fpdf2==2.7.8
Pillow==10.2.0
```

# residentes_ejemplo.txt
```
María López|201
Juan Pérez|102
Ana García
Carlos Ramírez|305
Luisa Fernández
Roberto Díaz|110
