import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import re
import pandas as pd
from io import BytesIO

# Configuración visual
st.set_page_config(page_title="Extractor Bolivia", page_icon="🇧🇴", layout="centered")

st.title("🇧🇴 Extractor de Contactos")

# Cargar IA (Se mantiene igual)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['es'], gpu=False) 

reader = load_reader()

# CAMBIO: accept_multiple_files=True para subir muchas fotos
uploaded_files = st.file_uploader("Selecciona imágenes...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    all_rows = []

    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        img_array = np.array(image.convert('RGB'))
        
        with st.spinner(f'Analizando {uploaded_file.name}...'):
            results = reader.readtext(img_array, detail=0)
        
        full_text = " ".join(results)
        
        # --- LÓGICA DE COLUMNAS A, B, C ---
        nombre = "Sin nombre"
        telefono = "No encontrado"
        rol = "Miembro"

        # Buscar Teléfono (Columna B)
        patron_bolivia = r'(\+591\s?[6-7]\d{7}|[6-7]\d{7})'
        match_tel = re.search(patron_bolivia, full_text.replace(" ", ""))
        if match_tel:
            telefono = match_tel.group()

        # Buscar Rol (Columna C) y Nombre (Columna A)
        for t in results:
            t_clean = t.strip()
            if "admin" in t_clean.lower():
                rol = "Administrador"
            elif len(t_clean) > 4 and not any(char.isdigit() for char in t_clean) and nombre == "Sin nombre":
                nombre = t_clean

        # Guardar en fila (Lado a lado)
        all_rows.append({"Nombre": nombre, "Teléfono": telefono, "Rol": rol})

    # Mostrar Tabla y Botón de Excel
    if all_rows:
        df = pd.DataFrame(all_rows)
        st.table(df) # Esto muestra las 3 columnas lado a lado

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Contactos')
        
        st.download_button(
            label="📥 Descargar Excel con todo",
            data=output.getvalue(),
            file_name="contactos_bolivia.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )












