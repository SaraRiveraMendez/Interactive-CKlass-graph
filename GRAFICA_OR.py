# =============================
# LIBRARIES
# =============================
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
# import gdown

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

ventas_group = ventas.groupby("Sem_ISO")["Cantidad"].sum().reset_index()
negados_group = negados.groupby("Sem_ISO")["Estado"].sum().reset_index()

df_merge = pd.merge(ventas_group, negados_group,
                    on="Sem_ISO", how="outer",
                    suffixes=("_Ventas", "_Negados")).fillna(0)

# =============================
# KPIs
# =============================

total_ventas = df_merge["Cantidad_Ventas"].sum()
total_negados = df_merge["Cantidad_Negados"].sum()

fill_rate = 1 - (total_negados / (total_ventas + total_negados)) if (total_ventas + total_negados) > 0 else 0

max_quiebre_semana = df_merge.loc[
    df_merge["Cantidad_Negados"].idxmax(), "Sem_ISO"
]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Ventas Totales", f"{int(total_ventas):,}")
col2.metric("Negados Totales", f"{int(total_negados):,}")
col3.metric("Fill Rate", f"{fill_rate:.2%}")
col4.metric("Semana Mayor Quiebre", int(max_quiebre_semana))

# =============================
# MAIN EXECUTIVE GRAPH
# =============================

fig = go.Figure()

# Ventas - gris claro
fig.add_trace(go.Scatter(
    x=df_merge["Sem_ISO"],
    y=df_merge["Cantidad_Ventas"],
    mode='lines',
    name='Ventas',
    line=dict(color="#B0B0B0", width=4)
))

# Negados - rojo con área
fig.add_trace(go.Scatter(
    x=df_merge["Sem_ISO"],
    y=df_merge["Cantidad_Negados"],
    mode='lines',
    name='Negados',
    line=dict(color="#C00000", width=3),
    fill='tozeroy',
    fillcolor='rgba(192,0,0,0.2)'
))

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font_color="black",
    title="Fluctuación Histórica: Ventas vs Demanda No Satisfecha",
    xaxis_title="Semana ISO",
    yaxis_title="Cantidad",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)
