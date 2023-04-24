from scripts.ETL_functions import *
from pyspark.sql.types import StructType, StringType, IntegerType, FloatType, DateType


# ------------------------------------------------------------------------------------------------------


# EXTRACCION

root_folder = "hdfs://namenode:9000/raw_data/parquet_data/"
dict_df = extract_parquet(root_folder)


# ------------------------------------------------------------------------------------------------------

# TRANSFORMACION:

# Eliminar registros duplicados
drop_duplicates(dict_df)


# Eliminar columnas vacías
null_column(dict_df)


# Normalización de Columnas

# Diccionario donde la key hace referencia al nombre del df y su contenido son tuplas con las correcciones a aplicar,
# es decir, cada tupla está compuesta por el nombre actual de la columna y el nombre por el cual se cambiará.

dict_standardization = {"Cliente": [("ID", "IdCliente"), ("Nombre_y_Apellido", "NombreCompleto"), ("X", "Longitud"), ("Y", "Latitud")],
                        "TiposDeGasto": [("Monto_Aproximado", "MontoAproximado")],
                        "Producto": [("ID_PRODUCTO", "IdProducto"), (" Precio ", "Precio")],
                        "Empleado": [("ID_empleado", "IdEmpleado")],
                        "Proveedor": [("IDProveedor", "IdProveedor"), ("Address", "Direccion"), ("City", "Ciudad"), ("State", "Provincia"), ("Country", "Pais"), ("departamen", "Localidad")],
                        "Sucursal": [("ID", "IdSucursal")],
                        "CanalDeVenta": [("CODIGO", "IdCanalVenta"), ("DESCRIPCION", "Descripcion")],
                        "Venta": [("Fecha_Entrega", "FechaEntrega")],
                        "Calendario": [("fecha", "Fecha"), ("anio", "Anio"), ("mes", "Mes"), ("dia", "Dia"), ("trimestre", "Trimestre"), ("semana", "Semana"), ("dia_nombre", "DiaNombre"), ("mes_nombre", "MesNombre")]}

standardization_df(dict_standardization, dict_df)

# Corrección valores atípicos
outliers_correction(dict_df, 'Venta', 'IdProducto', 'Precio')
outliers_correction(dict_df, 'Venta', 'IdProducto', 'Cantidad')

# Corrección de valores nulos en columnas numéricas
columns_int = ['Cantidad']
columns_float = ['Precio', 'Salario', 'Monto_promedio']

missing_value_num(dict_df, 'Venta', 'IdProducto', 'Cantidad', columns_int, columns_float)
missing_value_num(dict_df, 'Venta', 'IdProducto', 'Precio', columns_int, columns_float)


# Corrección de caracteres especiales, en este caso se reemplazan los " " por None
remove_whitespace_columns(dict_df, 'Cliente')
remove_whitespace_columns(dict_df, 'Producto')
remove_whitespace_columns(dict_df, 'Proveedor')

# Corrección de sintaxis de valores del tipo "Float"
replace_commas_with_dots(dict_df, "Cliente", "Longitud")
replace_commas_with_dots(dict_df, "Cliente", "Latitud")
replace_commas_with_dots(dict_df, "Producto", "Precio")
replace_commas_with_dots(dict_df, "Empleado", "Salario")
replace_commas_with_dots(dict_df, "Sucursal", "Longitud")
replace_commas_with_dots(dict_df, "Sucursal", "Latitud")


# Normalización de datos
list_data = ["Buenos Aires ", " Buenos Aires", "Buenos Aires", "Ciudad de Buenos Aires"]
norm_value = "Buenos Aires"

norm_data(dict_df, "Cliente", "Provincia", list_data, norm_value)

list_data = ["Cordoba", "Córdoba"]
norm_value = "Córdoba"

norm_data(dict_df, "Sucursal", "Provincia", list_data, norm_value)

list_data = ["B. Aires", "B.Aires", "Bs As", "Bs.As. ", "Buenos Aires", "C deBuenos Aires",
						 "CABA", "Ciudad de Buenos Aires", "Pcia Bs AS", "Prov de Bs As.", "Provincia de Buenos Aires"]
norm_value = "Buenos Aires"

norm_data(dict_df, "Sucursal", "Provincia", list_data, norm_value)


list_data = ["CABA", "Cap.   Federal", "Cap. Fed." ,"CapFed" ,"Capital", "Capital Federal",
 						 "Cdad de Buenos Aires", "Ciudad de Buenos Aires"]
norm_value = "Capital Federal"

norm_data(dict_df, "Sucursal", "Localidad", list_data, norm_value)


list_data = ["Cordoba", "Coroba", "Córdoba"]
norm_value = "Córdoba"

norm_data(dict_df, "Sucursal", "Localidad", list_data, norm_value)


# Cambiar el tipo de dato por columna

dict_types = {
    'Calendario': [
        ("IdFecha", IntegerType()),
        ("Fecha", DateType()),
        ("Anio", IntegerType()),
        ("Mes", IntegerType()),
        ("Dia", IntegerType()),
        ("Trimestre", IntegerType()),
        ("Semana", IntegerType()),
        ("DiaNombre", StringType()),
        ("MesNombre", StringType())
        ],
    'CanalDeVenta': [
        ("IdCanalVenta", IntegerType()),
        ("Descripcion", StringType())],
    'Cliente': [
        ("IdCliente", IntegerType()),
        ("Provincia", StringType()),
        ("NombreCompleto", StringType()),
        ("Domicilio", StringType()),
        ("Telefono", StringType()),
        ("Edad", IntegerType()),
        ("Localidad", StringType()),
        ("Longitud", FloatType()),
        ("Latitud", FloatType())
        ],
    'Compra': [
        ("IdCompra", IntegerType()),
        ("Fecha", DateType()),
        ("IdProducto", IntegerType()),
        ("Cantidad", IntegerType()),
        ("Precio", FloatType()),
        ("IdProveedor", IntegerType())
    ],
    'Empleado': [
        ("IdEmpleado", IntegerType()),
        ("Apellido", StringType()),
        ("Nombre", StringType()),
        ("Sucursal", StringType()),
        ("Sector", StringType()),
        ("Cargo", StringType()),
        ("Salario", FloatType())
    ],
    'Gasto': [
        ("IdGasto", IntegerType()),
        ("IdSucursal", IntegerType()),
        ("IdTipoGasto", IntegerType()),
        ("Fecha", DateType()),
        ("Monto", FloatType())
    ],
    'Producto': [
        ("IdProducto", IntegerType()),
        ("Concepto", StringType()),
        ("Tipo", StringType()),
        ("Precio", FloatType())
    ],
    'Proveedor': [
        ("IdProveedor", IntegerType()),
        ("Nombre", StringType()),
        ("Direccion", StringType()),
        ("Ciudad", StringType()),
        ("Provincia", StringType()),
        ("Pais", StringType()),
        ("Localidad", StringType())
    ],
    'Sucursal': [
        ("IdSucursal", IntegerType()),
        ("Sucursal", StringType()),
        ("Direccion", StringType()),
        ("Localidad", StringType()),
        ("Provincia", StringType()),
        ("Latitud", FloatType()),
        ("Longitud", FloatType())
    ],
    'TiposDeGasto': [
        ("IdTipoGasto", IntegerType()),
        ("Descripcion", StringType()),
        ("MontoAproximado", IntegerType())
    ],
    'Venta': [
        ("IdVenta", IntegerType()),
        ("Fecha", DateType()),
        ("FechaEntrega", DateType()),
        ("IdCanal", IntegerType()),
        ("IdCliente", IntegerType()),
        ("IdSucursal", IntegerType()),
        ("IdEmpleado", IntegerType()),
        ("IdProducto", IntegerType()),
        ("Precio", FloatType()),
        ("Cantidad", IntegerType())
    ]
        }

    
type_data(dict_df, dict_types)



# BACK
path = "hdfs://namenode:9000/transformed_data"
save_data(dict_df, path)