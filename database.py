# database.py - Configuración y gestión de base de datos SQLite
import sqlite3
import os

DATABASE_PATH = 'kitbox.db'

def get_db_connection():
    """Crea y retorna una conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conn

def init_db():
    """Inicializa la base de datos con las tablas necesarias"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Crear tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            precio INTEGER NOT NULL,
            categoria TEXT NOT NULL
        )
    ''')
    
    # Crear tabla de kits predefinidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kits_predefinidos (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            imagen TEXT NOT NULL
        )
    ''')
    
    # Crear tabla de productos en kits (relación muchos a muchos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kit_productos (
            kit_id TEXT NOT NULL,
            producto_id TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            PRIMARY KEY (kit_id, producto_id),
            FOREIGN KEY (kit_id) REFERENCES kits_predefinidos(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[DB] Base de datos inicializada correctamente")

def poblar_db():
    """Pobla la base de datos con datos iniciales"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verificar si ya hay datos
    cursor.execute('SELECT COUNT(*) FROM productos')
    if cursor.fetchone()[0] > 0:
        print("[DB] La base de datos ya contiene datos")
        conn.close()
        return
    
    print("[DB] Poblando base de datos con productos iniciales...")
    
    # Productos de limpieza
    productos_limpieza = [
        ("L001", "Detergente líquido Drive 1L", 3990, "limpieza"),
        ("L002", "Cloro Clorinda 1L", 1490, "limpieza"),
        ("L003", "Limpiador multiuso Lysol 500ml", 2690, "limpieza"),
        ("L004", "Jabón líquido Lifebuoy 250ml", 1890, "limpieza"),
        ("L005", "Esponjas Scotch-Brite pack x3", 1990, "limpieza"),
        ("L006", "Papel higiénico Elite pack x4", 3290, "limpieza"),
        ("L007", "Toallas de papel Nova pack x2", 2790, "limpieza"),
        ("L008", "Limpiavidrios Windex 500ml", 2490, "limpieza"),
        ("L009", "Bolsas de basura Gala pack x20", 2190, "limpieza"),
        ("L010", "Guantes de látex pack x2", 1290, "limpieza")
    ]
    
    # Productos de snacks
    productos_snacks = [
        ("S001", "Papas fritas Lays 150g", 1990, "snacks"),
        ("S002", "Galletas Sahne-Nuss pack x3", 2790, "snacks"),
        ("S003", "Maní Ebner 200g", 2290, "snacks"),
        ("S004", "Chocolates Ambrosoli pack x6", 3990, "snacks"),
        ("S005", "Galletas TUC 200g", 1890, "snacks"),
        ("S006", "Mezcla de frutos secos 150g", 4290, "snacks"),
        ("S007", "Gomitas Mogul pack x2", 2190, "snacks"),
        ("S008", "Barras de cereal Granola pack x6", 3490, "snacks"),
        ("S009", "Palomitas Act II pack x3", 2690, "snacks"),
        ("S010", "Bebida Red Bull pack x4", 4990, "snacks"),
        ("S011", "Vino Casillero del Diablo 750ml", 8990, "snacks"),
        ("S012", "Pisco Alto del Carmen 35° 750ml", 7990, "snacks"),
        ("S013", "Champagne Brut Imperial 750ml", 15990, "snacks"),
        ("S014", "Cerveza Corona 355ml", 1890, "snacks"),
        ("S015", "Ron Bacardí Carta Blanca 750ml", 11990, "snacks"),
        ("S016", "Whisky Johnnie Walker Red Label 750ml", 14990, "snacks"),
        ("S017", "Vino Concha y Toro 750ml", 4990, "snacks"),
        ("S018", "Pisco Mistral 35° 750ml", 6990, "snacks"),
        ("S019", "Cerveza Kunstmann 1L", 2990, "snacks"),
        ("S020", "Vodka Absolut 750ml", 9990, "snacks"),
        ("S021", "Espumante Santa Carolina Brut 750ml", 5990, "snacks"),
        ("S022", "Pisco Control 40° 750ml", 12990, "snacks"),
        ("S023", "Cerveza Heineken 330ml", 1790, "snacks"),
        ("S024", "Vino Santa Rita 120 750ml", 3990, "snacks"),
        ("S025", "Gin Beefeater 750ml", 13990, "snacks")
    ]
    
    # Productos de belleza
    productos_belleza = [
        ("B001", "Shampoo Pantene 400ml", 4990, "belleza"),
        ("B002", "Acondicionador Sedal 400ml", 4790, "belleza"),
        ("B003", "Crema hidratante Nivea 50ml", 6990, "belleza"),
        ("B004", "Jabón Dove 250ml", 3490, "belleza"),
        ("B005", "Desmaquillante Garnier 200ml", 4990, "belleza"),
        ("B006", "Protector solar Eucerin SPF50", 8990, "belleza"),
        ("B007", "Mascarilla capilar TRESemmé 200ml", 5490, "belleza"),
        ("B008", "Exfoliante Neutrogena 100ml", 5990, "belleza"),
        ("B009", "Sérum facial L'Oréal 30ml", 10990, "belleza"),
        ("B010", "Toallas desmaquillantes Nivea x25", 3990, "belleza")
    ]
    
    # Productos de bebé
    productos_bebe = [
        ("BB001", "Pañales Huggies pack x30", 13990, "bebe"),
        ("BB002", "Toallas húmedas Huggies x80", 4290, "bebe"),
        ("BB003", "Shampoo Johnson's Baby 400ml", 4490, "bebe"),
        ("BB004", "Crema para pañal Babysec 100g", 5990, "bebe"),
        ("BB005", "Jabón líquido Johnson's Baby 250ml", 3790, "bebe"),
        ("BB006", "Aceite Johnson's Baby 200ml", 4990, "bebe"),
        ("BB007", "Algodón Confort x100", 2490, "bebe"),
        ("BB008", "Colonia Johnson's Baby 100ml", 6990, "bebe"),
        ("BB009", "Protector solar Babysec SPF50", 10990, "bebe"),
        ("BB010", "Cotonitos Confort x75", 2190, "bebe")
    ]
    
    # Insertar todos los productos
    todos_productos = productos_limpieza + productos_snacks + productos_belleza + productos_bebe
    cursor.executemany('INSERT INTO productos VALUES (?, ?, ?, ?)', todos_productos)
    
    # Insertar kits predefinidos
    kits = [
        ("semanal", "Kit Semanal", "Todo lo esencial para una semana", "imgs/kit_semana.png"),
        ("mensual", "Kit Mensual", "Abastécete por todo un mes", "imgs/kit_mes.png")
    ]
    cursor.executemany('INSERT INTO kits_predefinidos VALUES (?, ?, ?, ?)', kits)
    
    # Productos del kit semanal
    kit_semanal_productos = [
        ("semanal", "L001", 1),
        ("semanal", "L006", 1),
        ("semanal", "L004", 1),
        ("semanal", "S001", 1),
        ("semanal", "S002", 1),
        ("semanal", "S004", 1),
        ("semanal", "S008", 1),
        ("semanal", "S010", 1)
    ]
    
    # Productos del kit mensual
    kit_mensual_productos = [
        ("mensual", "L001", 2),
        ("mensual", "L002", 1),
        ("mensual", "L003", 1),
        ("mensual", "L004", 2),
        ("mensual", "L005", 1),
        ("mensual", "L006", 3),
        ("mensual", "L007", 2),
        ("mensual", "L009", 1),
        ("mensual", "S001", 4),
        ("mensual", "S002", 2),
        ("mensual", "S003", 2),
        ("mensual", "S004", 2),
        ("mensual", "S006", 1),
        ("mensual", "S008", 2)
    ]
    
    # Insertar productos de kits
    cursor.executemany('INSERT INTO kit_productos VALUES (?, ?, ?)', 
                      kit_semanal_productos + kit_mensual_productos)
    
    conn.commit()
    conn.close()
    print("[DB] Base de datos poblada correctamente")

# Inicializar base de datos al importar el módulo
if not os.path.exists(DATABASE_PATH):
    print("[DB] Creando base de datos por primera vez...")
    init_db()
    poblar_db()
else:
    print("[DB] Base de datos existente encontrada")