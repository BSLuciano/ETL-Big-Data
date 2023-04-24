from scripts.EDA_functions import *


root_folder = "hdfs://namenode:9000/raw_data/parquet_data"
dict_df = extract_parquet(root_folder)



# --------------------------------------------------------------------------------------------------------

# Vista general de cada DataFrame
print("\t\t\t\tVISTA GENERAL\n")
general_view(dict_df)

# --------------------------------------------------------------------------------------------------------

# Dimension DF
print("\t\t\t\tDIMENSION DF\n")
shape_df(dict_df)

# --------------------------------------------------------------------------------------------------------

# Nombre de las columnas
print("\t\t\t\tNOMBRE COLUMNAS\n""")
col_name(dict_df)

# --------------------------------------------------------------------------------------------------------

# ANALIZAR TIPO DE DATO
print("\t\t\t\tTIPO DE DATO\n")
schema_df(dict_df)

# --------------------------------------------------------------------------------------------------------


# VALORES NULOS
print("\t\t\t\tVALORES NULOS\n")
null_count(dict_df)


# --------------------------------------------------------------------------------------------------------

# REGISTROS DUPLICADOS
print("\t\t\t\tREGISTROS DUPLICADOS\n")
duplicates_count(dict_df)

# --------------------------------------------------------------------------------------------------------

# CARACTERES ESPECIALES
print("\t\t\t\tCARACTERES ESPECIALES\n")
aux = ["mes_nombre", "dia_nombre", "DESCRIPCION", "Provincia", "Localidad", "Direccion", "Sucursal", "departamen",
"Country", "State", "City", "Address", "Nombre", "Cargo", "Sector", "Sucursal", "Nombre", "Apellido", "Tipo",
"Concepto", "Descripcion", "col10", "Nombre_y_Apellido", "Domicilio", "Telefono"]

special_char(dict_df, aux)


# -------------------------------------------------------------------------------------------------------

# DETECCIÓN DATOS A NORMALIZAR
print("\t\t\t\tDETECCIÓN DATOS A NORMALIZAR\n")
list_zones = ["Provincia", "Localidad", "City", "State", "Country", "departamen"]

unique_zones(dict_df, list_zones)

# -------------------------------------------------------------------------------------------------------

# DETECCIÓN DE OUTLIERS

# Nota: Para el df Producto se debe modificar el nombre de la columna ' Precio ' por 'Precio' de lo contrario
# al aplicar la función se genera un error.

for key in dict_df.keys():
    if 'Precio' in key:
        dict_df[key] = dict_df[key].withColumnRenamed(' Precio ', 'Precio')

detect_outliers(dict_df, 'Producto', 'Tipo', 'Precio')
detect_outliers(dict_df, 'Empleado', 'Cargo', 'Salario')
detect_outliers(dict_df, 'Gasto', 'IdTipoGasto', 'Monto')
detect_outliers(dict_df, 'Venta', 'IdProducto', 'Precio')
detect_outliers(dict_df, 'Venta', 'IdProducto', 'Cantidad')
