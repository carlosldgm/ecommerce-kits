#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para inicializar o resetear la base de datos
Uso: python init_database.py [--reset]
"""

import os
import sys
from database import init_db, poblar_db, DATABASE_PATH

def main():
    reset = '--reset' in sys.argv or '-r' in sys.argv
    
    if reset:
        print("Reseteando base de datos...")
        if os.path.exists(DATABASE_PATH):
            os.remove(DATABASE_PATH)
            print("Base de datos eliminada: {}".format(DATABASE_PATH))
    
    if not os.path.exists(DATABASE_PATH):
        print("Creando nueva base de datos...")
        init_db()
        poblar_db()
        print("Base de datos inicializada correctamente!")
    else:
        print("La base de datos ya existe: {}".format(DATABASE_PATH))
        print("Usa --reset para recrearla desde cero")
    
    # Mostrar estadisticas
    import sqlite3
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM productos')
    total_productos = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM kits_predefinidos')
    total_kits = cursor.fetchone()[0]
    
    cursor.execute('SELECT categoria, COUNT(*) FROM productos GROUP BY categoria')
    categorias = cursor.fetchall()
    
    conn.close()
    
    print("\n=== Estadisticas de la base de datos ===")
    print("Total de productos: {}".format(total_productos))
    print("Total de kits: {}".format(total_kits))
    print("\nProductos por categoria:")
    for cat, count in categorias:
        print("  - {}: {} productos".format(cat, count))

if __name__ == '__main__':
    main()