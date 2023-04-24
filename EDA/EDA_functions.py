from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name
import os, re
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, DateType
from pyspark.sql.functions import isnan, col, count, regexp_extract, expr, regexp_replace



spark = SparkSession.builder \
    .appName("EDA") \
    .getOrCreate()


# EXTRACCIÓN


def extract_parquet(root_folder: str) -> None:
    dictionary_df = {}
    for folder in spark.read.format("parquet").option("recursiveFileLookup", "true").option("header", "true").load(root_folder).select(input_file_name()).distinct().collect():
        file_path = folder[0]
        # Obtener el nombre del archivo desde el path
        file_name = os.path.basename(os.path.dirname(file_path))
        print(file_name)
        df = spark.read.option("compression.codec", "snappy").parquet(file_path)
        dictionary_df[file_name] = df
    return dictionary_df

# --------------------------------------------------------------------------------------------------------


# Vista general de cada DataFrame

# La función recibe como argumento un diccionario de df e imprime los primeros 10 elementos de cada uno.

def general_view(dictionary_df: dict) -> None:
    for key in dictionary_df.keys():
        print(key)
        dictionary_df[key].show(10)


# --------------------------------------------------------------------------------------------------------


# DIMENSIÓN DF

def shape_df(dictionary_df: dict) -> None:
    for key in dictionary_df.keys():
        df = dictionary_df[key]
        num_col = len(df.columns)
        num_row = df.count()
        print(f"DF: {key} => Dimension: {num_row} x {num_col}")


# --------------------------------------------------------------------------------------------------------


# NOMBRE COLUMNAS

def col_name(dictionary_df: dict) -> None:
    for key in dictionary_df.keys():
        df = dictionary_df[key]
        list_col = df.columns
        print(f"DF: {key} => Columnas: {list_col}")


# --------------------------------------------------------------------------------------------------------



# ANALIZAR TIPO DE DATO

# Este paso es para verificar si los schemas fueron aplicados correctamente

def schema_df(dictionary_df: dict) -> None:
    for key in dictionary_df.keys():
        print(f"Schema for {key}")
        dictionary_df[key].printSchema()

# Si el resultado del schema de los DF difiere no corresponde al que debería tener asigando,
# se deberá analizar el por qué para poder aplicar las correciones necesarias, esto puede ser
# provocado por: valores nulos, caracteres especiales, espacios, etc.


# --------------------------------------------------------------------------------------------------------


# VALORES NULOS

# La función busca valores nulos dentro de cada columna del conjunto de df e indica la cantidad presente
# de los mismos dando el nombre de archivo al que refiere el df (key del diccionario), nombre de la columna
# analizada y la cantidad en porcentaje de valores nulos. El argumento es un dicconario de dataframes.

def null_count(dict_df):
    for key in dict_df.keys():
        df = dict_df[key]
        for col_name in df.columns:
            null_count = df.filter(isnan(col(col_name)) | col(col_name).isNull()).count()
            null_count = round(null_count / df.count()*100, 2)
            if null_count > 0:
                print(f"DF: {key}, Columna: {col_name} => Valores Nulos: {null_count} %")


# Filtrar filas por nulos, obteniendo todas aquellas que presenten 2 o más.
# El objetivo de esto es detectar aquellos registros que presenes problemas por los
# que no puedan ser imputados, por ejemplo: (cuando no se presente ni precio ni cantidad por producto en una venta )

def process_row(row):
    null_values = [value for value in row if value is None]
    if len(null_values) >= 2:
        return row
    else:
        return None


def max_null(dictionary_df):
    new_dfs = {}
    for key in dictionary_df.keys():
        df = dictionary_df[key]
        filtered_rows = list(filter(lambda x: x is not None, df.rdd.map(process_row).collect()))
        new_df = spark.createDataFrame(filtered_rows, df.schema)
        new_dfs[key] = new_df
    for key in new_dfs.keys():
        df = new_dfs[key]
        if df.count() > 0:
            print("DF: {}, filas detectadas: {}".format(key, df.count()))
            df.show(df.count())


# --------------------------------------------------------------------------------------------------------


# REGISTROS DUPLICADOS

# La función cuenta la cantidad de registros duplicados en los dataframes contenidos en un diccionario.
# Para cada df, cuenta la cantidad de registros duplicados y lo muestra junto con el nombre del df.

def duplicates_count(dict_df: dict) -> None:
    for key in dict_df.keys():
        for df in dict_df[key]:
            df = dict_df[key]
            duplicates_count = df.groupBy(df.columns).count().filter("count > 1").count()
        print(f"DataFrame: {key} => Registros Duplicados: {duplicates_count} \n")


# --------------------------------------------------------------------------------------------------------


# CARACTERES ESPECIALES

# Esta función cuenta la cantidad de caracteres especiales en columnas de un conjunto de df contenidos
# en un diccionario. Toma como argumento un diccionario de dataframes y una lista que contiene el nombre de
# las columnas que se excluyen de la búsqueda. En caso de encontrar caracteres especiales indica la cantidad
# de apariciones de cada uno de ellos ordenados por la frecuencia de aparición.

def special_char(dictionary_df: dict, list_col: list) -> None:
    for key in dictionary_df.keys():
        df = dictionary_df[key]
        for col_name in df.columns:
            if col_name not in list_col:
                special_chars_count = (
                    df.select(regexp_extract(col(col_name), r"[^0-9.-]+", 0).alias("special_chars"))
                    .filter(col("special_chars") != "")
                    .groupBy("special_chars")
                    .agg(count("*").alias("count"))
                    .orderBy(col("count").desc())
                )
                special_chars_count_list = special_chars_count.collect()
                count_sc = special_chars_count_list[0]['count'] if special_chars_count_list else 0
                if count_sc > 0:
                    print(key, col_name)
                    special_chars_count.show()


# -------------------------------------------------------------------------------------------------------

# DETECCIÓN DATOS A NORMALIZAR

# Esta función busca los elementos únicos de las columnas referentes a zonas de cada df con el fin de
# detectar todos aquellos elementos distintos que refieren al mismo lugar, toma como argumento un diccionario
# compuesto por dataframes y una lista que contiene el nombre de las columnas a utilizar.

def unique_zones(dictionary_df: dict, list: list) -> None:
    for key in dictionary_df.keys():
         df = dictionary_df[key]
         for col in df.columns:
             if col in list:
                 print(f"DF: {key}, COL: {col} => elementos únicos: {df.select(col).distinct().count()}")
                 df.select(col).distinct().orderBy(col).show(600, truncate=False)


# -------------------------------------------------------------------------------------------------------

# DETECCIÓN DE OUTLIERS

# Buscaré valores atípicos en los DF: ['Producto', 'Empleado', 'Gasto', 'Venta']
# en las columnas referidas a valores monetarios o cantidades.
# En algunos casos la diferencia entre Q1 y Q3 es amplia, es decir, el rango intercuartílico es
# presenta un valor alto, y además el Q1 se encuentra cercano a 0, lo que produce que BI es un valor
# negativo, como estoy trabajando con precios y cantidades no tiene sentido que sean menores a 0, por
# lo tanto indique que en esos caso BI sea 0 de manera que si se presentara un valor negativo sea detectado
# como atípico. Esto no permitirá detectar los valores que estén en 0, pero al momento de corregir nulos lo
# tendré en cuenta indicando que en caso de existir se los remplace con una medida de tendencia central.

def detect_outliers(dictionary_df: dict, key: str, segmentation: str, column: str) -> None:
    # Obtener el dataframe correspondiente al key indicado en el diccionario
    df = dictionary_df[key]
    # Filtrar los registros en los que la columna indicada no es nula
    df = df.filter(col(column).isNotNull())
    # Si la columna contiene comas, reemplazarlas por puntos
    if df.filter(col(column).like("%,%")).count() > 0:
        df = df.withColumn(column, regexp_replace(column, ",", "."))
    # Convertir la columna a tipo double
    df = df.withColumn(column, col(column).cast("double"))
    # Agrupar el DataFrame por la variable de segmentación y calcular los cuartiles Q1 y Q3 para cada grupo
    grouped_df = df.groupBy(segmentation).agg(
        count(column).alias("n"),  
        expr(f"percentile_approx({column}, 0.25, {int(0.05*100)})").alias("Q1"),  # calcular cuartil Q1
        expr(f"percentile_approx({column}, 0.75, {int(0.05*100)})").alias("Q3")  # calcular cuartil Q3
    )
    # Calcular los límites de detección utilizando el rango intercuartílico (IQR)
    # El IQR se define como la diferencia entre Q3 y Q1
    # El límite inferior (BI) se define como Q1 - 1.5*IQR, excepto cuando el resultado es negativo, en cuyo caso se utiliza 0
    # El límite superior (BS) se define como Q3 + 1.5*IQR
    grouped_df = grouped_df.withColumn(
        "IQR", col("Q3") - col("Q1")
    ).withColumn(
        "BI", expr(f"case when Q1 - 1.5*IQR < 0 then 0 else Q1 - 1.5*IQR end")
    ).withColumn(
        "BS", col("Q3") + 1.5*col("IQR")
    )
    # Filtrar valores atípicos del DataFrame original utilizando el DataFrame de límites de detección
    outliers_df = df.select(segmentation, column).join(
        grouped_df.select(segmentation, "BI", "BS"), 
        segmentation
    ).filter(
        (df[column] < col("BI")) | (df[column] > col("BS"))
    )
    # Imprimir el número total de valores atípicos encontrados y un resumen
    print(f'\n{key}\n')
    outliers_df.show(outliers_df.count())
    print(f"\nTotal Outliers: {outliers_df.count()}\n\nOutliers por segmentacion:")
    count_outliers_df = outliers_df.groupBy(segmentation).agg(count("*").alias("count"))
    count_outliers_df.show(count_outliers_df.count())
