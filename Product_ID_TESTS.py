import pandas as pd
import streamlit as st


# Cargar datos (usando las funciones del dashboard)
def limpiar_df(df):
    for col in df.select_dtypes(include="object").columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.encode("utf-8", errors="ignore")
            .str.decode("utf-8")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )
    return df


df_ventas = pd.read_csv("data/ventas_lights_final.csv", encoding="utf-8-sig")
df_negados = pd.read_csv("data/negados_lights_final.csv", encoding="utf-8-sig")
df_ventas = limpiar_df(df_ventas)
df_negados = limpiar_df(df_negados)

st.title("🔍 Diagnóstico de ProductoID")

# Filtrar por Tijuana como en tu ejemplo
sucursal = "Tijuana"
ventas_tij = df_ventas[df_ventas["Sucursal_Nombre"] == sucursal]
negados_tij = df_negados[df_negados["Sucursal_Nombre"] == sucursal]

st.header("Ejemplos de ProductoID")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Ventas")
    st.write("Primeros 20 ProductoID:")
    productos_v = ventas_tij["ProductoID"].dropna().unique()[:20]
    for i, p in enumerate(productos_v, 1):
        st.text(f"{i:2d}. '{p}' (tipo: {type(p).__name__}, len: {len(str(p))})")

    st.write(f"\n**Total únicos:** {ventas_tij['ProductoID'].nunique()}")
    st.write(f"**Tipo de dato:** {ventas_tij['ProductoID'].dtype}")

with col2:
    st.subheader("🚫 Negados")
    st.write("Primeros 20 ProductoID:")
    productos_n = negados_tij["ProductoID"].dropna().unique()[:20]
    for i, p in enumerate(productos_n, 1):
        st.text(f"{i:2d}. '{p}' (tipo: {type(p).__name__}, len: {len(str(p))})")

    st.write(f"\n**Total únicos:** {negados_tij['ProductoID'].nunique()}")
    st.write(f"**Tipo de dato:** {negados_tij['ProductoID'].dtype}")

st.header("🔬 Análisis detallado")

st.subheader("Patrones comunes")
col1, col2 = st.columns(2)

with col1:
    st.write("**Ventas - Primeros 5 caracteres:**")
    prefijos_v = ventas_tij["ProductoID"].astype(str).str[:5].value_counts().head(10)
    st.dataframe(prefijos_v)

with col2:
    st.write("**Negados - Primeros 5 caracteres:**")
    prefijos_n = negados_tij["ProductoID"].astype(str).str[:5].value_counts().head(10)
    st.dataframe(prefijos_n)

st.subheader("Longitudes de ProductoID")
col1, col2 = st.columns(2)

with col1:
    st.write("**Ventas:**")
    longitudes_v = (
        ventas_tij["ProductoID"].astype(str).str.len().value_counts().sort_index()
    )
    st.dataframe(longitudes_v)

with col2:
    st.write("**Negados:**")
    longitudes_n = (
        negados_tij["ProductoID"].astype(str).str.len().value_counts().sort_index()
    )
    st.dataframe(longitudes_n)

st.subheader("Búsqueda de coincidencias parciales")
st.write("Intentando encontrar productos que coincidan parcialmente...")

# Probar si removiendo espacios o convirtiendo a mayúsculas hay match
productos_v_clean = set(ventas_tij["ProductoID"].astype(str).str.strip().str.upper())
productos_n_clean = set(negados_tij["ProductoID"].astype(str).str.strip().str.upper())
match_clean = productos_v_clean & productos_n_clean

st.write(f"**Con limpieza (strip + upper):** {len(match_clean)} coincidencias")

if len(match_clean) > 0:
    st.write("Ejemplos de coincidencias:")
    for p in list(match_clean)[:10]:
        st.text(f"  - {p}")
import pandas as pd
import numpy as np


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
    return df


# Cargar datos
df_ventas = pd.read_csv("data/ventas_lights_final.csv", encoding="utf-8-sig")
df_ventas = limpiar_df(df_ventas)

print("=" * 80)
print("DIAGNÓSTICO COMPLETO: DUPLICADOS EN SELECTBOX")
print("=" * 80)

# 1. Revisar el tipo de dato que devuelve unique()
print("\n1. TIPO DE DATOS:")
estados_unique = df_ventas["Estado"].dropna().unique()
print(f"   Tipo de estados_unique: {type(estados_unique)}")
print(f"   Dtype: {estados_unique.dtype}")
print(f"   Longitud: {len(estados_unique)}")

# 2. Ver los primeros estados
print("\n2. PRIMEROS 10 ESTADOS:")
for i, estado in enumerate(estados_unique[:10], 1):
    print(f"   {i:2d}. {type(estado).__name__:15s} | '{estado}' | hash: {hash(estado)}")

# 3. Probar diferentes métodos de eliminar duplicados
print("\n3. PRUEBA DE MÉTODOS PARA ELIMINAR DUPLICADOS:")

# Método 1: sorted(unique())
metodo1 = sorted(df_ventas["Estado"].dropna().unique())
print(f"\n   Método 1 - sorted(unique()): {len(metodo1)} elementos")
print(
    f"   Tipo: {type(metodo1)}, Primer elemento tipo: {type(metodo1[0]) if metodo1 else 'N/A'}"
)

# Método 2: sorted(list(set(unique())))
metodo2 = sorted(list(set(df_ventas["Estado"].dropna().unique())))
print(f"\n   Método 2 - sorted(list(set(unique()))): {len(metodo2)} elementos")
print(
    f"   Tipo: {type(metodo2)}, Primer elemento tipo: {type(metodo2[0]) if metodo2 else 'N/A'}"
)

# Método 3: sorted(df.unique().tolist())
metodo3 = sorted(df_ventas["Estado"].dropna().unique().tolist())
print(f"\n   Método 3 - sorted(unique().tolist()): {len(metodo3)} elementos")
print(
    f"   Tipo: {type(metodo3)}, Primer elemento tipo: {type(metodo3[0]) if metodo3 else 'N/A'}"
)

# Método 4: sorted(set(df.tolist()))
metodo4 = sorted(set(df_ventas["Estado"].dropna().tolist()))
print(f"\n   Método 4 - sorted(set(tolist())): {len(metodo4)} elementos")
print(
    f"   Tipo: {type(metodo4)}, Primer elemento tipo: {type(metodo4[0]) if metodo4 else 'N/A'}"
)

# 4. Comparar si tienen los mismos valores
print("\n4. COMPARACIÓN DE RESULTADOS:")
print(f"   ¿Método 1 == Método 2? {metodo1 == metodo2}")
print(f"   ¿Método 1 == Método 3? {metodo1 == metodo3}")
print(f"   ¿Método 1 == Método 4? {metodo1 == metodo4}")

# 5. Buscar duplicados específicamente
print("\n5. BUSCAR DUPLICADOS REALES EN LOS DATOS:")
from collections import Counter

estados_counter = Counter(df_ventas["Estado"].dropna().tolist())
duplicados = {k: v for k, v in estados_counter.items() if v > 1}
print(f"   Estados que aparecen más de una vez en el DataFrame: {len(duplicados)}")
if duplicados:
    print("   (Esto es normal - cada estado aparece en múltiples filas)")

# 6. Ver si hay variaciones sutiles del mismo estado
print("\n6. BUSCAR VARIACIONES SUTILES:")
estados_set = set(df_ventas["Estado"].dropna().unique())
for estado in list(estados_set)[:5]:
    variaciones = [
        e for e in estados_set if estado.lower() in e.lower() and e != estado
    ]
    if variaciones:
        print(f"   Estado '{estado}' tiene variaciones: {variaciones}")

# 7. Prueba final: simular lo que ve Streamlit
print("\n7. SIMULACIÓN DE STREAMLIT SELECTBOX:")
print("   Valor que se pasaría a st.selectbox:")

# Opción A (la problemática)
opcionA = sorted(df_ventas["Estado"].dropna().unique())
print(f"\n   Opción A (actual): tipo={type(opcionA)}, len={len(opcionA)}")
if opcionA:
    print(f"   Primeros 3: {opcionA[:3]}")

# Opción B (sugerida)
opcionB = sorted(df_ventas["Estado"].dropna().astype(str).unique().tolist())
print(f"\n   Opción B (strings puros): tipo={type(opcionB)}, len={len(opcionB)}")
if opcionB:
    print(f"   Primeros 3: {opcionB[:3]}")

# 8. Verificar si hay numpy strings vs python strings
print("\n8. DIFERENCIA NUMPY STRING VS PYTHON STRING:")
if estados_unique.dtype == "object":
    primer_estado = estados_unique[0]
    print(f"   Tipo exacto del primer estado: {type(primer_estado)}")
    print(f"   Es numpy.str_? {isinstance(primer_estado, np.str_)}")
    print(f"   Es str? {isinstance(primer_estado, str)}")

print("\n" + "=" * 80)
print("RECOMENDACIÓN:")
print("Usar: sorted(df['Estado'].dropna().astype(str).unique().tolist())")
print("=" * 80)
