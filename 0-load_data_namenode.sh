#!/bin/bash

# Copiar los archivos locales en el namenode
docker cp Datasets/calendario/Calendario.csv namenode:home/Datasets/calendario/Calendario.csv
docker cp Datasets/canaldeventa/CanalDeVenta.csv namenode:home/Datasets/canaldeventa/CanalDeVenta.csv
docker cp Datasets/cliente/Cliente.csv namenode:home/Datasets/cliente/Cliente.csv
docker cp Datasets/compra/Compra.csv namenode:home/Datasets/compra/Compra.csv
docker cp Datasets/empleado/Empleado.csv namenode:home/Datasets/empleado/Empleado.csv
docker cp Datasets/gasto/Gasto.csv namenode:home/Datasets/gasto/Gasto.csv
docker cp Datasets/producto/Producto.csv namenode:home/Datasets/producto/Producto.csv
docker cp Datasets/proveedor/Proveedor.csv namenode:home/Datasets/proveedor/Proveedor.csv
docker cp Datasets/sucursal/Sucursal.csv namenode:home/Datasets/sucursal/Sucursal.csv
docker cp Datasets/tipodegasto/TiposDeGasto.csv namenode:home/Datasets/tipodegasto/TiposDeGasto.csv
docker cp Datasets/venta/Venta.csv namenode:home/Datasets/venta/Venta.csv