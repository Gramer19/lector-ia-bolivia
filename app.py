import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import re
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Extractor Bolivia", page_icon="🇧🇴", layout="wide")
st.title("🇧🇴 Extractor de Contactos Completo")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['es'], gpu=False) 

reader = load_reader()

uploaded_files = st.file_uploader("Sube tus capturas", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    all_rows = []

    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        img_array = np.array(image.convert('RGB'))
        
        with st.spinner(f'Analizando {uploaded_file.name}...'):
            # Obtenemos los resultados con posición (para saber qué nombre va con qué número)
            results = reader.readtext(img_array)
        
        # Variables temporales para ir armando cada contacto
        nombre_actual = "Sin nombre"
        
        for (bbox, text, prob) in results:
            t_clean = text.strip()
            
            # 1. Si encontramos un TELÉFONO, asumimos que se completa un contacto
            # Buscamos formato de Bolivia (8 dígitos o +591)
            if re.search(r'(\+591\s?[6-7]\d{7}|[6-7]\d{7})', t_clean.replace(" ", "")):
                telefono_encontrado = t_clean
                
                # Buscamos si cerca decía "Admin"
                rol_encontrado = "Miembro"
                # (Lógica simple: si la palabra admin está en el bloque de texto)
                if "admin" in t_clean.lower():
                    rol_encontrado = "Administrador"

                # Guardamos este contacto y reseteamos para el siguiente en la misma foto
                all_rows.append({
                    "Nombre": nombre_actual,
                    "Teléfono": telefono_encontrado,
                    "Rol": rol_encontrado
                })
                nombre_actual = "Sin nombre" # Limpiamos para el siguiente
            
            # 2. Si es texto sin números, probablemente es el nombre del siguiente contacto
            elif len(t_clean) > 3 and not any(char.isdigit() for char in t_clean):
                if "admin" in t_clean.lower():
                    # Si la palabra admin viene sola, la marcamos para el último contacto
                    if all_rows: all_rows[-1]["Rol"] = "Administrador"
                else:
                    nombre_actual = t_clean

    if all_rows:
        df = pd.DataFrame(all_rows)
        st.subheader(f"📊 Se encontraron {len(df)} contactos en total")
        st.table(df) # Aquí verás la lista larga con todos los nombres y números

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Contactos')
        
        st.download_button(
            label="📥 Descargar Excel con TODOS los datos",
            data=output.getvalue(),
            file_name="contactos_completos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )









