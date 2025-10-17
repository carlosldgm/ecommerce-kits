# data.py - Interfaz de acceso a datos usando SQLite
# Mantiene la misma API que la versión anterior para compatibilidad

from database import get_db_connection

def get_productos_dict():
    """
    Retorna productos organizados por categoría (compatible con código existente)
    Formato: {"categoria": [{"id": "...", "nombre": "...", "precio": ..., "categoria": "..."}]}
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener todas las categorías únicas
    cursor.execute('SELECT DISTINCT categoria FROM productos ORDER BY categoria')
    categorias = [row['categoria'] for row in cursor.fetchall()]
    
    # Construir diccionario por categoría
    productos_dict = {}
    for categoria in categorias:
        cursor.execute('''
            SELECT id, nombre, precio, categoria 
            FROM productos 
            WHERE categoria = ? 
            ORDER BY id
        ''', (categoria,))
        
        productos_dict[categoria] = [
            {
                'id': row['id'],
                'nombre': row['nombre'],
                'precio': row['precio'],
                'categoria': row['categoria']
            }
            for row in cursor.fetchall()
        ]
    
    conn.close()
    return productos_dict

# Variable global PRODUCTOS para compatibilidad con código existente
PRODUCTOS = get_productos_dict()

def get_kits_predefinidos_dict():
    """
    Retorna kits predefinidos con sus productos
    Formato compatible con código existente
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener todos los kits
    cursor.execute('SELECT * FROM kits_predefinidos')
    kits_rows = cursor.fetchall()
    
    kits_dict = {}
    for kit_row in kits_rows:
        kit_id = kit_row['id']
        
        # Obtener productos del kit
        cursor.execute('''
            SELECT producto_id as id, cantidad 
            FROM kit_productos 
            WHERE kit_id = ?
        ''', (kit_id,))
        
        productos = [
            {'id': row['id'], 'cantidad': row['cantidad']}
            for row in cursor.fetchall()
        ]
        
        kits_dict[kit_id] = {
            'id': kit_row['id'],
            'nombre': kit_row['nombre'],
            'descripcion': kit_row['descripcion'],
            'imagen': kit_row['imagen'],
            'productos': productos
        }
    
    conn.close()
    return kits_dict

# Variable global KITS_PREDEFINIDOS para compatibilidad
KITS_PREDEFINIDOS = get_kits_predefinidos_dict()

def get_all_kits_con_precio():
    """
    Retorna todos los kits con sus precios calculados
    Compatible con el código existente en app.py
    """
    kits_con_precio = {}
    for kit_id in KITS_PREDEFINIDOS.keys():
        kits_con_precio[kit_id] = get_kit_con_precio(kit_id)
    return kits_con_precio

def get_producto_by_id(producto_id):
    """Obtiene un producto por su ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nombre, precio, categoria 
        FROM productos 
        WHERE id = ?
    ''', (producto_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row['id'],
            'nombre': row['nombre'],
            'precio': row['precio'],
            'categoria': row['categoria']
        }
    return None

def get_all_productos():
    """Obtiene todos los productos en una lista plana"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nombre, precio, categoria 
        FROM productos 
        ORDER BY categoria, id
    ''')
    
    productos = [
        {
            'id': row['id'],
            'nombre': row['nombre'],
            'precio': row['precio'],
            'categoria': row['categoria']
        }
        for row in cursor.fetchall()
    ]
    
    conn.close()
    return productos

def calcular_precio_kit(kit):
    """Calcula el precio total de un kit basado en sus productos y cantidades"""
    precio_total = 0
    for item in kit.get('productos', []):
        producto = get_producto_by_id(item['id'])
        if producto:
            precio_total += producto['precio'] * item['cantidad']
    return precio_total

def get_kit_con_precio(kit_id):
    """Obtiene un kit con su precio calculado"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener información del kit
    cursor.execute('''
        SELECT * FROM kits_predefinidos WHERE id = ?
    ''', (kit_id,))
    
    kit_row = cursor.fetchone()
    if not kit_row:
        conn.close()
        return None
    
    # Obtener productos del kit
    cursor.execute('''
        SELECT producto_id as id, cantidad 
        FROM kit_productos 
        WHERE kit_id = ?
    ''', (kit_id,))
    
    productos = [
        {'id': row['id'], 'cantidad': row['cantidad']}
        for row in cursor.fetchall()
    ]
    
    conn.close()
    
    kit = {
        'id': kit_row['id'],
        'nombre': kit_row['nombre'],
        'descripcion': kit_row['descripcion'],
        'imagen': kit_row['imagen'],
        'productos': productos
    }
    
    kit['precio'] = calcular_precio_kit(kit)
    return kit

# Funciones adicionales para gestión de base de datos

def refrescar_cache():
    """
    Refresca las variables globales PRODUCTOS y KITS_PREDEFINIDOS
    Útil si se modifican datos en la base de datos
    """
    global PRODUCTOS, KITS_PREDEFINIDOS
    PRODUCTOS = get_productos_dict()
    KITS_PREDEFINIDOS = get_kits_predefinidos_dict()
    print("[DATA] Cache refrescado desde base de datos")

def agregar_producto(id, nombre, precio, categoria):
    """Agrega un nuevo producto a la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO productos (id, nombre, precio, categoria)
            VALUES (?, ?, ?, ?)
        ''', (id, nombre, precio, categoria))
        conn.commit()
        conn.close()
        refrescar_cache()
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo agregar producto: {e}")
        conn.close()
        return False

def actualizar_producto(id, nombre=None, precio=None, categoria=None):
    """Actualiza un producto existente"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Construir query dinámicamente según campos proporcionados
    updates = []
    params = []
    
    if nombre is not None:
        updates.append('nombre = ?')
        params.append(nombre)
    if precio is not None:
        updates.append('precio = ?')
        params.append(precio)
    if categoria is not None:
        updates.append('categoria = ?')
        params.append(categoria)
    
    if not updates:
        conn.close()
        return False
    
    params.append(id)
    query = f"UPDATE productos SET {', '.join(updates)} WHERE id = ?"
    
    try:
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        refrescar_cache()
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo actualizar producto: {e}")
        conn.close()
        return False

def eliminar_producto(id):
    """Elimina un producto de la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Primero eliminar de kits si existe
        cursor.execute('DELETE FROM kit_productos WHERE producto_id = ?', (id,))
        # Luego eliminar el producto
        cursor.execute('DELETE FROM productos WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        refrescar_cache()
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo eliminar producto: {e}")
        conn.close()
        return False