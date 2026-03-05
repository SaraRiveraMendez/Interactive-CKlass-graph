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
            color: #CCCCCC !important; font-size: 0.8rem;
            text-transform: uppercase; letter-spacing: 0.05em;
        }
        [data-testid="stSidebar"] hr { border-color: #333; }
        .cklass-header {
            background: linear-gradient(90deg, #C8102E 0%, #A00D24 100%);
            padding: 1.5rem 2rem; border-radius: 8px; margin-bottom: 1.5rem;
        }
        .cklass-header h1 { color: white; margin: 0; font-size: 1.8rem; font-weight: 700; }
        .cklass-header p  { color: rgba(255,255,255,0.75); margin: 0.2rem 0 0 0; font-size: 0.9rem; }
        .kpi-card {
            background: white; border-radius: 8px; padding: 1.2rem 1.5rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08); border-left: 4px solid #C8102E;
        }
        .kpi-label { color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; margin-bottom: 0.3rem; }
        .kpi-value { color: #1A1A1A; font-size: 2rem; font-weight: 700; line-height: 1; }
        .kpi-sub   { color: #C8102E; font-size: 0.78rem; margin-top: 0.3rem; }
        .chart-container {
            background: white; border-radius: 8px; padding: 1rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08); margin-bottom: 1rem;
        }
        .section-title {
            font-size: 1rem; font-weight: 700; color: #1A1A1A;
            text-transform: uppercase; letter-spacing: 0.06em;
            border-left: 4px solid #C8102E; padding-left: 0.6rem;
            margin: 1.5rem 0 0.8rem 0;
        }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding-top: 1rem; }
    </style>
""",
    unsafe_allow_html=True,
)


# =============================
# DATA FUNCTIONS
# =============================
def limpiar_nombre_duplicado(texto):
    if pd.isna(texto) or texto == "nan":
        return texto
    texto = str(texto).strip()
    longitud = len(texto)
    if longitud < 4:
        return texto
    for n in range(2, 11):
        if longitud % n == 0:
            tam_segmento = longitud // n
            segmento = texto[:tam_segmento]
            if segmento * n == texto:
                return segmento
    if longitud % 2 == 0:
        mitad = longitud // 2
        if texto[:mitad] == texto[mitad:]:
            return texto[:mitad]
    for tam in range(3, longitud // 2 + 1):
        segmento = texto[:tam]
        repeticiones = longitud // tam
        if segmento * repeticiones == texto[: tam * repeticiones] and repeticiones >= 2:
            return segmento
    return texto


def limpiar_df(df):
    for col in df.select_dtypes(include="object").columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.encode("utf-8", errors="ignore")
            .str.decode("utf-8")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.replace(r"[\x00-\x1f\x7f-\x9f]", "", regex=True)
        )
    if "Estado" in df.columns:
        df["Estado"] = df["Estado"].apply(limpiar_nombre_duplicado)
    if "Sucursal_Nombre" in df.columns:
        df["Sucursal_Nombre"] = df["Sucursal_Nombre"].apply(limpiar_nombre_duplicado)
    return df


def normalizar_producto_id(product_id):
    product_str = str(product_id).strip().lstrip("0")
    return product_str[:9] if len(product_str) > 9 else product_str


def encontrar_columna(df, nombres_posibles):
    columnas_lower = {col.lower(): col for col in df.columns}
    for nombre in nombres_posibles:
        if nombre.lower() in columnas_lower:
            return columnas_lower[nombre.lower()]
    return None


@st.cache_data(show_spinner="Cargando datos...")
def load_data():
    try:
        ID_NEGADOS = "1-l35EBoTNQKBHKpvGNYlL89S1ORsGYIU"
        ID_VENTAS = "1rRI0Uw5AFouSbpLFjRmm8Y1xmqaBK3iu"

        url_ventas = f"https://drive.google.com/uc?export=download&id={ID_VENTAS}"
        url_negados = f"https://drive.google.com/uc?export=download&id={ID_NEGADOS}"

        df_ventas = limpiar_df(pd.read_csv(url_ventas, encoding="utf-8-sig"))
        df_negados = limpiar_df(pd.read_csv(url_negados, encoding="utf-8-sig"))

        # Detectar columnas
        mapeo_ventas = {
            encontrar_columna(
                df_ventas, ["Cantidad", "cantidad", "Qty", "Ventas"]
            ): "Cantidad",
            encontrar_columna(df_ventas, ["Año", "año", "Year", "Anio"]): "Año",
            encontrar_columna(
                df_ventas, ["Sem_ISO", "sem_iso", "Semana", "Week"]
            ): "Sem_ISO",
            encontrar_columna(
                df_ventas, ["ProductoID", "productoid", "producto_id", "Producto"]
            ): "ProductoID",
            encontrar_columna(df_ventas, ["Estado", "estado", "State"]): "Estado",
            encontrar_columna(
                df_ventas, ["Sucursal_Nombre", "Sucursal", "sucursal"]
            ): "Sucursal_Nombre",
            encontrar_columna(
                df_ventas, ["estacion", "Estacion", "season", "Temporada"]
            ): "estacion",
        }

        mapeo_negados = {
            encontrar_columna(
                df_negados, ["Negados", "negados", "Denied", "Quiebres"]
            ): "Negados",
            encontrar_columna(df_negados, ["Año", "año", "Year", "Anio"]): "Año",
            encontrar_columna(
                df_negados, ["Sem_ISO", "sem_iso", "Semana", "Week"]
            ): "Sem_ISO",
            encontrar_columna(
                df_negados, ["ProductoID", "productoid", "producto_id", "Producto"]
            ): "ProductoID",
            encontrar_columna(df_negados, ["Estado", "estado", "State"]): "Estado",
            encontrar_columna(
                df_negados, ["Sucursal_Nombre", "Sucursal", "sucursal"]
            ): "Sucursal_Nombre",
            encontrar_columna(
                df_negados, ["estacion", "Estacion", "season", "Temporada"]
            ): "estacion",
        }

        # Verificar columnas críticas
        if None in mapeo_ventas:
            raise ValueError(
                f"Columnas faltantes en ventas. Disponibles: {df_ventas.columns.tolist()}"
            )
        if None in mapeo_negados:
            raise ValueError(
                f"Columnas faltantes en negados. Disponibles: {df_negados.columns.tolist()}"
            )

        df_ventas = df_ventas.rename(
            columns={k: v for k, v in mapeo_ventas.items() if k}
        )
        df_negados = df_negados.rename(
            columns={k: v for k, v in mapeo_negados.items() if k}
        )

        df_ventas["Cantidad"] = pd.to_numeric(
            df_ventas["Cantidad"], errors="coerce"
        ).fillna(0)
        df_negados["Negados"] = pd.to_numeric(
            df_negados["Negados"], errors="coerce"
        ).fillna(0)
        df_ventas["Año"] = pd.to_numeric(df_ventas["Año"], errors="coerce")
        df_negados["Año"] = pd.to_numeric(df_negados["Año"], errors="coerce")
        df_ventas["Sem_ISO"] = df_ventas["Sem_ISO"].astype(str).str.strip()
        df_negados["Sem_ISO"] = df_negados["Sem_ISO"].astype(str).str.strip()
        df_ventas["ProductoID_Norm"] = df_ventas["ProductoID"].apply(
            normalizar_producto_id
        )
        df_negados["ProductoID_Norm"] = df_negados["ProductoID"].apply(
            normalizar_producto_id
        )

        return df_ventas, df_negados

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Verifica que los archivos de Google Drive sean públicos")
        st.stop()


df_ventas, df_negados = load_data()

ROJO, GRIS, GRIS_L = "#C8102E", "#6B6B6B", "#E0E0E0"
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

st.sidebar.markdown("## 🔍 Filtros\n---")
estados = sorted(df_ventas["Estado"].dropna().astype(str).unique().tolist())
estado_select = st.sidebar.selectbox("Estado", estados, key="estado_sb")
sucursales = sorted(
    df_ventas[df_ventas["Estado"] == estado_select]["Sucursal_Nombre"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)
sucursal_select = st.sidebar.selectbox("Sucursal", sucursales, key="sucursal_sb")
anios = sorted(
    [
        int(a)
        for a in pd.to_numeric(
            df_ventas[df_ventas["Sucursal_Nombre"] == sucursal_select]["Año"]
            .dropna()
            .unique(),
            errors="coerce",
        )
        if pd.notna(a)
    ],
    reverse=True,
)
anio_select = st.sidebar.selectbox("Año", anios, key="anio_sb")
temporadas = sorted(
    df_ventas[
        (df_ventas["Sucursal_Nombre"] == sucursal_select)
        & (df_ventas["Año"] == anio_select)
    ]["estacion"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)
temporada_select = st.sidebar.selectbox("Temporada", temporadas, key="temporada_sb")
st.sidebar.markdown("---\n## 📊 Modo de Visualización")
modo_vista = st.sidebar.radio(
    "Mostrar datos de:",
    ["Ambos (Ventas + Negados)", "Solo Ventas", "Solo Negados"],
    index=0,
)
st.sidebar.markdown("---\n## 📈 Gráficas")
graficas_activas = {
    "serie_ventas": st.sidebar.checkbox("Serie — Ventas", value=True),
    "serie_quiebres": st.sidebar.checkbox("Serie — Negados", value=True),
    "heat_ventas": st.sidebar.checkbox("Heatmap — Ventas", value=True),
    "heat_quiebres": st.sidebar.checkbox("Heatmap — Negados", value=True),
}

st.markdown(
    f'<div class="cklass-header"><h1>Executive Sales Dashboard</h1><p>{sucursal_select} &nbsp;·&nbsp; {estado_select} &nbsp;·&nbsp; {int(anio_select)} &nbsp;·&nbsp; Temporada {temporada_select}</p></div>',
    unsafe_allow_html=True,
)

ventas = df_ventas[
    (df_ventas["Sucursal_Nombre"] == sucursal_select)
    & (df_ventas["Año"] == anio_select)
    & (df_ventas["estacion"] == temporada_select)
]
negados = df_negados[
    (df_negados["Sucursal_Nombre"] == sucursal_select)
    & (df_negados["Año"] == anio_select)
    & (df_negados["estacion"] == temporada_select)
]

ventas_group = (
    ventas.groupby("Sem_ISO")["Cantidad"]
    .sum()
    .reset_index()
    .rename(columns={"Cantidad": "Cantidad_Ventas"})
)
ventas_group["Sem_ISO_num"] = pd.to_numeric(ventas_group["Sem_ISO"], errors="coerce")
ventas_group = ventas_group.sort_values("Sem_ISO_num").reset_index(drop=True)

negados_group = (
    negados.groupby("Sem_ISO")["Negados"]
    .sum()
    .reset_index()
    .rename(columns={"Negados": "Eventos_Negados"})
)
negados_group["Sem_ISO_num"] = pd.to_numeric(negados_group["Sem_ISO"], errors="coerce")
negados_group = negados_group.sort_values("Sem_ISO_num").reset_index(drop=True)

col_producto = (
    "ProductoID" if modo_vista != "Ambos (Ventas + Negados)" else "ProductoID_Norm"
)
heat_ventas_df = (
    ventas.groupby([col_producto, "Sem_ISO"])["Cantidad"]
    .sum()
    .reset_index()
    .pivot(index=col_producto, columns="Sem_ISO", values="Cantidad")
    .fillna(0)
)
if not heat_ventas_df.empty:
    heat_ventas_df = heat_ventas_df[
        sorted(
            heat_ventas_df.columns,
            key=lambda x: float(x) if str(x).replace(".", "").isdigit() else 0,
        )
    ]
heat_negados_df = (
    negados.groupby([col_producto, "Sem_ISO"])["Negados"]
    .sum()
    .reset_index()
    .pivot(index=col_producto, columns="Sem_ISO", values="Negados")
    .fillna(0)
)
if not heat_negados_df.empty:
    heat_negados_df = heat_negados_df[
        sorted(
            heat_negados_df.columns,
            key=lambda x: float(x) if str(x).replace(".", "").isdigit() else 0,
        )
    ]

total_ventas, total_eventos_negados, semanas_con_quiebre = (
    ventas_group["Cantidad_Ventas"].sum(),
    negados_group["Eventos_Negados"].sum(),
    (negados_group["Eventos_Negados"] > 0).sum(),
)
productos_activos, productos_con_quiebre = (
    ventas[col_producto].nunique(),
    negados[col_producto].nunique(),
)
productos_comunes = (
    len(set(ventas[col_producto].unique()) & set(negados[col_producto].unique()))
    if modo_vista == "Ambos (Ventas + Negados)"
    else 0
)

col1, col2, col3, col4 = st.columns(4)
for col, label, value, sub in [
    (col1, "Ventas Totales", f"{int(total_ventas):,}", "unidades vendidas"),
    (
        col2,
        "Eventos de Negado",
        f"{int(total_eventos_negados):,}",
        "demanda no satisfecha",
    ),
    (col3, "Semanas con Negados", f"{int(semanas_con_quiebre):,}", "semanas afectadas"),
    (
        col4,
        "Productos",
        f"{int(productos_activos):,}",
        (
            f"{productos_con_quiebre} con negados"
            if modo_vista != "Ambos (Ventas + Negados)"
            else f"{productos_comunes} en común"
        ),
    ),
]:
    with col:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

series_activas = []
if graficas_activas["serie_ventas"] and modo_vista != "Solo Negados":
    series_activas.append("ventas")
if graficas_activas["serie_quiebres"] and modo_vista != "Solo Ventas":
    series_activas.append("quiebres")

if series_activas:
    st.markdown(
        '<div class="section-title">Comportamiento Global de la Sucursal</div>',
        unsafe_allow_html=True,
    )
    if len(series_activas) == 2:
        col_ventas, col_quiebres = st.columns(2)
    else:
        col_ventas = col_quiebres = st.container()

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
        fig_ventas.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=ventas_group["Sem_ISO"].tolist(),
        )
        with col_ventas:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_ventas, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    if "quiebres" in series_activas:
        fig_negados = go.Figure()
        fig_negados.add_trace(
            go.Scatter(
                x=negados_group["Sem_ISO"],
                y=negados_group["Eventos_Negados"],
                mode="lines+markers",
                name="Quiebres",
                line=dict(color=ROJO, width=3),
                marker=dict(color=ROJO, size=6),
                fill="tozeroy",
                fillcolor="rgba(200,16,46,0.08)",
            )
        )
        fig_negados.update_layout(
            **LAYOUT_BASE,
            title=dict(text="Negados Totales por Semana", font=dict(size=14)),
            xaxis_title="Semana ISO",
            yaxis_title="Unidades No Satisfechas",
        )
        fig_negados.update_xaxes(
            type="category",
            categoryorder="array",
            categoryarray=negados_group["Sem_ISO"].tolist(),
        )
        with col_quiebres:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(fig_negados, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

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

if (
    graficas_activas["heat_ventas"]
    and modo_vista != "Solo Negados"
    or graficas_activas["heat_quiebres"]
    and modo_vista != "Solo Ventas"
):
    st.markdown(
        '<div class="section-title">Fluctuación por Producto y Semana</div>',
        unsafe_allow_html=True,
    )

if (
    graficas_activas["heat_ventas"]
    and modo_vista != "Solo Negados"
    and not heat_ventas_df.empty
):
    fig_hv = go.Figure(
        go.Heatmap(
            z=heat_ventas_df.values,
            x=[str(s) for s in heat_ventas_df.columns],
            y=[str(p) for p in heat_ventas_df.index],
            colorscale=COLORSCALE_VENTAS,
            hoverongaps=False,
            hovertemplate="Semana: %{x}<br>Producto: %{y}<br>Ventas: %{z:,}<extra></extra>",
            colorbar=dict(title="Unidades", tickfont=dict(size=10)),
        )
    )
    fig_hv.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif"),
        title=dict(
            text="Heatmap de Ventas por Producto", font=dict(size=14, color="#1A1A1A")
        ),
        xaxis=dict(
            title="Semana ISO",
            tickangle=0,
            tickfont=dict(size=9, color=GRIS),
            showgrid=False,
        ),
        yaxis=dict(title="Producto", tickfont=dict(size=8, color=GRIS), autorange=True),
        margin=dict(t=50, b=80, l=80, r=20),
        height=500,
    )
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_hv, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if (
    graficas_activas["heat_quiebres"]
    and modo_vista != "Solo Ventas"
    and not heat_negados_df.empty
):
    fig_hn = go.Figure(
        go.Heatmap(
            z=heat_negados_df.values,
            x=[str(s) for s in heat_negados_df.columns],
            y=[str(p) for p in heat_negados_df.index],
            colorscale=COLORSCALE_QUIEBRE,
            hoverongaps=False,
            hovertemplate="Semana: %{x}<br>Producto: %{y}<br>Negados: %{z:,}<extra></extra>",
            colorbar=dict(title="Unidades No\nSatisfechas", tickfont=dict(size=10)),
        )
    )
    fig_hn.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Arial, sans-serif"),
        title=dict(
            text="Heatmap de Negados por Producto", font=dict(size=14, color="#1A1A1A")
        ),
        xaxis=dict(
            title="Semana ISO",
            tickangle=0,
            tickfont=dict(size=9, color=GRIS),
            showgrid=False,
        ),
        yaxis=dict(title="Producto", tickfont=dict(size=8, color=GRIS), autorange=True),
        margin=dict(t=50, b=80, l=80, r=20),
        height=500,
    )
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_hn, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if ventas.empty and negados.empty:
    st.warning("⚠️ No hay datos para la combinación de filtros seleccionada.")
