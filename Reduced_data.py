import pandas as pd

# Cargar archivo pesado
df = pd.read_csv("C:/Users/rsara/Downloads/consolidado_negado_nacional.csv")

# Quedarnos solo con columnas necesarias
df = df[["Sem_ISO", "ProductoID", "estacion", "Estado", "Negados"]]

# Agregar
df_grouped = df.groupby(
    ["Sem_ISO", "ProductoID", "estacion", "Negados"]
)["Estado"].sum().reset_index()

# Guardar versión ligera
df_grouped.to_csv("ventas_light_n2.csv", index=False)

print("Archivo reducido creado.")
