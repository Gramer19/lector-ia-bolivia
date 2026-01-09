import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
from io import BytesIO
import re

st.set_page_config(layout="wide")
st.title("Extractor de Contactos (Excel)")

# Subida múltiple
files = st.file_uploader("Sube tus imágenes", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if files:
    datos = []
    for f in files:
        img = Image.open(f)
        # Extraer texto de forma ligera
        texto_sucio = pytesseract.image_to_string(img, lang='spa')
        lineas = texto_sucio.split('\n')
        
        nombre, telefono, rol = "Sin nombre", "", "Miembro"
        
        for l in lineas:
            t = l.strip()
            if not t: continue
            
            # B - Teléfono
            if re.search(r'\d{7,}', t):
                telefono = t
            # C - Rol
            elif "admin" in t.lower():
                rol = "Administrador"
            # A - Nombre
            elif len(t) > 2 and not any(c.isdigit() for c in t) and nombre == "Sin nombre":
                nombre = t
        
        datos.append({"Nombre": nombre, "Teléfono": telefono, "Rol": rol})

    # Mostrar Tabla y Botón
    df = pd.DataFrame(datos)
    st.table(df)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button("Descargar Excel", output.getvalue(), "contactos.xlsx")

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")










