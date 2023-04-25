# Proyecto: Data Engineering
#### Autor: Luciano Barcenilla Simón
#### contacto:
#####           - mail: barcenillasimonluciano@gmail.com


## Objetivo:

Este es un proyecto en el cual simulo un entorno big data por medio de contenedores de docker
integrando Hadoop, Spark y Hive para llevar a cabo distintas tareas del área de ingeniería
de datos, con el fin de:

	a) Crear un Datalake en Hadoop
	b) Realizar un Análisis Exploratorio de Datos (EDA) con Spark
	c) Hacer una Extracción, Transformación y Carga (ETL) con Spark
	d) Crear un Datawarehouse con Hive
	
Los datos utilizados son de una tienda de artículos tecnológicos.


###	a) Datalake:

		El proceso de creación de las distintas carpetas, así como la carga de los archivos originales en formato .csv
		se ejecuta desde un shell script.

		Los datos sin procesar en formato .parquet y los transformados en formato .parquet son cargados mediante scripts
		de python.


####	Esquema final:

		hdfs ------- /raw_data
			|	|
			|	|-- /csv_data ----- calendario
			|	|		|-- canaldeventa
			|	|		|-- cliente
			|	|		|-- compra
			|	|		|-- empleado
			|	|		|-- gasto
			|	|		|-- producto
			|	|		|-- proveedor
         		|	|		|-- sucursal
			|	|		|-- tipodegasto
			|	|		|-- venta
			|	|
			|	|-- /parquet_data ----- Calendario
			|			    |-- CanalDeVenta
			|			    |-- Cliente
			|			    |-- Compra
			|			    |-- Empleado
			|			    |-- Gasto
			|			    |-- Producto
			|			    |-- Proveedor
           	        |			    |-- Sucursal
			|	            	    |-- TipoDeGasto
			|			    |-- Venta
			|
			|
			|--- /transformed_data ----- Calendario
						 |-- CanalDeVenta
						 |-- Cliente
						 |-- Compra
						 |-- Empleado
						 |-- Gasto
						 |-- Producto
						 |-- Proveedor
					 	 |-- Sucursal
						 |-- TipoDeGasto
						 |-- Venta	



###	b) EDA

	Para el EDA utilicé PySpark. El objetivo de esta etapa fue conocer y entender lo datos con los que
	se cuenta y determinar los problemas que presentan como: registros duplicados, valores nulos,
	valores atípicos, nombres de columnas y datos a normalizar, verificar el tipo de dato de las columnas
	y la presencia de caracteres especiales que imposibiliten aplicar el formato correcto a las mismas.

	Algo a destacar es que en estos procesos es muy importante el uso de gráficos, lo cual no apliqué
	debido a limitaciones de de mi pc, ya que utilizar un contenedor con jupyter exedía los recursos
	disponibles.
	

###	c) ETL

	El ETL tambíen lo desarrollé con Pyspark, creé funciones con el objetivo de corregir cada uno de los
	problemas detectados en el paso anterior. Una vez procesados todos los datos y terminadas las correciones
	procedí a cargar los datos nuevamente en el Datalake en el directrio correspondiente.


###	d) Datawarehouse
	
	Cree una base de datos y cargue los archivos del directorio /transformed_data a cada una de las tablas. 
	



### Notas:
	- Cada una de las funciones creadas para las distintas etapas están explicadas en el archivo correspondiente.
	- Todos los procesos son ejecutados por scripts de shell, python y hive. También deje los pasos para ejecutar el EDA con un script de python, pero recomiendo ir ejecutando por parte debido a que de la otra manera se pueden perder algunos resultados



## Pasos a seguir:

### 0) Ejecutar el contenedor:
	
	Por medio de la consola, situarse en el directorio donde se encuentra el archivo .yml y ejecutar:
	
####	>> docker compose -f docker-compose.yml up -d


### 1) Copiar los archivos ubicados en la carpeta Datasets, dentro del contenedor "namenode":

   Ingresar al namenode y crear el directorio donde se copiarán los archivos. Para ello,
   copiar el script 0-crear_directorios.sh en el namenode para poder ejecutarlo (es necesario encontrarse
   en el directorio donde está el script):
	
####	>> docker cp 0-crear_directorios.sh namenode:home/0-crear_directorios.sh
####	>> docker exec -it namenode bash
####	>> cd home
####	>> sh 0-crear_directorios.sh



### 2) Situarse en la carpeta donde se ubica el archivo 0-load_data_namenode.sh y ejecutarlo para copiar los archivos locales en el sistema de archivos del namenode.

####	>> sh 0-load_data_namenode.sh

#### Nota: los pasos anteriores los realicé a modo de práctica, pueden simplificarse copiando directamente la carpeta Datasets en el contenedor del namenode
	
####	>> docker cp Datasets/ namenode:home/Datasets/



### 3) Datalake (Hadoop)
   
   Disponibilizar los elementos del sistema de archivos del namenode en el sistema de archivos del cluster (hdfs):

   Copiar el script en el namenode y ejecutarlo:

####	>> docker cp 1-hdfs_datalake.sh namenode:home/1-hdfs_datalake.sh
####	>> docker exec -it namenode bash
####	>> sh home/1-hdfs_datalake.sh
	

	Listar los elementos cargados en el sistema de archivos del cluster
####	>> hdfs dfs -ls /raw_data/csv_data



### 4) Copiar archivos locales en el sistema de archivos de spark
	
	El objetivo de esto es disponibilizar los archivos .py en spark para automatizar el proceso de EDA y ETL ejecutando los
	scripts en la consola.
		
####	>> docker cp 2-csv_data_to_parquet+snappy.py spark-master:/opt/bitnami/spark/scripts/2-csv_data_to_parquet+snappy.py
####	>> docker cp EDA/EDA_functions.py spark-master:/opt/bitnami/spark/scripts/EDA_functions.py
####	>> docker cp EDA/EDA.py spark-master:/opt/bitnami/spark/scripts/EDA.py
####	>> docker cp ETL/ETL_functions.py spark-master:/opt/bitnami/spark/scripts/ETL_functions.py
####	>> docker cp ETL/ETL.py spark-master:/opt/bitnami/spark/scripts/ETL.py

	El archivo "2-csv_data_to_parquet+snappy.py" contiene las intrucciones para transformar los archivos originales de formato .csv a .parquet comprimidos con snappy, lo cual brinda ventajas en terminos de procesamiento y espacio de almacenamiento.



### 5) Transformación de formato de archivos, EDA y ETL:

   Ingresar a la consola de PySpark y ejecutar:

####	>> docker exec -it spark-master bash
####	>> pyspark
####	>> exec(open("/opt/bitnami/spark/scripts/2-csv_data_to_parquet+snappy.py").read())
####	>> exec(open("/opt/bitnami/spark/scripts/EDA.py").read())
####	>> exec(open("/opt/bitnami/spark/scripts/ETL.py").read())

        Con estas sentencias se ejecutan cada uno de los scripts cargados a Spark del paso anterior.


### 6) Datawarehouse (Hive)

   Copiar los archivos .hql en el directorio de Hive:
	
####	>> docker cp ETL/Datawarehouse-Hive.hql hive-server:/opt/hql/Datawarehouse-Hive.hql	

   Ingresar a la consola de Hive:

####	>> docker exec -it hive-server bash

   Crear la base de datos:
	
####	>> source /opt/hql/Datawarehouse-Hive.hql;



### Optimizaciones:

	Algunas mejoras que se pueden hacer son:

	- Integrar Jupyter para mejorar el EDA.
	- Incorporar Airflow para automatizar la ejecución de los scripts y gestionar el proceso
		programando el flujo de las tareas.
