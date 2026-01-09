import streamlit as st
import easyocr
import pandas as pd
from PIL import Image
import numpy as np
import io

# Configuración de la página
st.set_page_config(page_title="Lector IA Bolivia", page_icon="🇧🇴")
st.title("🇧🇴 Lector de Datos - Bolivia")
st.write("Sube una imagen y los datos se separarán en filas para tu Excel.")

# Cache para que la IA no se descargue cada vez
@st.cache_resource
def load_reader():
    # 'es' para español, 'en' para inglés
    return easyocr.Reader(['es', 'en'], gpu=False)

reader = load_reader()

uploaded_file = st.file_uploader("Elige una imagen...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Mostrar imagen
    image = Image.open(uploaded_file)
    st.image(image, caption='Imagen subida', use_container_width=True)
    
    st.write("🌀 Procesando con IA...")
    
    # Convertir imagen para EasyOCR
    img_array = np.array(image)
    
    # Leer texto
    results = reader.readtext(img_array, detail=0) # detail=0 devuelve solo el texto limpio
    
    if results:
        st.success("¡Datos extraídos!")
        
        # --- EL TRUCO PARA LAS CELDAS ---
        # Creamos el DataFrame. Cada elemento de la lista 'results' será una fila.
        df = pd.DataFrame(results, columns=["Información Detectada"])
        
        # Mostrar tabla en la web
        st.table(df)
        
        # Convertir a Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos')
        
        excel_data = output.getvalue()
        
        # Botón de descarga
        st.download_button(
            label="📥 Descargar Excel con celdas separadas",
            data=excel_data,
            file_name="datos_bolivia.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No se detectó ningún texto en la imagen.")

st.divider()

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")
