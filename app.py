import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
import numpy as np
from io import BytesIO
import re

st.set_page_config(page_title="Extractor de Contactos", layout="wide")

@st.cache_resource
def load_reader():
    # Cargamos el modelo en español
    return easyocr.Reader(['es'])

reader = load_reader()

st.title("📸 Extractor de Contactos a Excel (Columnas A, B, C)")
st.write("Sube tus capturas. Los datos se organizarán lado a lado en el Excel.")

uploaded_files = st.file_uploader(
    "Selecciona tus imágenes", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    datos_para_excel = []
    
    for file in uploaded_files:
        image = Image.open(file)
        img_np = np.array(image)
        
        with st.spinner(f"Procesando {file.name}..."):
            # Obtenemos el texto con su posición en la imagen
            # Esto ayuda a separar mejor los bloques de texto
            resultados = reader.readtext(img_np)
            
            # Variables temporales para cada fila del Excel
            nombre = "Sin nombre"
            telefono = ""
            rol = "Miembro"

            for (bbox, texto, prob) in resultados:
                texto_limpio = texto.strip()
                
                # 1. Detectar Teléfono (Si tiene + o muchos números seguidos)
                if re.search(r'\+?\d[\d\s-]{7,}', texto_limpio):
                    telefono = texto_limpio
                
                # 2. Detectar Rol (Si dice Admin)
                elif "admin" in texto_limpio.lower():
                    rol = "Administrador"
                
                # 3. Detectar Nombre (Si no es número ni admin, y tiene letras)
                elif len(texto_limpio) > 2 and not any(char.isdigit() for char in texto_limpio):
                    nombre = texto_limpio

            # Solo guardamos si al menos encontramos un nombre o un teléfono
            if nombre != "Sin nombre" or telefono != "":
                datos_para_excel.append({
                    "Nombre (Usuario)": nombre,
                    "Teléfono": telefono,
                    "Rol (Rango)": rol
                })

    # Creamos el DataFrame con la estructura exacta que pides
    df = pd.DataFrame(datos_para_excel)

    if not df.empty:
        st.write("### Vista previa del orden (Columnas A, B, C):")
        st.dataframe(df, use_container_width=True)

        # Crear el archivo Excel profesional
        def conversion_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # El DataFrame se escribe empezando en la celda A1 por defecto
                df.to_excel(writer, index=False, sheet_name='Lista de Contactos')
                
                workbook = writer.book
                worksheet = writer.sheets['Lista de Contactos']
                
                # Formato para que los encabezados se vean bien
                header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 25) # Ancho de columna

            return output.getvalue()

        boton_excel = conversion_excel(df)
        
        st.download_button(
            label="📥 DESCARGAR EXCEL ORGANIZADO",
            data=boton_excel,
            file_name="contactos_limpios.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No se detectaron datos claros en las imágenes.")

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")







