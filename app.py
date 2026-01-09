import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import re
import pandas as pd
from io import BytesIO

# CONFIGURACIÓN PARA CELULARES
st.set_page_config(
    page_title="Extractor Bolivia", 
    page_icon="🇧🇴", 
    layout="centered",  # Esto hace que en el móvil no se vea todo apretado
    initial_sidebar_state="collapsed"
)

# Estilo para mejorar la vista en móviles
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #28a745; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇧🇴 Extractor de Contactos Solucion con Todos ")

# Cargar IA
@st.cache_resource
def load_reader():
    return easyocr.Reader(['es'], gpu=False) 

reader = load_reader()

# Botón para limpiar todo (Reset)
if st.button("🗑️ Limpiar y Nueva Lista"):
    st.cache_resource.clear()
    st.rerun()

# Subida múltiple
uploaded_files = st.file_uploader("📷 Sube o toma fotos", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    all_rows = []

    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        img_array = np.array(image.convert('RGB'))
        
        with st.spinner(f'Leyendo datos de la imagen...'):
            results = reader.readtext(img_array)
        
        nombre_actual = "Sin nombre"
        
        for (bbox, text, prob) in results:
            t_clean = text.strip()
            
            # Detectar Teléfono (Bolivia)
            if re.search(r'(\+591\s?[6-7]\d{7}|[6-7]\d{7})', t_clean.replace(" ", "")):
                telefono_encontrado = t_clean
                rol_encontrado = "Miembro"
                
                if "admin" in t_clean.lower():
                    rol_encontrado = "Administrador"

                # Guardar fila (A, B, C)
                all_rows.append({
                    "Nombre": nombre_actual,
                    "Teléfono": telefono_encontrado,
                    "Rol": rol_encontrado
                })
                nombre_actual = "Sin nombre"
            
            # Detectar Nombre
            elif len(t_clean) > 3 and not any(char.isdigit() for char in t_clean):
                if "admin" in t_clean.lower():
                    if all_rows: all_rows[-1]["Rol"] = "Administrador"
                else:
                    nombre_actual = t_clean

    if all_rows:
        df = pd.DataFrame(all_rows)
        st.success(f"✅ ¡{len(df)} contactos listos!")
        
        # Tabla scrolleable para celular
        st.dataframe(df, use_container_width=True)

        # Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Contactos')
        
        st.download_button(
            label="📥 DESCARGAR EXCEL",
            data=output.getvalue(),
            file_name="contactos_bolivia.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

st.divider()
st.caption("Usa la cámara de tu celular para escanear directamente.")










