# =============================
# LIBRARIES
# =============================
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Executive Dashboard", layout="wide")

st.title("Executive Sales Dashboard")
st.markdown("Análisis histórico de desempeño comercial")

# =============================
# DATA
# =============================

@st.cache_data
def load_data():
    df_ventas = pd.read_csv("data/ventas_light.csv")
    df_negados = pd.read_csv("data/negados_light.csv")
    return df_ventas, df_negados

df_ventas, df_negados = load_data()

# =============================
# SIDEBAR FILTERS
# =============================

st.sidebar.header("Filtros")

estaciones = sorted(df_ventas["estacion"].dropna().unique())
productos = sorted(df_ventas["ProductoID"].dropna().unique())

estacion_select = st.sidebar.selectbox("Estación", estaciones)
producto_select = st.sidebar.selectbox("Producto", productos)

# =============================
# FILTER DATA
# =============================

ventas = df_ventas[
    (df_ventas["estacion"] == estacion_select) &
    (df_ventas["ProductoID"] == producto_select)
]

negados = df_negados[
    (df_negados["estacion"] == estacion_select) &
    (df_negados["ProductoID"] == producto_select)
]

# =============================
# AGRUPACIONES
# =============================

# Ventas por semana
ventas_group = (
    ventas.groupby("Sem_ISO")["Cantidad"]
    .sum()
    .reset_index()
    .rename(columns={"Cantidad": "Cantidad_Ventas"})
)

# Conteo de eventos negados por semana
negados_group = (
    negados.groupby("Sem_ISO")
    .size()
    .reset_index(name="Eventos_Negados")
)

# =============================
# KPIs
# =============================

total_ventas = ventas_group["Cantidad_Ventas"].sum()
total_eventos_negados = negados_group["Eventos_Negados"].sum()

col1, col2 = st.columns(2)

col1.metric("Ventas Totales", f"{int(total_ventas):,}")
col2.metric("Eventos de Quiebre", f"{int(total_eventos_negados):,}")

# =============================
# GRAFICA 1 — VENTAS
# =============================

fig_ventas = go.Figure()

fig_ventas.add_trace(go.Scatter(
    x=ventas_group["Sem_ISO"],
    y=ventas_group["Cantidad_Ventas"],
    mode='lines',
    name='Ventas',
    line=dict(color="#B0B0B0", width=4)
))

fig_ventas.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    title="Ventas por Semana",
    xaxis_title="Semana ISO",
    yaxis_title="Cantidad",
    hovermode="x unified"
)

st.plotly_chart(fig_ventas, use_container_width=True)

# =============================
# GRAFICA 2 — EVENTOS NEGADOS
# =============================

fig_negados = go.Figure()

fig_negados.add_trace(go.Bar(
    x=negados_group["Sem_ISO"],
    y=negados_group["Eventos_Negados"],
    name='Eventos Negados'
))

fig_negados.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    title="Eventos de Demanda No Satisfecha por Semana",
    xaxis_title="Semana ISO",
    yaxis_title="Número de Eventos"
)

st.plotly_chart(fig_negados, use_container_width=True)
