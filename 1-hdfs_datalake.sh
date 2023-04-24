# Crear el directorio raw_data en hdfs
#       En este directorio se almacenarán los datos en su estado original
hdfs dfs -rm -r /raw_data
hdfs dfs -mkdir /raw_data
hdfs dfs -setrep 3 /raw_data

#       Creo los subdirectorios "csv_data" y "parquet_data"
hdfs dfs -rm -r /raw_data/csv_data
hdfs dfs -mkdir /raw_data/csv_data
hdfs dfs -setrep 3 /raw_data/csv_data

hdfs dfs -rm -r /raw_data/parquet_data
hdfs dfs -mkdir /raw_data/parquet_data
hdfs dfs -setrep 3 /raw_data/parquet_data

# Crear el directorio transformed_data en hdfs
#       En este directorio se almacenarán los datos transformados+
hdfs dfs -rm -r /transformed_data
hdfs dfs -mkdir /transformed_data
hdfs dfs -setrep 3 /transformed_data

# Copiar los elementos del sistema de archivos local (namenode) al del cluster (hdfs)
hdfs dfs -put /home/Datasets/* /raw_data/csv_data