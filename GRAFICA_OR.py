# =============================
# LIBRARIES
# =============================
import pandas as pd
import streamlit as st
import plotly.express as px
import gdown

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Dashboard Ventas y Negados", layout="wide")

st.title("Dashboard Histórico")
st.markdown("Análisis interactivo de Ventas y Demanda No Satisfecha")

# =============================
# GOOGLE DRIVE LINKS (Direct Download)
# =============================

negados_url = "https://drive.google.com/uc?id=1Fp_yWwj6NfA1ySeM59x2S-UISMrPlGDA"
ventas_url = "https://drive.google.com/uc?id=18KA1UDW0WE22n-3VAoaDmFVftEepS826"

@st.cache_data
def load_data(url, filename):
    gdown.download(url, filename, quiet=False)
    return pd.read_csv(filename)

df_negados = load_data(negados_url, "negados.csv")
df_ventas = load_data(ventas_url, "ventas.csv")

# =============================
# SIDEBAR FILTERS
# =============================

st.sidebar.header("Filtros")

estaciones = sorted(df_ventas["estacion"].dropna().unique())
productos = sorted(df_ventas["ProductoID"].dropna().unique())

estacion_select = st.sidebar.selectbox("Selecciona Estación", estaciones)
producto_select = st.sidebar.selectbox("Selecciona Producto", productos)

# =============================
# FILTER DATA
# =============================

ventas_filtrado = df_ventas[
    (df_ventas["estacion"] == estacion_select) &
    (df_ventas["ProductoID"] == producto_select)
]

negados_filtrado = df_negados[
    (df_negados["estacion"] == estacion_select) &
    (df_negados["ProductoID"] == producto_select)
]

# Agrupar por semana
ventas_group = ventas_filtrado.groupby("Sem_ISO")["Cantidad"].sum().reset_index()
negados_group = negados_filtrado.groupby("Sem_ISO")["Cantidad"].sum().reset_index()

# =============================
# COLOR PALETTE
# =============================

color_ventas = "#B0B0B0"   # gris claro
color_negados = "#C00000"  # rojo corporativo

# =============================
# GRÁFICA VENTAS
# =============================

fig_ventas = px.line(
    ventas_group,
    x="Sem_ISO",
    y="Cantidad",
    title="Ventas Históricas",
)

fig_ventas.update_traces(line_color=color_ventas)
fig_ventas.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font_color="black"
)

# =============================
# GRÁFICA NEGADOS
# =============================

fig_negados = px.line(
    negados_group,
    x="Sem_ISO",
    y="Cantidad",
    title="Demanda No Satisfecha (Negados)",
)

fig_negados.update_traces(line_color=color_negados)
fig_negados.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font_color="black"
)

# =============================
# DISPLAY SIDE BY SIDE
# =============================

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_ventas, use_container_width=True)

with col2:
    st.plotly_chart(fig_negados, use_container_width=True)
