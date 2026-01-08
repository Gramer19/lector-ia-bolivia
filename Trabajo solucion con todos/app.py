import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import re
import pandas as pd

# Configuración visual de la página
st.set_page_config(page_title="Extractor de Contactos Bolivia", page_icon="🇧🇴", layout="centered")

st.title("🇧🇴 Extractor de Datos IA")
st.markdown("""
Sube fotos de tarjetas, listas o formularios para extraer **Nombres** y **Celulares de Bolivia**.
""")

# Función para cargar la IA (se guarda en caché para que sea rápida)
@st.cache_resource
def load_reader():
    # 'es' para español
    return easyocr.Reader(['es'], gpu=False) 

reader = load_reader()

# Subida de archivos (permite varios a la vez)
uploaded_files = st.file_uploader("Selecciona imágenes...", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    all_data = []

    for uploaded_file in uploaded_files:
        # Procesar imagen
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        
        with st.spinner(f'Analizando {uploaded_file.name}...'):
            # La IA lee la imagen
            results = reader.readtext(img_array)
        
        # Unimos todo el texto detectado para aplicar los filtros
        full_text = " ".join([res[1] for res in results])
        
        # --- LÓGICA DE FILTRADO PARA BOLIVIA ---
        # Detecta: +591 seguido de 8 dígitos O números de 8 dígitos que empiezan con 6 o 7
        patron_bolivia = r'(\+591\s?[6-7]\d{7}|[6-7]\d{7})'
        telefonos = re.findall(patron_bolivia, full_text)
        
        # Limpieza de teléfonos (quitar espacios)
        telefonos = list(set([t.replace(" ", "") for t in telefonos])) 
        
        # Filtrado de posibles nombres (Texto largo sin números)
        nombres = [res[1] for res in results if not any(char.isdigit() for char in res[1]) and len(res[1]) > 4]

        # Guardar resultados
        for tel in telefonos:
            all_data.append({"Archivo": uploaded_file.name, "Dato": tel, "Tipo": "Teléfono"})
        
        for nom in nombres[:3]: # Limitamos a los 3 más probables por imagen
            all_data.append({"Archivo": uploaded_file.name, "Dato": nom, "Tipo": "Posible Nombre"})

    # Mostrar resultados si se encontró algo
    if all_data:
        df = pd.DataFrame(all_data)
        
        st.success("¡Extracción completada!")
        st.subheader("📊 Datos Encontrados")
        st.dataframe(df, use_container_width=True)

        # Botón para descargar a Excel (CSV)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar lista para Excel",
            data=csv,
            file_name="contactos_bolivia.csv",
            mime="text/csv",
        )
    else:
        st.warning("No se detectaron números que coincidan con el formato de Bolivia.")

st.divider()
st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")