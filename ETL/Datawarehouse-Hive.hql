CREATE DATABASE IF NOT EXISTS technology_sale;
USE technology_sale;


DROP TABLE IF EXISTS calendario;
CREATE EXTERNAL TABLE IF NOT EXISTS calendario (
  IdFecha               INT,
  Fecha                 DATE,
  Anio                  INT,
  Mes                   INT,
  Dia                   INT,
  Trimestre             INT,
  Semana                INT,
  DiaNombre             VARCHAR(12),
  MesNombre             VARCHAR(12)
)
STORED AS PARQUET 
LOCATION '/transformed_data/Calendario'
TBLPROPERTIES ('parquet.compression'='SNAPPY');



DROP TABLE IF EXISTS canal_venta;
CREATE EXTERNAL TABLE IF NOT EXISTS canal_venta (
  IdCanalVenta               INT,
  Descripcion                VARCHAR(12)
)
STORED AS PARQUET 
LOCATION '/transformed_data/CanalDeVenta'
TBLPROPERTIES ('parquet.compression'='SNAPPY');



DROP TABLE IF EXISTS cliente;
CREATE EXTERNAL TABLE IF NOT EXISTS cliente (
  IdCliente              INT,
  Provincia              VARCHAR(50),
  NombreCompleto         VARCHAR(80),
  Domicilio              VARCHAR(150),
  Telefono               VARCHAR(30),
  Edad                   INT,
  Localidad              VARCHAR(80),
  Longitud               FLOAT,
  Latitud                FLOAT
)
STORED AS PARQUET 
LOCATION '/transformed_data/Cliente'
TBLPROPERTIES ('parquet.compression'='SNAPPY');



DROP TABLE IF EXISTS compra;
CREATE EXTERNAL TABLE IF NOT EXISTS Compra (
  IdCompra          INTEGER,
  Fecha             DATE,
  IdProducto        INTEGER,
  Cantidad          INTEGER,
  Precio            FLOAT,
  IdProveedor       INTEGER
)
STORED AS PARQUET
LOCATION '/transformed_data/Compra'
TBLPROPERTIES ('parquet.compression'='SNAPPY');



DROP TABLE IF EXISTS empleado;
CREATE EXTERNAL TABLE IF NOT EXISTS empleado (
  IdEmpleado        INTEGER,
  Apellido          VARCHAR(50),
  Nombre            VARCHAR(80),
  Sucursal          VARCHAR(150),
  Sector            VARCHAR(30),
  Cargo             VARCHAR(30),
  Salario           FLOAT
)
STORED AS PARQUET
LOCATION '/transformed_data/Empleado'
TBLPROPERTIES ('parquet.compression'='SNAPPY');



DROP TABLE IF EXISTS gasto;
CREATE EXTERNAL TABLE IF NOT EXISTS gasto (
  IdGasto           INTEGER,
  IdSucursal        INTEGER,
  Fecha             DATE,
  Monto             FLOAT
)
PARTITIONED BY(IdTipoGasto INTEGER)
STORED AS PARQUET
LOCATION '/transformed_data/Gasto'
TBLPROPERTIES ('parquet.compression'='SNAPPY');



DROP TABLE IF EXISTS producto;
CREATE EXTERNAL TABLE IF NOT EXISTS producto (
  IdProducto        INTEGER,
  Descripcion       VARCHAR(100),
  Precio            FLOAT
)
PARTITIONED BY(Tipo VARCHAR(50))
STORED AS PARQUET
LOCATION '/transformed_data/Producto'
TBLPROPERTIES ('parquet.compression'='SNAPPY');



DROP TABLE IF EXISTS proveedor;
CREATE EXTERNAL TABLE IF NOT EXISTS proveedor (
  IdProveedor       INTEGER,
  Nombre            VARCHAR(40),
  Direccion         VARCHAR(150),
  Ciudad            VARCHAR(80),
  Provincia         VARCHAR(50),
  Pais              VARCHAR(20),
  Localidad         VARCHAR(50)
)
STORED AS PARQUET
LOCATION '/transformed_data/Proveedor'
TBLPROPERTIES ('parquet.compression'='SNAPPY');



DROP TABLE IF EXISTS sucursal;
CREATE EXTERNAL TABLE IF NOT EXISTS sucursal (
  IdSucursal        INTEGER,
  Sucursal          VARCHAR(40),
  Domicilio         VARCHAR(150),
  Localidad         VARCHAR(80),
  Provincia         VARCHAR(50),
  Latitud           FLOAT,
  Longitud          FLOAT
)
STORED AS PARQUET
LOCATION '/transformed_data/Sucursal'
TBLPROPERTIES ('parquet.compression'='SNAPPY');



DROP TABLE IF EXISTS tipo_gasto;
CREATE EXTERNAL TABLE IF NOT EXISTS tipo_gasto (
  IdTipoGasto           INTEGER,
  Descripcion           VARCHAR(50),
  MontoAproximado       FLOAT
)
STORED AS PARQUET
LOCATION '/transformed_data/TiposDeGasto'
TBLPROPERTIES ('parquet.compression'='SNAPPY');



DROP TABLE IF EXISTS venta;
CREATE EXTERNAL TABLE IF NOT EXISTS venta (
  IdVenta            INTEGER,
  Fecha              DATE,
  FechaEntrega       DATE,
  IdCanal            INTEGER, 
  IdCliente          INTEGER, 
  IdSucursal         INTEGER,
  IdEmpleado         INTEGER,
  IdProducto         INTEGER,
  Precio             FLOAT,
  Cantidad           INTEGER
)
STORED AS PARQUET
LOCATION '/transformed_data/Venta'
TBLPROPERTIES ('parquet.compression'='SNAPPY');