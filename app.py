import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO
import re

# 1. Configuración y Lector
st.set_page_config(layout="wide")
reader = easyocr.Reader(['es'], gpu=False)

st.title("Extractor de Contactos")

# 2. Subida de archivos (Múltiple)
files = st.file_uploader("Sube tus fotos", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if files:
    datos = []
    for f in files:
        # Procesar imagen
        img = np.array(Image.open(f).convert('RGB'))
        texto = reader.readtext(img, detail=0)
        
        # Columnas A, B y C
        nombre, telefono, rol = "Sin nombre", "", "Miembro"
        
        for t in texto:
            # Buscar Teléfono (Si tiene números largos)
            if re.search(r'\d{7,}', t):
                telefono = t
            # Buscar Rol
            elif "admin" in t.lower():
                rol = "Administrador"
            # Buscar Nombre (Cualquier otro texto que no sea número)
            elif len(t) > 2 and not any(c.isdigit() for c in t) and nombre == "Sin nombre":
                nombre = t
        
        datos.append({"Nombre": nombre, "Teléfono": telefono, "Rol": rol})

    # 3. Mostrar Tabla
    df = pd.DataFrame(datos)
    st.table(df)

    # 4. Descargar Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="Descargar Excel",
        data=output.getvalue(),
        file_name="contactos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")









