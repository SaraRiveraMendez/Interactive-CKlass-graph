import pandas as pd

# Cargar archivo pesado
df = pd.read_csv("C:/Users/rsara/Downloads/consolidado_negado_nacional.csv")

# Quedarnos solo con columnas necesarias
df = df[["Sem_ISO", "ProductoID", "estacion", "Estado"]]

# Agregar
df_grouped = df.groupby(
    ["Sem_ISO", "ProductoID", "estacion"]
)["Cantidad"].sum().reset_index()

# Guardar versión ligera
df_grouped.to_csv("ventas_light_n.csv", index=False)

print("Archivo reducido creado.")
