# =============================
# LIBRARIES
# =============================
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import gc

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="Executive Dashboard | Cklass", layout="wide")

# =============================
# CSS
# =============================
st.markdown(
    """
<style>
.stApp{background-color:#F5F5F5}
[data-testid="stSidebar"]{background-color:#1A1A1A}
[data-testid="stSidebar"] *{color:#FFF!important}
.cklass-header{background:linear-gradient(90deg,#C8102E 0%,#A00D24 100%);padding:1.5rem 2rem;border-radius:8px;margin-bottom:1.5rem}
.cklass-header h1{color:#FFF;margin:0;font-size:1.8rem;font-weight:700}
.cklass-header p{color:rgba(255,255,255,0.75);margin:0.2rem 0 0 0;font-size:0.9rem}
.kpi-card{background:#FFF;border-radius:8px;padding:1.2rem 1.5rem;box-shadow:0 1px 4px rgba(0,0,0,0.08);border-left:4px solid #C8102E}
.kpi-label{color:#888;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-bottom:0.3rem}
.kpi-value{color:#1A1A1A;font-size:2rem;font-weight:700;line-height:1}
.kpi-sub{color:#C8102E;font-size:0.78rem;margin-top:0.3rem}
.chart-container{background:#FFF;border-radius:8px;padding:1rem;box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-bottom:1rem}
.section-title{font-size:1rem;font-weight:700;color:#1A1A1A;text-transform:uppercase;letter-spacing:0.06em;border-left:4px solid #C8102E;padding-left:0.6rem;margin:1.5rem 0 0.8rem 0}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1rem}
</style>
""",
    unsafe_allow_html=True,
)


# =============================
# FUNCTIONS
# =============================
def limpiar_nombre_duplicado(texto):
    if pd.isna(texto) or texto == "nan":
        return texto
    texto = str(texto).strip()
    if len(texto) < 4:
        return texto
    for n in range(2, 6):
        if len(texto) % n == 0:
            seg = texto[: len(texto) // n]
            if seg * n == texto:
                return seg
    return texto


def encontrar_columna(df, nombres):
    cols = {c.lower(): c for c in df.columns}
    for n in nombres:
        if n.lower() in cols:
            return cols[n.lower()]
    return None


@st.cache_data(show_spinner="Cargando datos...", ttl=3600)
def load_data():
    try:
        # URLs para archivos grandes
        url_v = "https://drive.usercontent.google.com/download?id=1rRI0Uw5AFouSbpLFjRmm8Y1xmqaBK3iu&export=download&confirm=t"
        url_n = "https://drive.usercontent.google.com/download?id=1-l35EBoTNQKBHKpvGNYlL89S1ORsGYIU&export=download&confirm=t"

        # Cargar datos
        df_v = pd.read_csv(url_v, encoding="utf-8-sig")
        df_n = pd.read_csv(url_n, encoding="utf-8-sig")

        # Limpiar strings
        for col in df_v.select_dtypes(include="object").columns:
            df_v[col] = df_v[col].astype(str).str.strip()
        for col in df_n.select_dtypes(include="object").columns:
            df_n[col] = df_n[col].astype(str).str.strip()

        # Detectar y renombrar columnas
        mapeo_v = {
            encontrar_columna(
                df_v, ["Cantidad", "cantidad", "Qty", "Ventas"]
            ): "Cantidad",
            encontrar_columna(df_v, ["Año", "año", "Year", "Anio"]): "Año",
            encontrar_columna(df_v, ["Sem_ISO", "Semana", "Week"]): "Sem_ISO",
            encontrar_columna(df_v, ["ProductoID", "Producto"]): "ProductoID",
            encontrar_columna(df_v, ["Estado", "State"]): "Estado",
            encontrar_columna(df_v, ["Sucursal_Nombre", "Sucursal"]): "Sucursal_Nombre",
            encontrar_columna(
                df_v, ["estacion", "Estacion", "season", "Temporada"]
            ): "estacion",
        }

        mapeo_n = {
            encontrar_columna(df_n, ["Negados", "Denied", "Quiebres"]): "Negados",
            encontrar_columna(df_n, ["Año", "año", "Year", "Anio"]): "Año",
            encontrar_columna(df_n, ["Sem_ISO", "Semana", "Week"]): "Sem_ISO",
            encontrar_columna(df_n, ["ProductoID", "Producto"]): "ProductoID",
            encontrar_columna(df_n, ["Estado", "State"]): "Estado",
            encontrar_columna(df_n, ["Sucursal_Nombre", "Sucursal"]): "Sucursal_Nombre",
            encontrar_columna(
                df_n, ["estacion", "Estacion", "season", "Temporada"]
            ): "estacion",
        }

        if None in mapeo_v or None in mapeo_n:
            raise ValueError("Columnas críticas no encontradas")

        df_v = df_v.rename(columns={k: v for k, v in mapeo_v.items() if k})
        df_n = df_n.rename(columns={k: v for k, v in mapeo_n.items() if k})

        # Convertir tipos
        df_v["Cantidad"] = (
            pd.to_numeric(df_v["Cantidad"], errors="coerce").fillna(0).astype("float32")
        )
        df_n["Negados"] = (
            pd.to_numeric(df_n["Negados"], errors="coerce").fillna(0).astype("float32")
        )
        df_v["Año"] = pd.to_numeric(df_v["Año"], errors="coerce").astype("Int16")
        df_n["Año"] = pd.to_numeric(df_n["Año"], errors="coerce").astype("Int16")

        # Limpiar duplicados
        df_v["Estado"] = df_v["Estado"].apply(limpiar_nombre_duplicado)
        df_v["Sucursal_Nombre"] = df_v["Sucursal_Nombre"].apply(
            limpiar_nombre_duplicado
        )
        df_n["Estado"] = df_n["Estado"].apply(limpiar_nombre_duplicado)
        df_n["Sucursal_Nombre"] = df_n["Sucursal_Nombre"].apply(
            limpiar_nombre_duplicado
        )

        gc.collect()
        return df_v, df_n

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.stop()


# Cargar datos
try:
    df_ventas, df_negados = load_data()
except Exception as e:
    st.error(f"No se pudieron cargar los datos: {e}")
    st.stop()

# Constantes
ROJO = "#C8102E"
LAYOUT_BASE = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(t=50, b=40, l=50, r=20),
    hovermode="x unified",
)

# Sidebar
st.sidebar.markdown("## 🔍 Filtros\n---")
estados = sorted(df_ventas["Estado"].dropna().unique().tolist())
estado_select = st.sidebar.selectbox("Estado", estados)
sucursales = sorted(
    df_ventas[df_ventas["Estado"] == estado_select]["Sucursal_Nombre"]
    .dropna()
    .unique()
    .tolist()
)
sucursal_select = st.sidebar.selectbox("Sucursal", sucursales)
anios = sorted(
    [
        int(a)
        for a in df_ventas[df_ventas["Sucursal_Nombre"] == sucursal_select]["Año"]
        .dropna()
        .unique()
        if pd.notna(a)
    ],
    reverse=True,
)
anio_select = st.sidebar.selectbox("Año", anios)
temporadas = sorted(
    df_ventas[
        (df_ventas["Sucursal_Nombre"] == sucursal_select)
        & (df_ventas["Año"] == anio_select)
    ]["estacion"]
    .dropna()
    .unique()
    .tolist()
)
temporada_select = st.sidebar.selectbox("Temporada", temporadas)
st.sidebar.markdown("---\n## 📊 Modo")
modo_vista = st.sidebar.radio(
    "Mostrar:", ["Ambos", "Solo Ventas", "Solo Negados"], index=0
)
st.sidebar.markdown("---\n## 📈 Gráficas")
show_series = st.sidebar.checkbox("Series de Tiempo", value=True)
show_heat = st.sidebar.checkbox("Heatmaps", value=False)

# Header
st.markdown(
    f'<div class="cklass-header"><h1>Executive Sales Dashboard</h1><p>{sucursal_select} · {estado_select} · {int(anio_select)} · {temporada_select}</p></div>',
    unsafe_allow_html=True,
)

# Filtrar datos
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

if ventas.empty and negados.empty:
    st.warning("⚠️ No hay datos para estos filtros")
    st.stop()

# Agrupar
vg = ventas.groupby("Sem_ISO")["Cantidad"].sum().reset_index()
vg["num"] = pd.to_numeric(vg["Sem_ISO"], errors="coerce")
vg = vg.sort_values("num").reset_index(drop=True)

ng = negados.groupby("Sem_ISO")["Negados"].sum().reset_index()
ng["num"] = pd.to_numeric(ng["Sem_ISO"], errors="coerce")
ng = ng.sort_values("num").reset_index(drop=True)

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Ventas Totales</div><div class="kpi-value">{int(vg["Cantidad"].sum()):,}</div><div class="kpi-sub">unidades</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Negados</div><div class="kpi-value">{int(ng["Negados"].sum()):,}</div><div class="kpi-sub">eventos</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Semanas Afectadas</div><div class="kpi-value">{(ng["Negados"] > 0).sum()}</div><div class="kpi-sub">semanas</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">Productos</div><div class="kpi-value">{ventas["ProductoID"].nunique()}</div><div class="kpi-sub">activos</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Series de tiempo
if show_series:
    st.markdown(
        '<div class="section-title">Comportamiento Semanal</div>',
        unsafe_allow_html=True,
    )

    if modo_vista == "Ambos":
        c1, c2 = st.columns(2)
    else:
        c1 = c2 = st.container()

    if modo_vista in ["Ambos", "Solo Ventas"]:
        fig = go.Figure(
            go.Scatter(
                x=vg["Sem_ISO"],
                y=vg["Cantidad"],
                mode="lines+markers",
                line=dict(color=ROJO, width=3),
                marker=dict(size=6),
                fill="tozeroy",
                fillcolor="rgba(200,16,46,0.08)",
            )
        )
        fig.update_layout(
            **LAYOUT_BASE,
            title="Ventas por Semana",
            xaxis_title="Semana",
            yaxis_title="Cantidad",
        )
        fig.update_xaxes(
            type="category", categoryorder="array", categoryarray=vg["Sem_ISO"].tolist()
        )
        with c1:
            st.plotly_chart(fig, use_container_width=True)

    if modo_vista in ["Ambos", "Solo Negados"]:
        fig = go.Figure(
            go.Scatter(
                x=ng["Sem_ISO"],
                y=ng["Negados"],
                mode="lines+markers",
                line=dict(color=ROJO, width=3),
                marker=dict(size=6),
                fill="tozeroy",
                fillcolor="rgba(200,16,46,0.08)",
            )
        )
        fig.update_layout(
            **LAYOUT_BASE,
            title="Negados por Semana",
            xaxis_title="Semana",
            yaxis_title="Negados",
        )
        fig.update_xaxes(
            type="category", categoryorder="array", categoryarray=ng["Sem_ISO"].tolist()
        )
        with c2:
            st.plotly_chart(fig, use_container_width=True)

# Heatmaps
if show_heat:
    st.markdown(
        '<div class="section-title">Distribución por Producto</div>',
        unsafe_allow_html=True,
    )

    if modo_vista in ["Ambos", "Solo Ventas"]:
        hv = (
            ventas.groupby(["ProductoID", "Sem_ISO"])["Cantidad"]
            .sum()
            .reset_index()
            .pivot(index="ProductoID", columns="Sem_ISO", values="Cantidad")
            .fillna(0)
        )
        if not hv.empty:
            hv = hv.iloc[:300]  # Máximo 300 productos
            fig = go.Figure(
                go.Heatmap(
                    z=hv.values,
                    x=[str(s) for s in hv.columns],
                    y=[str(p) for p in hv.index],
                    colorscale=[[0, "#F0F0F0"], [1, ROJO]],
                    showscale=False,
                )
            )
            fig.update_layout(
                title="Heatmap Ventas", height=400, margin=dict(t=50, b=50, l=80, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

    if modo_vista in ["Ambos", "Solo Negados"]:
        hn = (
            negados.groupby(["ProductoID", "Sem_ISO"])["Negados"]
            .sum()
            .reset_index()
            .pivot(index="ProductoID", columns="Sem_ISO", values="Negados")
            .fillna(0)
        )
        if not hn.empty:
            hn = hn.iloc[:300]
            fig = go.Figure(
                go.Heatmap(
                    z=hn.values,
                    x=[str(s) for s in hn.columns],
                    y=[str(p) for p in hn.index],
                    colorscale=[[0, "#F0F0F0"], [1, "#8B2500"]],
                    showscale=False,
                )
            )
            fig.update_layout(
                title="Heatmap Negados", height=400, margin=dict(t=50, b=50, l=80, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
