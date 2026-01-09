import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
import numpy as np
from io import BytesIO
import re

# 1. Configuración de página al principio
st.set_page_config(page_title="Extractor de Contactos", layout="wide")

# 2. Cargar el lector de forma segura
@st.cache_resource
def load_reader():
    # Usamos CPU para que no dé error en Streamlit Cloud
    return easyocr.Reader(['es'], gpu=False)

try:
    reader = load_reader()
except Exception as e:
    st.error("Error cargando el motor de lectura. Por favor, refresca la página.")

st.title("📸 Extractor de Contactos a Excel")
st.write("Sube tus capturas y las organizaremos en columnas A, B y C.")

# 3. Subida de archivos
uploaded_files = st.file_uploader(
    "Selecciona tus imágenes", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    datos_para_excel = []
    
    for file in uploaded_files:
        try:
            image = Image.open(file).convert('RGB')
            img_np = np.array(image)
            
            with st.spinner(f"Leyendo {file.name}..."):
                resultados = reader.readtext(img_np, detail=0)
                
                nombre, telefono, rol = "Sin nombre", "", "Miembro"

                for texto in resultados:
                    t = texto.strip()
                    # Buscar Teléfono
                    if re.search(r'\+?\d[\d\s-]{7,}', t):
                        telefono = t
                    # Buscar Rol
                    elif "admin" in t.lower():
                        rol = "Administrador"
                    # Buscar Nombre (si no es número ni admin)
                    elif len(t) > 2 and not any(char.isdigit() for char in t) and nombre == "Sin nombre":
                        nombre = t

                if nombre != "Sin nombre" or telefono != "":
                    datos_para_excel.append({"Nombre": nombre, "Teléfono": telefono, "Rol": rol})
        except Exception as e:
            st.error(f"No se pudo leer la imagen {file.name}")

    if datos_para_excel:
        df = pd.DataFrame(datos_para_excel)
        st.write("### Vista previa:")
        st.dataframe(df, use_container_width=True)

        # Crear Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Contactos')
        
        st.download_button(
            label="📥 DESCARGAR EXCEL",
            data=output.getvalue(),
            file_name="contactos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")








