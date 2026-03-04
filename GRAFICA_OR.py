# =============================
# LIBRARIES
# =============================
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Executive Dashboard | Cklass", layout="wide")

# =============================
# CSS PERSONALIZADO — CKLASS
# =============================
st.markdown(
    """
    <style>
        /* Fondo general */
        .stApp {
            background-color: #F5F5F5;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1A1A1A;
        }
        [data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] .stSelectbox label {
            color: #CCCCCC !important;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Header */
        .cklass-header {
            background: linear-gradient(90deg, #C8102E 0%, #A00D24 100%);
            padding: 1.5rem 2rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }
        .cklass-header h1 {
            color: white;
            margin: 0;
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }
        .cklass-header p {
            color: rgba(255,255,255,0.75);
            margin: 0.2rem 0 0 0;
            font-size: 0.9rem;
        }

        /* KPI Cards */
        .kpi-card {
            background: white;
            border-radius: 8px;
            padding: 1.2rem 1.5rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            border-left: 4px solid #C8102E;
        }
        .kpi-label {
            color: #888888;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }
        .kpi-value {
            color: #1A1A1A;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1;
        }
        .kpi-sub {
            color: #C8102E;
            font-size: 0.78rem;
            margin-top: 0.3rem;
        }

        /* Gráficas container */
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            margin-bottom: 1rem;
        }

        /* Ocultar elementos default de Streamlit */
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {padding-top: 1rem;}
    </style>
""",
    unsafe_allow_html=True,
)


# =============================
# DATA
# =============================
@st.cache_data
def load_data():
    df_ventas = pd.read_csv("data/ventas_light_final.csv")
    df_negados = pd.read_csv("data/negados_light_final.csv")
    return df_ventas, df_negados


df_ventas, df_negados = load_data()

# =============================
# HEADER
# =============================
st.markdown(
    """
    <div class="cklass-header">
        <h1>Executive Sales Dashboard</h1>
        <p>Análisis histórico de desempeño comercial</p>
    </div>
""",
    unsafe_allow_html=True,
)

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.markdown("## Filtros")
st.sidebar.markdown("---")

estaciones = sorted(df_ventas["estacion"].dropna().unique())
sucursales = sorted(df_ventas["Sucursal_Nombre"].dropna().unique())
productos = sorted(df_ventas["ProductoID"].dropna().unique())

estacion_select = st.sidebar.selectbox("Estación", estaciones)
sucursal_select = st.sidebar.selectbox("Sucursal", sucursales)
producto_select = st.sidebar.selectbox("Producto", productos)

# =============================
# FILTER DATA
# =============================
ventas = df_ventas[
    (df_ventas["estacion"] == estacion_select)
    & (df_ventas["Sucursal_Nombre"] == sucursal_select)
    & (df_ventas["ProductoID"] == producto_select)
]

negados = df_negados[
    (df_negados["estacion"] == estacion_select)
    & (df_negados["Sucursal_Nombre"] == sucursal_select)
    & (df_negados["ProductoID"] == producto_select)
]

# =============================
# AGRUPACIONES
# =============================
ventas_group = (
    ventas.groupby("Sem_ISO")["Cantidad"]
    .sum()
    .reset_index()
    .rename(columns={"Cantidad": "Cantidad_Ventas"})
)

negados_group = negados.groupby("Sem_ISO").size().reset_index(name="Eventos_Negados")

# =============================
# KPIs
# =============================
total_ventas = ventas_group["Cantidad_Ventas"].sum()
total_eventos_negados = negados_group["Eventos_Negados"].sum()
semanas_con_quiebre = (negados_group["Eventos_Negados"] > 0).sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Ventas Totales</div>
            <div class="kpi-value">{int(total_ventas):,}</div>
            <div class="kpi-sub">unidades vendidas</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Eventos de Quiebre</div>
            <div class="kpi-value">{int(total_eventos_negados):,}</div>
            <div class="kpi-sub">demanda no satisfecha</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Semanas con Quiebre</div>
            <div class="kpi-value">{int(semanas_con_quiebre):,}</div>
            <div class="kpi-sub">semanas afectadas</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# =============================
# COLORES CKLASS
# =============================
ROJO = "#C8102E"
GRIS = "#6B6B6B"
GRIS_L = "#E0E0E0"

LAYOUT_BASE = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Inter, Arial, sans-serif", color="#1A1A1A"),
    margin=dict(t=50, b=40, l=50, r=20),
    hovermode="x unified",
    xaxis=dict(showgrid=False, linecolor=GRIS_L, tickfont=dict(color=GRIS)),
    yaxis=dict(gridcolor=GRIS_L, linecolor=GRIS_L, tickfont=dict(color=GRIS)),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

# =============================
# GRÁFICA 1 — VENTAS
# =============================
fig_ventas = go.Figure()

fig_ventas.add_trace(
    go.Scatter(
        x=ventas_group["Sem_ISO"],
        y=ventas_group["Cantidad_Ventas"],
        mode="lines+markers",
        name="Ventas",
        line=dict(color=ROJO, width=3),
        marker=dict(color=ROJO, size=6),
        fill="tozeroy",
        fillcolor="rgba(200,16,46,0.08)",
    )
)

fig_ventas.update_layout(
    **LAYOUT_BASE,
    title=dict(text="Ventas por Semana", font=dict(size=15, color="#1A1A1A")),
    xaxis_title="Semana ISO",
    yaxis_title="Cantidad",
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_ventas, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# =============================
# GRÁFICA 2 — EVENTOS NEGADOS
# =============================
fig_negados = go.Figure()

fig_negados.add_trace(
    go.Bar(
        x=negados_group["Sem_ISO"],
        y=negados_group["Eventos_Negados"],
        name="Eventos Negados",
        marker=dict(
            color=negados_group["Eventos_Negados"],
            colorscale=[[0, GRIS_L], [1, ROJO]],
            showscale=False,
        ),
    )
)

fig_negados.update_layout(
    **LAYOUT_BASE,
    title=dict(
        text="Demanda No Satisfecha por Semana", font=dict(size=15, color="#1A1A1A")
    ),
    xaxis_title="Semana ISO",
    yaxis_title="Número de Eventos",
    bargap=0.3,
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.plotly_chart(fig_negados, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
