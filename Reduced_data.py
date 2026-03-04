import pandas as pd

# Cargar archivo pesado
df = pd.read_csv("C:/Users/rsara/Downloads/consolidado_ventas_nacional.csv")

# Quedarnos solo con columnas necesarias
df = df[["Sem_ISO", "ProductoID", "estacion", "Estado", "Cantidad", "Sucursal_Nombre"]]

# Agregar
df_grouped = (
    df.groupby(["Sem_ISO", "ProductoID", "estacion", "Cantidada", "Sucursal_Nombre"])[
        "Estado"
    ]
    .sum()
    .reset_index()
)

# Guardar versión ligera
df_grouped.to_csv("ventas_light_final.csv", index=False)


print("Archivo reducido creado.")
