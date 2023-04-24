from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name
import os
from pyspark.sql.functions import col, count, avg, round
from pyspark.sql.functions import percentile_approx, desc, dense_rank, when, lit, regexp_replace
from pyspark.sql.window import Window
from pyspark.sql.types import IntegerType, FloatType



spark = SparkSession.builder \
    .appName("ETL") \
    .getOrCreate()


# ----------------------------------------------------------------------------------------------------------


#EXTRACCIÓN

def extract_parquet(root_folder: str) -> None:
    dictionary_df = {}
    for folder in spark.read.format("parquet").option("recursiveFileLookup", "true").option("header", "true").load(root_folder).select(input_file_name()).distinct().collect():
        file_path = folder[0]
        # Obtener el nombre del archivo desde el path
        file_name = os.path.basename(os.path.dirname(file_path))
        df = spark.read.option("compression.codec", "snappy").parquet(file_path)
        dictionary_df[file_name] = df
    return dictionary_df

# ----------------------------------------------------------------------------------------------------------


# TRANSFORMACIÓN

# Registros duplicados

def drop_duplicates(dictionary_df: dict) -> None:
    for key in dictionary_df.keys():
        df = dictionary_df[key]
        df = df.dropDuplicates()
        dictionary_df[key] = df
    return dictionary_df


# Columnas vacías

# La función recorre todos los df contenidos en un diccionario, detecta las columnas que presentan todos
# sus elementos nulos, las agrega a una lista y luego elimina todas las columnas contenidas en la lista del df.
# Por último, actualiza el contenido del diccionario.
def null_column(dictionary_df: dict) -> None:
    # Iterar sobre cada clave del diccionario de DataFrames
    for key in dictionary_df.keys():
        # Obtener el DataFrame correspondiente a la clave actual
        df = dictionary_df[key]
        # Crear una lista de las columnas que tienen todos los valores nulos
        null_cols = [c for c in df.columns if df.where(col(c).isNotNull()).count() == 0]
        # Eliminar las columnas con todos los valores nulos del DataFrame
        df = df.drop(*null_cols)
        # Actualizar el diccionario de DataFrames con el DataFrame modificado
        dictionary_df[key] = df
    return dictionary_df


# Normalización de Columnas

#  La función recorre cada dataframe en el diccionario y verifica si su nombre coincide con alguno en
#  la lista de dataframes que deben ser estandarizados. Si es así, recorre la lista de columnas que
#  deben ser estandarizadas y las renombra en el dataframe correspondiente. Finalmente, actualiza el
#  valor del dataframe en el diccionario.


def standardization_df(dict_standardization: dict, dictionary_df: dict) -> None:
    for key, df in dictionary_df.items():
        for name in dict_standardization:
            if key == name:
                for old_name, new_name in dict_standardization[name]:
                    df = df.withColumnRenamed(old_name, new_name)
                    dictionary_df[key] = df
    return dictionary_df


# Valores Atípicos

#La función "outliers_correction" toma como entrada un diccionario (dictionary_df) que contiene DataFrames (df)
# y realiza una corrección de valores atípicos en el DataFrame especificado por la clave (key).
# La corrección se realiza para cada grupo definido por la columna segment_column y utilizando los valores
# de la columna value_column.
# Para realizar la corrección, se calculan los cuartiles Q1 y Q3 para cada grupo utilizando la función
# percentile_approx. A partir de estos cuartiles, se calculan los límites BI y BS para cada grupo utilizando
# el rango intercuartílico (IQR). Luego, se calcula la moda real para cada grupo contando las frecuencias
# de los valores y seleccionando la moda. Finalmente, se reemplazan los valores atípicos por la moda
# correspondiente para cada grupo.


def outliers_correction(dictionary_df: dict, key: str, segment_column: str, value_column: str) -> None:
    # Obtener el DataFrame correspondiente a la clave especificada
    df = dictionary_df[key]
    # Calcular los cuartiles Q1 y Q3 para cada grupo
    q1 = percentile_approx(value_column, 0.25).over(Window.partitionBy(segment_column))
    q3 = percentile_approx(value_column, 0.75).over(Window.partitionBy(segment_column))
    # Calcular los límites BI y BS para cada grupo utilizando el rango intercuartílico (IQR)
    iqr = q3 - q1
    bi = q1 - 1.5 * iqr
    bs = q3 + 1.5 * iqr
    # Calcular la moda real para cada grupo
    # Contar las frecuencias de los valores y seleccionar la moda
    frecuencias_df = df.groupBy(segment_column, value_column).agg(count('*').alias('frecuencia'))
    ventana = Window.partitionBy(segment_column).orderBy(desc('frecuencia'))
    moda_real_df = frecuencias_df \
        .withColumn('rank', dense_rank().over(ventana)) \
        .filter(col('rank') == 1) \
        .drop('frecuencia', 'rank') \
        .withColumnRenamed(value_column, 'moda')
    # Reemplazar los valores atípicos por la moda correspondiente para cada grupo
    corrected_df = df.join(moda_real_df, [segment_column], 'inner') \
                     .withColumn('outlier', (col(value_column) < bi) | (col(value_column) > bs)) \
                     .withColumn(value_column, when(col('outlier'), col('moda')).otherwise(col(value_column))) \
                     .drop('outlier', 'moda')
    # Actualizar el DataFrame en el diccionario de entrada
    dictionary_df[key] = corrected_df
    # Retornar el DataFrame corregido
    return dictionary_df



# Valores Nulos

# La función "missing_value_num" tiene el objetivo de imputar valores faltantes en un DataFrame que se encuentra dentro de un diccionario.
# Recibe como parámetros el diccionario que contiene los DataFrames, la clave del DataFrame que se desea imputar, las columnas de segmentación y valor,
# y dos listas que contienen las columnas que deben tratarse como enteras o flotantes.
# La función comienza rellenando los valores faltantes en la columna especificada con ceros y cambiando el tipo de dato a entero o flotante según corresponda.
# Luego, calcula la imputación correspondiente para cada grupo en base a la columna de segmentación y el tipo de dato de la columna con valores faltantes.
# La imputación se calcula como el promedio de los valores no faltantes de la columna para cada grupo.
# Posteriormente, une el DataFrame original con el DataFrame de imputaciones, se reemplazan los valores faltantes por la imputación correspondiente
# para cada grupo y se actualiza el DataFrame en el diccionario de entrada. Finalmente, la función devuelve el diccionario actualizado.

def missing_value_num(dictionary_df: dict, key: str, segment_column: str,
                    value_column: str, list_columns_int: list, list_columns_float: list) -> None:
    # Obtener el DataFrame correspondiente a la clave especificada
    df = dictionary_df[key]
    if value_column in list_columns_int:
        # rellenar los valores nulos con 0
        df = df.withColumn(value_column, when(col(value_column).isNull(), 0).otherwise(col(value_column)))
        # cambiar el tipo de dato a integer
        df = df.withColumn(value_column, col(value_column).cast(IntegerType()))
    elif value_column in list_columns_float:
        # rellenar los valores nulos con 0
        df = df.withColumn(value_column, when(col(value_column).isNull(), 0).otherwise(col(value_column)))
        # Si la columna contiene comas, reemplazarlas por puntos
        if df.filter(col(value_column).like("%,%")).count() > 0:
            df = df.withColumn(value_column, regexp_replace(value_column, ",", "."))
        df = df.withColumn(value_column, col(value_column).cast(FloatType()))
    # Calcular la imputación correspondiente para cada grupo
    if value_column in list_columns_int:
        imputation_df = df.filter(col(value_column) != 0) \
                 .groupBy(segment_column) \
                 .agg(avg(col(value_column)) \
                 .alias('imputation'))
        imputation_df = imputation_df.withColumn('imputation', (round(imputation_df['imputation'], 0)).cast(IntegerType()))
    elif value_column in list_columns_float:
        imputation_df = df.filter(col(value_column) != 0) \
                 .groupBy(segment_column) \
                 .agg(avg(col(value_column)) \
                 .alias('imputation'))
        imputation_df = imputation_df.withColumn('imputation', (round(imputation_df['imputation'], 2)).cast(FloatType()))
    # Unir el DataFrame original con el DataFrame de imputaciones
    joined_df = df.join(imputation_df, on=segment_column, how="left")
    # Reemplazar los valores faltantes por la imputación correspondiente para cada grupo
    corrected_df = joined_df.withColumn(value_column, when(col(value_column)==0, col('imputation')).otherwise(col(value_column))) \
                     .drop('imputation')
    # Actualizar el DataFrame en el diccionario de entrada
    dictionary_df[key] = corrected_df
    # Retornar el DataFrame corregido
    return dictionary_df


#### En las columnas donde los valores faltantes no pueden corregirse con una medida de tendencia central, ya que el resultado que se obtendría
#### no sería correcto, decidí dejar los valores None presentes, ya que no habrá problemas para dar el formato necesario a las columnas.
#### Estas columnas son las referentes a nombres, localidades, coordenadas geofráficas y fechas.


# Caracteres especiales (" ")

# Ante la presencia de valores iguales a " " la función los reemplaza por None

def remove_whitespace_columns(dictionary_df: dict, key: str) -> None:
    df = dictionary_df[key]
    for c in df.columns:
        df = df.withColumn(c, when(col(c) == " ", lit(None)).otherwise(col(c)))
        dictionary_df[key] = df
    return dictionary_df


# Error de sintaxis en valores del tipo float, ya que se ha utilizado la "," decimal en vez del "."

def replace_commas_with_dots(dictionary_df: dict, key: str, column: str) -> None:
    df = dictionary_df[key]
    df = df.withColumn(column, regexp_replace(col(column), ",", "."))
    dictionary_df[key] = df
    return dictionary_df


# Normalización de datos

# La funciónn recibe como parámetros un diccionario de df, la clave referente a al DF, el nombre de la columna
# que presenta los datos a normalizar, una lista que contiene todos los elementos distintos que hacen referencia
# a un mismo elemento y la estandarización a aplicar.

def norm_data(dictionary_df: dict, key: str, value_column: str, list_data: list, norm_value: str):
    df = dictionary_df[key]
    df = df.withColumn(value_column, when(col(value_column).isin(list_data), norm_value).otherwise(col(value_column)))
    dictionary_df[key] = df
    return dictionary_df



# ----------------------------------------------------------------------------------------------------------

#### IMPORTANTE: CASTEAR LOS TIPOS DE DATOS

# El objetivo de esta función es darle el tipo de dato correcto a cada columna de cada DF para evitar errores
# al crear la base de datos.
# La función recibe dos diccionarios como parámetros, uno tiene como valores dataframes y el otro listas de tuplas,
# donde cada tupla está compuesta por el nombre de una columna y el tipo de dato que debe tener. Los diccionarios
# presentan las mismas claves que refieren al nombre del df.
# La función itera sobre cada DataFrame en el diccionario y busca si la clave del DataFrame coincide con alguna clave
# en el diccionario de tipos. Si hay una coincidencia, itera sobre las columnas y tipos de datos especificados y cambia
# el tipo de dato de la columna correspondiente en el DataFrame.
# Actualiza el df en el diccionario de entrada y continua con el df siguiente en el diccionario.  Finalmente, la función
# devuelve el diccionario actualizado con los tipos de datos modificados.

def type_data(dictionary_df: dict, dict_types: dict) -> None:
    for key, df in dictionary_df.items():
        for name in dict_types:
            if key == name:
                for column, type in dict_types[name]:
                    for column, type in dict_types[name]:
                        df = df.withColumn(column, col(column).cast(type))
                        dictionary_df[key] = df
    return dictionary_df


# BACK

# Cargo los archivos transformados en el datalake, los cuales seran utilizados para creear
# un datawarhouse con Hive.

def save_data(dictionary_df: dict, root_folder: str) -> None:
    for key in dictionary_df.keys():
        df = dictionary_df[key]
        df.write.mode('overwrite').format("parquet").option("compression", "snappy").save(f"{root_folder}/{key}")