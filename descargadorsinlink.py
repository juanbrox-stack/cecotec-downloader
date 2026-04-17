import streamlit as st
import pandas as pd
import requests
import io

# 1. Configuración visual de la aplicación
st.set_page_config(page_title="Cecotec Feed Downloader", page_icon="⚡", layout="centered")

st.title("📦 Cecotec Feed Downloader")
st.markdown("""
Esta herramienta descarga los catálogos de productos (feeds) de los diferentes países, 
limpia los errores de formato y genera archivos Excel listos para usar.
""")

# 2. Diccionario con las URLs de los feeds
FEEDS = {
    "España (ES)": "https://cecotec.es/api/v3/doofinder/feed/?lang=es",
    "Francia (FR)": "https://storececotec.fr/api/v3/doofinder/feed/?lang=fr",
    "Italia (IT)": "https://content.storececotec.it/api/v3/doofinder/feed/?lang=it",
    "Alemania (DE)": "https://storececotec.de/api/v3/doofinder/feed/?lang=de",
    "Portugal (PT)": "https://cecotec.pt/api/v3/doofinder/feed/?lang=pt"
}

def procesar_feed(nombre, url):
    """Descarga el contenido y lo convierte a DataFrame ignorando líneas corruptas"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Lectura robusta: separador |, ignora líneas con errores (como las de FR/DE)
        df = pd.read_csv(
            io.StringIO(response.text), 
            sep='|', 
            engine='python',
            on_bad_lines='skip', 
            quoting=3,
            encoding='utf-8'
        )
        return df
    except Exception as e:
        st.error(f"❌ Error al procesar {nombre}: {e}")
        return None

def convertir_a_excel(df):
    """Convierte el DataFrame a un objeto Excel en memoria"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# 3. Interfaz de usuario
opcion = st.selectbox("Selecciona el destino:", ["--- Seleccionar Todo ---"] + list(FEEDS.keys()))

if st.button("🚀 Iniciar Procesamiento"):
    if opcion == "--- Seleccionar Todo ---":
        progreso = st.progress(0)
        paises = list(FEEDS.items())
        
        for i, (nombre, url) in enumerate(paises):
            with st.status(f"Procesando {nombre}...", expanded=False):
                df_resultado = procesar_feed(nombre, url)
                if df_resultado is not None:
                    excel_bin = convertir_a_excel(df_resultado)
                    st.download_button(
                        label=f"⬇️ Descargar Excel {nombre}",
                        data=excel_bin,
                        file_name=f"feed_{nombre.split(' ')[0]}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"btn_{nombre}"
                    )
            # Actualizar barra de progreso
            progreso.progress((i + 1) / len(paises))
        st.success("✅ ¡Todos los países procesados!")
        
    else:
        with st.spinner(f"Preparando datos de {opcion}..."):
            df_resultado = procesar_feed(opcion, FEEDS[opcion])
            if df_resultado is not None:
                excel_bin = convertir_a_excel(df_resultado)
                st.success(f"¡Listo! El archivo de {opcion} se ha generado correctamente.")
                st.download_button(
                    label=f"⬇️ Descargar Excel {opcion}",
                    data=excel_bin,
                    file_name=f"feed_{opcion.split(' ')[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )