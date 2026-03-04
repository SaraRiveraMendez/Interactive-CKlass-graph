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
        .stApp { background-color: #F5F5F5; }

        [data-testid="stSidebar"] { background-color: #1A1A1A; }
        [data-testid="stSidebar"] * { color: #FFFFFF !important; }
        [data-testid="stSidebar"] .stSelectbox label {
            color: #CCCCCC !important;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        [data-testid="stSidebar"] hr { border-color: #333; }

        .cklass-header {
            background: linear-gradient(90deg, #C8102E 0%, #A00D24 100%);
            padding: 1.5rem 2rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }
        .cklass-header h1 { color: white; margin: 0; font-size: 1.8rem; font-weight: 700; }
        .cklass-header p  { color: rgba(255,255,255,0.75); margin: 0.2rem 0 0 0; font-size: 0.9rem; }

        .filter-badge {
            background: #2A2A2A;
            border-radius: 6px;
            padding: 0.6rem 1rem;
            margin-bottom: 0.5rem;
            font-size: 0.78rem;
            color: #AAAAAA;
        }
        .filter-badge span { color: #FFFFFF; font-weight: 600; }

        .kpi-card {
            background: white;
            border-radius: 8px;
            padding: 1.2rem 1.5rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            border-left: 4px solid #C8102E;
        }
        .kpi-label { color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 0.3rem; }
        .kpi-value { color: #1A1A1A; font-size: 2rem; font-weight: 700; line-height: 1; }
        .kpi-sub   { color: #C8102E; font-size: 0.78rem; margin-top: 0.3rem; }

        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            margin-bottom: 1rem;
        }

        .section-title {
            font-size: 1rem;
            font-weight: 700;
            color: #1A1A1A;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            border-left: 4px solid #C8102E;
            padding-left: 0.6rem;
            margin: 1.5rem 0 0.8rem 0;
        }

        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1rem; }
    </style>
""",
    unsafe_allow_html=True,
)


# =============================
# DATA
# =============================
@st.cache_data
def load_data():
    df_ventas = pd.read_csv("data/ventas_lights_final.csv")
    df_negados = pd.read_csv("data/negados_lights_final.csv")

    # Limpiar Estado — por si hay valores concatenados duplicados
    for df in [df_ventas, df_negados]:
        if "Estado" in df.columns:

            def limpiar_estado(val):
                if not isinstance(val, str):
                    return val
                val = val.strip()
                for n in [2, 3, 4]:
                    L = len(val)
                    if L % n == 0:
                        parte = val[: L // n]
                        if parte * n == val:
                            return parte
                return val

            df["Estado"] = df["Estado"].apply(limpiar_estado)

    return df_ventas, df_negados


df_ventas, df_negados = load_data()

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
# SIDEBAR — FILTROS EN CASCADA
# =============================
st.sidebar.markdown("## 🔍 Filtros")
st.sidebar.markdown("---")

# 1. Estado
estados = sorted(df_ventas["Estado"].dropna().unique())
estado_select = st.sidebar.selectbox("Estado", estados)

# 2. Sucursal — filtrada por estado
sucursales = sorted(
    df_ventas[df_ventas["Estado"] == estado_select]["Sucursal_Nombre"].dropna().unique()
)
sucursal_select = st.sidebar.selectbox("Sucursal", sucursales)

# 3. Año — filtrado por sucursal
anios = sorted(
    df_ventas[df_ventas["Sucursal_Nombre"] == sucursal_select]["Año"].dropna().unique(),
    reverse=True,
)
anio_select = st.sidebar.selectbox("Año", anios)

# 4. Estación/Temporada — filtrada por sucursal + año
temporadas = sorted(
    df_ventas[
        (df_ventas["Sucursal_Nombre"] == sucursal_select)
        & (df_ventas["Año"] == anio_select)
    ]["estacion"]
    .dropna()
    .unique()
)
temporada_select = st.sidebar.selectbox("Temporada", temporadas)

# Productos que pertenecen a esta sucursal
productos_sucursal = sorted(
    df_ventas[df_ventas["Sucursal_Nombre"] == sucursal_select]["ProductoID"]
    .dropna()
    .unique()
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div class="filter-badge">📦 <span>{len(productos_sucursal)}</span> productos en esta sucursal</div>
""",
    unsafe_allow_html=True,
)

# =============================
# CHECKLIST DE GRÁFICAS
# =============================
st.sidebar.markdown("---")
st.sidebar.markdown("## 📊 Visualizaciones")

graficas_activas = {
    "serie_ventas": st.sidebar.checkbox("Serie — Ventas", value=True),
    "serie_quiebres": st.sidebar.checkbox("Serie — Quiebres", value=True),
    "heat_ventas": st.sidebar.checkbox("Heatmap — Ventas", value=True),
    "heat_quiebres": st.sidebar.checkbox("Heatmap — Quiebres", value=True),
}

# =============================
# HEADER
# =============================
st.markdown(
    f"""
    <div class="cklass-header">
        <h1>Executive Sales Dashboard</h1>
        <p>{sucursal_select} &nbsp;·&nbsp; {estado_select} &nbsp;·&nbsp; {anio_select} &nbsp;·&nbsp; Temporada {temporada_select}</p>
    </div>
""",
    unsafe_allow_html=True,
)

# =============================
# FILTER DATA
# =============================
mask_ventas = (
    (df_ventas["Sucursal_Nombre"] == sucursal_select)
    & (df_ventas["Año"] == anio_select)
    & (df_ventas["estacion"] == temporada_select)
    & (df_ventas["ProductoID"].isin(productos_sucursal))
)
mask_negados = (
    (df_negados["Sucursal_Nombre"] == sucursal_select)
    & (df_negados["Año"] == anio_select)
    & (df_negados["estacion"] == temporada_select)
    & (df_negados["ProductoID"].isin(productos_sucursal))
)

ventas = df_ventas[mask_ventas]
negados = df_negados[mask_negados]

# =============================
# AGRUPACIONES — KPIs
# =============================
ventas_group = (
    ventas.groupby("Sem_ISO")["Cantidad"]
    .sum()
    .reset_index()
    .rename(columns={"Cantidad": "Cantidad_Ventas"})
)

# ✅ CORRECCIÓN: usar columna "Negados" en lugar de contar filas
negados_group = (
    negados.groupby("Sem_ISO")["Negados"]
    .sum()
    .reset_index()
    .rename(columns={"Negados": "Eventos_Negados"})
)

total_ventas = ventas_group["Cantidad_Ventas"].sum()
total_eventos_negados = negados_group["Eventos_Negados"].sum()
semanas_con_quiebre = (negados_group["Eventos_Negados"] > 0).sum()
productos_activos = ventas["ProductoID"].nunique()

# =============================
# KPIs
# =============================
col1, col2, col3, col4 = st.columns(4)

for col, label, value, sub in [
    (col1, "Ventas Totales", f"{int(total_ventas):,}", "unidades vendidas"),
    (
        col2,
        "Eventos de Quiebre",
        f"{int(total_eventos_negados):,}",
        "demanda no satisfecha",
    ),
    (col3, "Semanas con Quiebre", f"{int(semanas_con_quiebre):,}", "semanas afectadas"),
    (
        col4,
        "Productos Activos",
        f"{int(productos_activos):,}",
        f"de {len(productos_sucursal)} en sucursal",
    ),
]:
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-sub">{sub}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# =============================
# AGRUPACIONES — HEATMAPS
# =============================
heat_ventas_df = (
    ventas.groupby(["ProductoID", "Sem_ISO"])["Cantidad"]
    .sum()
    .reset_index()
    .pivot(index="ProductoID", columns="Sem_ISO", values="Cantidad")
    .fillna(0)
)

# ✅ CORRECCIÓN: sumar "Negados" en lugar de contar filas
heat_negados_df = (
    negados.groupby(["ProductoID", "Sem_ISO"])["Negados"]
    .sum()
    .reset_index()
    .pivot(index="ProductoID", columns="Sem_ISO", values="Negados")
    .fillna(0)
)

# =============================
# SECCIÓN — SERIES DE TIEMPO
# =============================
series_activas = []
if graficas_activas["serie_ventas"]:
    series_activas.append("ventas")
if graficas_activas["serie_quiebres"]:
    series_activas.append("quiebres")

if series_activas:
    st.markdown(
        '<div class="section-title">Comportamiento Global de la Sucursal</div>',
        unsafe_allow_html=True,
    )

    # Layout automático
    if len(series_activas) == 2:
        contenedores = st.columns(2)
        col_ventas = contenedores[0]
        col_quiebres = contenedores[1]
    else:
        col_ventas = st.container()
        col_quiebres = st.container()

    if "ventas" in series_activas:
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
            title=dict(text="Ventas Totales por Semana", font=dict(size=14)),
            xaxis_title="Semana ISO",
            yaxis_title="Cantidad",
        )
        with col_ventas:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_ventas, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    if "quiebres" in series_activas:
        fig_negados = go.Figure()
        fig_negados.add_trace(
            go.Bar(
                x=negados_group["Sem_ISO"],
                y=negados_group["Eventos_Negados"],
                name="Quiebres",
                marker=dict(
                    color=negados_group["Eventos_Negados"],
                    colorscale=[[0, GRIS_L], [1, ROJO]],
                    showscale=False,
                ),
            )
        )
        fig_negados.update_layout(
            **LAYOUT_BASE,
            title=dict(text="Quiebres Totales por Semana", font=dict(size=14)),
            xaxis_title="Semana ISO",
            yaxis_title="Unidades No Satisfechas",
            bargap=0.3,
        )
        with col_quiebres:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_negados, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# =============================
# SECCIÓN — HEATMAPS
# =============================
heatmaps_activos = graficas_activas["heat_ventas"] or graficas_activas["heat_quiebres"]

if heatmaps_activos:
    st.markdown(
        '<div class="section-title">Fluctuación por Producto y Semana</div>',
        unsafe_allow_html=True,
    )

HEATMAP_LAYOUT = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Inter, Arial, sans-serif"),
    xaxis=dict(
        title="Producto",
        tickangle=-45,
        tickfont=dict(size=8, color=GRIS),
        showgrid=False,
    ),
    yaxis=dict(
        title="Semana ISO", tickfont=dict(size=9, color=GRIS), autorange="reversed"
    ),
    margin=dict(t=50, b=120, l=80, r=20),
    height=500,
)

# ✅ CORRECCIÓN colores heatmap: escala con mayor contraste
COLORSCALE_VENTAS = [
    [0, "#F0F0F0"],
    [0.01, "#FADADD"],
    [0.3, "#F4A7B4"],
    [0.7, "#E05070"],
    [1.0, ROJO],
]
COLORSCALE_QUIEBRE = [
    [0, "#F0F0F0"],
    [0.01, "#FFE8CC"],
    [0.3, "#FFBB77"],
    [0.7, "#E07020"],
    [1.0, "#8B2500"],
]

if graficas_activas["heat_ventas"] and not heat_ventas_df.empty:
    fig_hv = go.Figure(
        go.Heatmap(
            z=heat_ventas_df.T.values,
            x=[str(p) for p in heat_ventas_df.index],
            y=[str(s) for s in heat_ventas_df.columns],
            colorscale=COLORSCALE_VENTAS,
            hoverongaps=False,
            hovertemplate="Producto: %{x}<br>Semana: %{y}<br>Ventas: %{z:,}<extra></extra>",
            colorbar=dict(title="Unidades", tickfont=dict(size=10)),
        )
    )
    fig_hv.update_layout(
        **HEATMAP_LAYOUT,
        title=dict(
            text="Heatmap de Ventas por Producto", font=dict(size=14, color="#1A1A1A")
        ),
    )
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_hv, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if graficas_activas["heat_quiebres"] and not heat_negados_df.empty:
    fig_hn = go.Figure(
        go.Heatmap(
            z=heat_negados_df.T.values,
            x=[str(p) for p in heat_negados_df.index],
            y=[str(s) for s in heat_negados_df.columns],
            colorscale=COLORSCALE_QUIEBRE,
            hoverongaps=False,
            hovertemplate="Producto: %{x}<br>Semana: %{y}<br>Quiebres: %{z:,}<extra></extra>",
            colorbar=dict(title="Unidades\nNo Satisfechas", tickfont=dict(size=10)),
        )
    )
    fig_hn.update_layout(
        **HEATMAP_LAYOUT,
        title=dict(
            text="Heatmap de Quiebres por Producto", font=dict(size=14, color="#1A1A1A")
        ),
    )
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_hn, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================
# EMPTY STATE
# =============================
if ventas.empty and negados.empty:
    st.warning("⚠️ No hay datos para la combinación de filtros seleccionada.")
