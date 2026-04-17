import streamlit as st
import pandas as pd
import requests
import io

# Configuración de página
st.set_page_config(page_title="Cecotec Feed Downloader", page_icon="⚡")

st.title("📦 Cecotec Feed Downloader Pro")
st.markdown("Generación de archivos Excel con enlaces directos optimizados.")

# Origen de datos
FEEDS = {
    "España (ES)": "https://cecotec.es/api/v3/doofinder/feed/?lang=es",
    "Francia (FR)": "https://storececotec.fr/api/v3/doofinder/feed/?lang=fr",
    "Italia (IT)": "https://content.storececotec.it/api/v3/doofinder/feed/?lang=it",
    "Alemania (DE)": "https://storececotec.de/api/v3/doofinder/feed/?lang=de",
    "Portugal (PT)": "https://cecotec.pt/api/v3/doofinder/feed/?lang=pt"
}

# Dominios base corregidos
DOMINIOS = {
    "España (ES)": "https://cecotec.es",
    "Francia (FR)": "https://www.storececotec.fr",
    "Italia (IT)": "https://storececotec.it",
    "Alemania (DE)": "https://storececotec.de",
    "Portugal (PT)": "https://cecotec.pt/pt"
}

def procesar_feed(nombre, url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        df = pd.read_csv(
            io.StringIO(response.text), 
            sep='|', 
            engine='python',
            on_bad_lines='skip', 
            quoting=3,
            encoding='utf-8'
        )

        if 'link' in df.columns:
            dominio_base = DOMINIOS[nombre]
            # Limpieza y concatenación
            df['link'] = df['link'].astype(str).str.strip().str.lstrip('/')
            df['link'] = dominio_base + '/' + df['link']
            
        return df
    except Exception as e:
        st.error(f"❌ Error en {nombre}: {e}")
        return None

def convertir_a_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# Interfaz
opcion = st.selectbox("Selecciona el país:", ["--- Seleccionar Todo ---"] + list(FEEDS.keys()))

if st.button("🚀 Iniciar Descarga"):
    if opcion == "--- Seleccionar Todo ---":
        progreso = st.progress(0)
        paises = list(FEEDS.items())
        
        for i, (nombre, url) in enumerate(paises):
            with st.status(f"Procesando {nombre}...", expanded=False):
                df_res = procesar_feed(nombre, url)
                if df_res is not None:
                    excel_bin = convertir_a_excel(df_res)
                    st.download_button(
                        label=f"⬇️ Descargar {nombre}",
                        data=excel_bin,
                        file_name=f"feed_{nombre.split(' ')[0]}.xlsx",
                        key=f"btn_{nombre}"
                    )
            progreso.progress((i + 1) / len(paises))
        st.success("✅ ¡Proceso completado!")
        
    else:
        with st.spinner(f"Procesando {opcion}..."):
            df_res = procesar_feed(opcion, FEEDS[opcion])
            if df_res is not None:
                excel_bin = convertir_a_excel(df_res)
                st.download_button(
                    label=f"⬇️ Descargar Excel {opcion}",
                    data=excel_bin,
                    file_name=f"feed_{opcion.split(' ')[0]}.xlsx"
                )