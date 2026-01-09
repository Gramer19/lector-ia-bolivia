import streamlit as st
import pandas as pd
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO
import re

# Cargamos lo que ya tienes
st.set_page_config(layout="wide")
reader = easyocr.Reader(['es'], gpu=False)

st.title("Extractor de Contactos")

files = st.file_uploader("Sube tus imágenes", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if files:
    datos_lista = []
    
    for f in files:
        # 1. Leer imagen
        img = np.array(Image.open(f).convert('RGB'))
        texto_detectado = reader.readtext(img, detail=0)
        
        # 2. Variables para Columnas A, B y C
        nombre, telefono, rol = "Sin nombre", "No encontrado", "Miembro"
        
        for t in texto_detectado:
            t_limpio = t.strip()
            # Buscar Teléfono (Columna B)
            if re.search(r'\d{7,}', t_limpio.replace(" ", "")):
                telefono = t_limpio
            # Buscar Rol (Columna C)
            elif "admin" in t_limpio.lower():
                rol = "Administrador"
            # Buscar Nombre (Columna A)
            elif len(t_limpio) > 3 and not any(c.isdigit() for c in t_limpio) and nombre == "Sin nombre":
                nombre = t_limpio
        
        # 3. Guardar lado a lado
        datos_lista.append({"Nombre": nombre, "Teléfono": telefono, "Rol": rol})

    # Mostrar tabla y descargar
    df = pd.DataFrame(datos_lista)
    st.table(df)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button("Descargar Excel", output.getvalue(), "contactos.xlsx")

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")











