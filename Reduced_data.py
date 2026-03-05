import pandas as pd

# Cargar archivo pesado
df = pd.read_csv("C:/Users/rsara/Downloads/consolidado_negado_nacional.csv")

# Quedarnos solo con columnas necesarias
df = df[
    [
        "Sem_ISO",
        "ProductoID",
        "estacion",
        "Estado",
        "Negados",
        "Sucursal_Nombre",
        "Año",
    ]
]

# Agregar
df_grouped = (
    df.groupby(
        ["Sem_ISO", "ProductoID", "estacion", "Negados", "Sucursal_Nombre", "Año"]
    )["Estado"]
    .sum()
    .reset_index()
)

# Guardar versión ligera
df_grouped.to_csv("negados_lights_final.csv", index=False)


print("Archivo reducido creado.")
