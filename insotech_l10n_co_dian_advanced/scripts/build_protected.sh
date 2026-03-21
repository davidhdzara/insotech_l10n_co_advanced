#!/bin/bash
# build_protected.sh
# Script de empaquetado y ofuscación de Insotech L10n CO Advanced (Odoo 19)
# Este script previene la copia y replicación no autorizada del producto.

echo "============================================="
echo " Compilando y Ofuscando Módulo Insotech"
echo "============================================="

# 1. Instalar PyArmor (Herramienta estándar para ofuscar Python)
pip install pyarmor

# 2. Definir rutas
SOURCE_DIR="../models"
DIST_DIR="../obfuscated_dist/models"

# 3. Limpiar carpeta anterior
rm -rf ../obfuscated_dist
mkdir -p $DIST_DIR

# 4. Compilar usando PyArmor
# Pyarmor reemplazará el código fuente legible por bytecode encriptado que Odoo puede leer.
echo ">> Ofuscando archivos en $SOURCE_DIR ..."
pyarmor gen -O $DIST_DIR $SOURCE_DIR/*.py

echo ">> Proceso finalizado. Los archivos ofuscados están en obfuscated_dist/"
echo "Al momento de entregar el módulo al cliente, se deben enviar los .py ofuscados."
