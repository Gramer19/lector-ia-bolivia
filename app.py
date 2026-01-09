import streamlit as st
import easyocr
import pandas as pd
from PIL import Image
import numpy as np
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="IA a Google Sheets", page_icon="🇧🇴")
st.title("🇧🇴 Base de Datos en la Nube")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_resource
def load_reader():
    return easyocr.Reader(['es', 'en'], gpu=False)

reader = load_reader()

uploaded_file = st.file_uploader("Sube imagen para la base de datos...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    results = reader.readtext(img_array, detail=0)
    
    if results:
        nombres, telefonos, roles = [], [], []
        for texto in results:
            t = texto.strip()
            if sum(c.isdigit() for c in t) >= 7: telefonos.append(t)
            elif "admin" in t.lower(): roles.append("Administrador")
            elif "miembro" in t.lower(): roles.append("Miembro")
            else: nombres.append(t)
        
        max_len = max(len(nombres), len(telefonos), len(roles))
        df_nuevo = pd.DataFrame({
            "Nombre": nombres + [""]*(max_len-len(nombres)),
            "Teléfono": telefonos + [""]*(max_len-len(telefonos)),
            "Rol": roles + [""]*(max_len-len(roles))
        })

        st.write("Datos detectados:")
        st.dataframe(df_nuevo)

        if st.button("🚀 Guardar en Google Sheets Permanente"):
            try:
                # Leer datos actuales
                df_existente = conn.read()
                # Unir con los nuevos
                df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
                # Limpiar celdas vacías
                df_final = df_final.dropna(how='all')
                # Actualizar la nube
                conn.update(data=df_final)
                st.success("✅ ¡Guardado! Ya puedes cerrar esto y subir otra foto.")
            except Exception as e:
                st.error(f"Error al conectar: {e}")

st.divider()

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")



