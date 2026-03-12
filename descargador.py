import streamlit as st
import pandas as pd
import requests
import io

# Configuración de la página
st.set_page_config(page_title="Cecotec Feed Downloader", page_icon="⚡")

st.title("📦 Cecotec Feed Downloader")
st.markdown("Selecciona los países para descargar sus catálogos en formato Excel.")

# Diccionario de feeds
FEEDS = {
    "España (ES)": "https://cecotec.es/api/v3/doofinder/feed/?lang=es",
    "Francia (FR)": "https://storececotec.fr/api/v3/doofinder/feed/?lang=fr",
    "Italia (IT)": "https://content.storececotec.it/api/v3/doofinder/feed/?lang=it",
    "Alemania (DE)": "https://storececotec.de/api/v3/doofinder/feed/?lang=de",
    "Portugal (PT)": "https://cecotec.pt/api/v3/doofinder/feed/?lang=pt"
}

# Selector en la barra lateral
opcion = st.selectbox("¿Qué país deseas procesar?", ["Todos"] + list(FEEDS.keys()))

def procesar_feed(url):
    response = requests.get(url)
    response.raise_for_status()
    # Procesamos el CSV con separador |
    df = pd.read_csv(io.StringIO(response.text), sep='|', engine='python')
    return df

if st.button("Generar Archivo(s)"):
    try:
        if opcion == "Todos":
            for pais, url in FEEDS.items():
                df = procesar_feed(url)
                nombre_limpio = pais.split(' ')[0]
                
                # Botón de descarga para cada país
                excel_data = io.BytesIO()
                df.to_excel(excel_data, index=False)
                st.download_button(
                    label=f"⬇️ Descargar Excel {nombre_limpio}",
                    data=excel_data.getvalue(),
                    file_name=f"feed_{nombre_limpio}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            with st.spinner(f"Descargando datos de {opcion}..."):
                df = procesar_feed(FEEDS[opcion])
                nombre_limpio = opcion.split(' ')[0]
                
                # Convertir DF a Excel en memoria
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                
                st.success(f"¡Datos de {nombre_limpio} listos!")
                st.download_button(
                    label="⬇️ Descargar Archivo Excel",
                    data=output.getvalue(),
                    file_name=f"feed_{nombre_limpio}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"Error al conectar con el servidor: {e}")