"""
Ejercicio 1: Comparador de distribuciones con multiples datasets
----------------------------------------------------------------
App de Streamlit que permite cargar dos archivos CSV simultaneamente
y comparar la distribucion de una variable numerica entre ambos
datasets usando histogramas superpuestos con transparencia.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# ----------------------------------------------------------------------
# Configuracion de la pagina
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Comparador de distribuciones",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Comparador de distribuciones entre datasets")
st.write(
    "Carga **dos archivos CSV** y compara la distribucion de una "
    "variable numerica entre ambos mediante histogramas superpuestos."
)


# ----------------------------------------------------------------------
# 1. Carga de archivos (accept_multiple_files=True)
# ----------------------------------------------------------------------
uploaded_files = st.file_uploader(
    "Sube exactamente dos archivos CSV",
    type=["csv"],
    accept_multiple_files=True,
    help="Selecciona dos archivos manteniendo Ctrl/Cmd o arrastralos juntos.",
)


# ----------------------------------------------------------------------
# 2. Validaciones del numero de archivos
# ----------------------------------------------------------------------
if not uploaded_files:
    st.info("⬆️ Esperando que subas dos archivos CSV para comenzar.")
    st.stop()

if len(uploaded_files) == 1:
    st.warning(
        "⚠️ Solo se ha subido **un archivo**. "
        "Esta app necesita dos CSVs para comparar distribuciones. "
        "Por favor, sube un segundo archivo."
    )
    # Mostramos un preview del unico archivo para que el usuario
    # confirme que cargo lo correcto mientras agrega el segundo.
    try:
        df_preview = pd.read_csv(uploaded_files[0])
        with st.expander(f"Vista previa de {uploaded_files[0].name}"):
            st.dataframe(df_preview.head())
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
    st.stop()

if len(uploaded_files) > 2:
    st.error(
        f"❌ Se subieron {len(uploaded_files)} archivos. "
        "Esta app solo admite **exactamente dos** CSVs."
    )
    st.stop()


# ----------------------------------------------------------------------
# 3. Lectura de los dos CSVs
# ----------------------------------------------------------------------
file_a, file_b = uploaded_files

try:
    df_a = pd.read_csv(file_a)
    df_b = pd.read_csv(file_b)
except Exception as e:
    st.error(f"Error al leer alguno de los archivos: {e}")
    st.stop()

name_a, name_b = file_a.name, file_b.name

# Mostrar previsualizaciones lado a lado
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Dataset A — `{name_a}`")
    st.write(f"Filas: **{len(df_a)}**, Columnas: **{df_a.shape[1]}**")
    st.dataframe(df_a.head())
with col2:
    st.subheader(f"Dataset B — `{name_b}`")
    st.write(f"Filas: **{len(df_b)}**, Columnas: **{df_b.shape[1]}**")
    st.dataframe(df_b.head())


# ----------------------------------------------------------------------
# 4. Columnas numericas comunes
# ----------------------------------------------------------------------
num_cols_a = set(df_a.select_dtypes(include="number").columns)
num_cols_b = set(df_b.select_dtypes(include="number").columns)
common_numeric = sorted(num_cols_a & num_cols_b)

if not common_numeric:
    st.error(
        "❌ Los dos datasets no comparten ninguna columna numerica. "
        "No es posible comparar distribuciones."
    )
    st.stop()

st.markdown("---")
st.subheader("🎯 Selecciona la variable a comparar")

variable = st.selectbox(
    "Columnas numericas comunes entre ambos datasets",
    options=common_numeric,
)

# Control extra para el numero de bins (mejora la UX)
bins = st.slider("Numero de bins del histograma", 5, 100, 30)


# ----------------------------------------------------------------------
# 5. Histogramas superpuestos con plotly.graph_objects
# ----------------------------------------------------------------------
serie_a = df_a[variable].dropna()
serie_b = df_b[variable].dropna()

fig = go.Figure()
fig.add_trace(
    go.Histogram(
        x=serie_a,
        name=name_a,
        opacity=0.6,
        nbinsx=bins,
        marker_color="#1f77b4",
    )
)
fig.add_trace(
    go.Histogram(
        x=serie_b,
        name=name_b,
        opacity=0.6,
        nbinsx=bins,
        marker_color="#ff7f0e",
    )
)

fig.update_layout(
    barmode="overlay",  # clave para superponer los dos histogramas
    title=f"Distribucion de '{variable}' en ambos datasets",
    xaxis_title=variable,
    yaxis_title="Frecuencia",
    legend_title="Dataset",
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)


# ----------------------------------------------------------------------
# 6. Tabla comparativa: media, mediana y desviacion estandar
# ----------------------------------------------------------------------
st.subheader("📋 Estadisticas comparativas")

stats = pd.DataFrame(
    {
        "Dataset": [name_a, name_b],
        "n": [len(serie_a), len(serie_b)],
        "Media": [serie_a.mean(), serie_b.mean()],
        "Mediana": [serie_a.median(), serie_b.median()],
        "Desv. estandar": [serie_a.std(), serie_b.std()],
    }
)

st.dataframe(
    stats.style.format(
        {
            "Media": "{:.4f}",
            "Mediana": "{:.4f}",
            "Desv. estandar": "{:.4f}",
        }
    ),
    use_container_width=True,
)

# Pequeno resumen interpretativo
diff_media = serie_a.mean() - serie_b.mean()
st.caption(
    f"Diferencia de medias (A − B): **{diff_media:.4f}** · "
    f"Razon de desviaciones (A / B): "
    f"**{(serie_a.std() / serie_b.std()):.4f}**"
    if serie_b.std() != 0
    else "Desviacion de B es 0; no se calcula la razon."
)
