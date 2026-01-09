import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO
import re

@st.cache_resource
def load_reader():
    return easyocr.Reader(['es'], gpu=False)

reader = load_reader()

st.title("Extractor de Contactos Múltiple")

# CAMBIO 1: Agregamos "accept_multiple_files=True"
uploaded_files = st.file_uploader("Sube tus imágenes...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    datos_acumulados = [] # Aquí guardaremos todas las filas
    
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        img_np = np.array(image.convert('RGB'))
        
        # Procesar cada imagen con la IA
        result = reader.readtext(img_np, detail=0)
        
        nombre, telefono, rol = "Sin nombre", "No encontrado", "Miembro"
        
        for texto in result:
            t = texto.strip()
            if re.search(r'\d{7,}', t.replace(" ", "")):
                telefono = t
            elif "admin" in t.lower():
                rol = "Administrador"
            elif len(t) > 3 and not any(c.isdigit() for c in t) and nombre == "Sin nombre":
                nombre = t
        
        # CAMBIO 2: Vamos sumando cada contacto a la lista
        datos_acumulados.append({"Nombre": nombre, "Teléfono": telefono, "Rol": rol})
    
    # Crear la tabla final con todos los datos juntos
    df = pd.DataFrame(datos_acumulados)
    st.write("### Lista de contactos extraídos:")
    st.table(df) # Se verá la Columna A, B y C lado a lado

    # Generar el Excel con todo
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Contactos')
    
    st.download_button(
        label="📥 Descargar Excel con todos los contactos",
        data=output.getvalue(),
        file_name="contactos_totales.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")












