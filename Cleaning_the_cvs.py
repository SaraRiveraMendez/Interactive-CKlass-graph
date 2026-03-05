import pandas as pd
import os
from datetime import datetime


def limpiar_nombre_duplicado(texto):
    """
    Detecta y limpia nombres duplicados/triplicados.
    Ej: 'ChiapasChiapas' → 'Chiapas'
        'GuanajuatoGuanajuatoGuanajuato' → 'Guanajuato'
    """
    if pd.isna(texto) or texto == "nan":
        return texto

    texto = str(texto).strip()

    # Intentar detectar repeticiones
    longitud = len(texto)

    # Probar divisores desde 2 hasta 10 (para nombres duplicados hasta 10 veces)
    for n in range(2, 11):
        if longitud % n == 0:
            tam_segmento = longitud // n
            segmento = texto[:tam_segmento]

            # Verificar si el texto es la repetición exacta del segmento
            if segmento * n == texto:
                return segmento

    return texto


def limpiar_archivo_csv(ruta_archivo):
    """
    Lee un CSV, limpia nombres duplicados y sobrescribe el archivo.
    """
    print(f"\n{'='*80}")
    print(f"Procesando: {ruta_archivo}")
    print(f"{'='*80}")

    # Crear backup
    backup_path = ruta_archivo.replace(
        ".csv", f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

    # Leer archivo
    print(f"📖 Leyendo archivo...")
    df = pd.read_csv(ruta_archivo, encoding="utf-8-sig")
    print(f"   - Filas originales: {len(df)}")
    print(f"   - Columnas: {df.columns.tolist()}")

    # Crear backup
    print(f"\n💾 Creando backup en: {backup_path}")
    df.to_csv(backup_path, index=False, encoding="utf-8-sig")

    # Estadísticas ANTES
    print(f"\n📊 ANTES DE LIMPIAR:")
    if "Estado" in df.columns:
        estados_unicos_antes = df["Estado"].nunique()
        print(f"   - Estados únicos: {estados_unicos_antes}")
        # Mostrar duplicados
        estados_con_duplicados = [
            e for e in df["Estado"].unique() if len(str(e)) > 0 and str(e)[0].isalpha()
        ]
        duplicados = [
            e for e in estados_con_duplicados if limpiar_nombre_duplicado(e) != e
        ]
        if duplicados:
            print(f"   - Estados con duplicación detectada: {len(duplicados)}")
            print(f"   - Ejemplos: {duplicados[:5]}")

    if "Sucursal_Nombre" in df.columns:
        sucursales_unicas_antes = df["Sucursal_Nombre"].nunique()
        print(f"   - Sucursales únicas: {sucursales_unicas_antes}")
        # Mostrar duplicados
        sucursales_con_duplicados = [
            s for s in df["Sucursal_Nombre"].unique() if len(str(s)) > 0
        ]
        duplicados_suc = [
            s for s in sucursales_con_duplicados if limpiar_nombre_duplicado(s) != s
        ]
        if duplicados_suc:
            print(f"   - Sucursales con duplicación detectada: {len(duplicados_suc)}")
            print(f"   - Ejemplos: {duplicados_suc[:5]}")

    # Limpiar
    print(f"\n🧹 LIMPIANDO DATOS...")
    if "Estado" in df.columns:
        print(f"   - Limpiando columna 'Estado'...")
        df["Estado"] = df["Estado"].apply(limpiar_nombre_duplicado)

    if "Sucursal_Nombre" in df.columns:
        print(f"   - Limpiando columna 'Sucursal_Nombre'...")
        df["Sucursal_Nombre"] = df["Sucursal_Nombre"].apply(limpiar_nombre_duplicado)

    # Limpieza adicional de espacios
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # Estadísticas DESPUÉS
    print(f"\n✅ DESPUÉS DE LIMPIAR:")
    if "Estado" in df.columns:
        estados_unicos_despues = df["Estado"].nunique()
        print(f"   - Estados únicos: {estados_unicos_despues}")
        print(
            f"   - Reducción: {estados_unicos_antes - estados_unicos_despues} estados duplicados eliminados"
        )

    if "Sucursal_Nombre" in df.columns:
        sucursales_unicas_despues = df["Sucursal_Nombre"].nunique()
        print(f"   - Sucursales únicas: {sucursales_unicas_despues}")
        print(
            f"   - Reducción: {sucursales_unicas_antes - sucursales_unicas_despues} sucursales duplicadas eliminadas"
        )

    # Sobrescribir archivo
    print(f"\n💾 Sobrescribiendo archivo original...")
    df.to_csv(ruta_archivo, index=False, encoding="utf-8-sig")
    print(f"   ✅ Archivo actualizado: {ruta_archivo}")

    return df


# =============================
# MAIN
# =============================
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("LIMPIEZA DE ARCHIVOS CSV - ELIMINAR NOMBRES DUPLICADOS")
    print("=" * 80)

    archivos = ["data/ventas_lights_final.csv", "data/negados_lights_final.csv"]

    for archivo in archivos:
        if os.path.exists(archivo):
            try:
                df_limpio = limpiar_archivo_csv(archivo)
            except Exception as e:
                print(f"\n❌ ERROR procesando {archivo}: {e}")
        else:
            print(f"\n⚠️  Archivo no encontrado: {archivo}")

    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO")
    print("=" * 80)
    print("\nBackups creados con timestamp en el mismo directorio.")
    print("Los archivos originales han sido sobrescritos con datos limpios.")
    print(
        "\n⚠️  IMPORTANTE: Reinicia tu aplicación Streamlit para cargar los datos limpios."
    )
    print("=" * 80 + "\n")
