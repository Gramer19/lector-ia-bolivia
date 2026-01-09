import streamlit as st
import pandas as pd
import easyocr
from PIL import Image
import numpy as np
from io import BytesIO

# Configuración inicial
st.set_page_config(page_title="Lector de Contactos Pro", layout="centered")

# Cargamos el lector de OCR (esto puede tardar un poco la primera vez)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['es'])

reader = load_reader()

st.title("📸 Extractor de Contactos Múltiple")
st.write("Sube tus capturas y descarga un solo Excel con todos los datos.")

# 1. Subida múltiple de archivos
uploaded_files = st.file_uploader(
    "Selecciona una o varias imágenes", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    lista_total = []
    
    for file in uploaded_files:
        with st.expander(f"👁️ Ver imagen: {file.name}"):
            image = Image.open(file)
            st.image(image, use_container_width=True)
            
            # Convertir imagen para EasyOCR
            img_np = np.array(image)
            
            # Leer texto
            with st.spinner(f"Leyendo {file.name}..."):
                resultados = reader.readtext(img_np, detail=0)
                
                # Lógica simple para organizar los datos leídos
                # Aquí podrías mejorar cómo separas Nombre y Teléfono
                texto_unido = " ".join(resultados)
                lista_total.append({
                    "Archivo": file.name,
                    "Contenido Extraído": texto_unido
                })

    # 2. Mostrar Tabla
    df = pd.DataFrame(lista_total)
    st.write("### Vista previa de datos:")
    st.dataframe(df, use_container_width=True)

    # 3. Función para descargar Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Contactos')
        return output.getvalue()

    if not df.empty:
        excel_data = to_excel(df)
        st.download_button(
            label="📥 Descargar todo en un Excel",
            data=excel_data,
            file_name="contactos_ia.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.divider()
st.info("💡 Consejo: Asegúrate de que las fotos tengan buena luz para que la IA lea mejor los números.")

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")





