import streamlit as st
import easyocr
import pandas as pd
from PIL import Image
import numpy as np
import io
import re

st.set_page_config(page_title="Lector IA Bolivia", page_icon="🇧🇴")
st.title("Lector Inteligente Solucion Con Todos")
st.write("Detecta: Nombre (A), Teléfono (B) y Rol (C)")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['es', 'en'], gpu=False)

reader = load_reader()

uploaded_file = st.file_uploader("Sube la captura de pantalla...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Imagen subida', use_container_width=True)
    st.write("🔍 Analizando y organizando datos...")
    
    img_array = np.array(image)
    results = reader.readtext(img_array, detail=0)
    
    if results:
        # Listas para organizar las columnas
        nombres = []
        telefonos = []
        roles = []

        # Lógica para separar los datos
        for texto in results:
            texto_limpio = texto.strip()
            
            # 1. Buscar Teléfonos (si tiene muchos números)
            if sum(c.isdigit() for c in texto_limpio) >= 7:
                telefonos.append(texto_limpio)
            # 2. Buscar Rol (Admin o Miembro)
            elif "admin" in texto_limpio.lower():
                roles.append("Administrador")
            elif "miembro" in texto_limpio.lower():
                roles.append("Miembro")
            # 3. Lo demás es Nombre
            else:
                if len(texto_limpio) > 2: # Evitar basuritas de texto
                    nombres.append(texto_limpio)

        # Ajustar las listas para que tengan el mismo largo y entren en el Excel
        max_len = max(len(nombres), len(telefonos), len(roles))
        nombres += [""] * (max_len - len(nombres))
        telefonos += [""] * (max_len - len(telefonos))
        roles += [""] * (max_len - len(roles))

        # Crear el DataFrame con las 3 columnas que pediste
        df = pd.DataFrame({
            "Nombre": nombres,
            "Teléfono": telefonos,
            "Rol": roles
        })
        
        st.success("¡Datos organizados con éxito!")
        st.table(df)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Contactos')
        
        st.download_button(
            label="📥 Descargar Excel Organizado (A, B, C)",
            data=output.getvalue(),
            file_name="contactos_organizados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No se encontró texto.")

st.divider()

st.info("Nota: La precisión depende de la calidad de la foto y la iluminación.")


