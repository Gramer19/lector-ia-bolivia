import streamlit as st
import pandas as pd
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="IA Lector de Contactos", layout="centered")

st.title("📸 Extractor de Contactos IA")
st.write("Sube una o varias capturas y descarga los datos en Excel.")

# 1. Selector de archivos (ahora acepta múltiples)
uploaded_files = st.file_uploader(
    "Selecciona tus capturas de pantalla", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    lista_contactos = []  # Aquí se guardará todo

    for file in uploaded_files:
        st.info(f"Procesando: {file.name}")
        
        # --- AQUÍ VA TU LÓGICA DE GEMINI/IA ---
        # datos = procesar_imagen_con_ia(file)
        # lista_contactos.extend(datos)
        
        # Ejemplo temporal para que veas cómo se vería:
        lista_contactos.append({"Nombre": "Ejemplo IA", "Teléfono": "123456789", "Rol": "Admin"})

    # 2. Creamos la tabla (DataFrame)
    df = pd.DataFrame(lista_contactos)
    st.write("### Datos extraídos:")
    st.dataframe(df)

    # 3. Función mágica para crear el archivo Excel
    def crear_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Contactos')
        return output.getvalue()

    # 4. Botón de Descarga
    excel_archivo = crear_excel(df)
    st.download_button(
        label="📥 Descargar lista completa en Excel",
        data=excel_archivo,
        file_name="mis_contactos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.divider()
st.caption("Esta versión procesa todo en memoria, nada se guarda en la nube.")
st.divider()

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")




