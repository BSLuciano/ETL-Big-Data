from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name
import os


spark = SparkSession.builder \
    .appName("change_format") \
    .getOrCreate()


#EXTRACCIÓN

# extract_csv:

#         - Objetivo:
# Esta función carga recursivamente todos los archivos CSV que se encuentran en
# la carpeta raíz especificada, crea un DataFrame por cada archivo y los asigna
# como valores a un diccionario, donde la clave es el nombre del archivo.

#         - Detalles:
# recursiveFileLookup: 
#   esta opción le dice a Spark que explore de forma recursiva todas las subcarpetas de la carpeta raíz
#   en busca de archivos CSV. De esta manera, Spark podrá cargar todos los archivos CSV que se encuentren
#   en las subcarpetas, sin tener que especificar la ruta completa de cada archivo, incluso si hay varias
#   carpetas anidadas a diferentes niveles. Básicamente lo que hace es permitir iterar entre todas las
#   subcarpetas hasta el nivel más bajo que contenga un archivo CSV.

# .select(input_file_name()).distinct().collect():
#   input_file_name(): es una función de Spark SQL que devuelve el nombre completo del
#         archivo que se está leyendo. 
#   .distinct(): se usa para evitar que se repita el nombre del archivo. 
#   .collect(): este método devuelve una lista de objetos Row, cada uno con
#         las columnas seleccionadas en la operación select().

def extract_csv(root_folder: str) -> None:
    dict = {}
    for folder in spark.read.format("csv").option("recursiveFileLookup", "true").option("header", "true").load(root_folder).select(input_file_name()).distinct().collect():
        path = folder[0]
        file_name = os.path.basename(path).split(".")[0]
        # Detectar el delimitador automáticamente
        df = spark.read.text(path)
        header = df.first()[0]
        delimiters = [",", ";", "|"]
        detected_delimiter = None
        for delimiter in delimiters:
            if delimiter in header:
                detected_delimiter = delimiter
                break      
        if detected_delimiter:
            df = spark.read.format("csv").option("header", "true").option("delimiter", detected_delimiter).load(path)
        else:
            raise ValueError("Could not detect delimiter in file")
        dict[file_name] = df
    return dict

path_1 = "hdfs://namenode:9000/raw_data/csv_data"
dict_df = extract_csv(path_1)


# ----------------------------------------------------------------------------------------------------------

# Normalización de columna " Precio "

# Se deben quitar los caracteres especiales (" ") del nombre de la columna debido a que
# generan un error al realizar la conversion

for key in dict_df:
    df = dict_df[key]
    for column in df.columns:
        if column == " Precio ":
            df = df.withColumnRenamed(" Precio ", "Precio")
            dict_df[key] = df 



# ----------------------------------------------------------------------------------------------------------

# CSV -> Parquet + Snappy

def format_conversion(dictionary_df: dict, root_folder: str) -> None:
    for key in dictionary_df.keys():
        df = dictionary_df[key]
        df.write.mode('overwrite').option("compression", "snappy").parquet(f'{root_folder}/{key}')

path_2 = "hdfs://namenode:9000/raw_data/parquet_data"
format_conversion(dict_df, path_2)