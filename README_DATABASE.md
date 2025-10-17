# 🗄️ Migración a Base de Datos SQLite

## ✅ Cambios Realizados

Se ha migrado el almacenamiento de datos de diccionarios Python a una base de datos SQLite, manteniendo **100% de compatibilidad** con el código existente.

## 📁 Nuevos Archivos

1. **`database.py`** - Configuración y gestión de la base de datos
2. **`data.py`** (actualizado) - Interfaz compatible que usa SQLite
3. **`init_database.py`** - Script para inicializar/resetear la BD
4. **`kitbox.db`** - Base de datos SQLite (se crea automáticamente)

## 🚀 Cómo Usar

### Primera Vez

La base de datos se crea automáticamente al iniciar la aplicación:

```bash
python app.py
```

### Resetear Base de Datos

Si necesitas recrear la base de datos desde cero:

```bash
python init_database.py --reset
```

### Ver Estadísticas

Para ver información sobre la base de datos actual:

```bash
python init_database.py
```

## 🔧 Estructura de la Base de Datos

### Tabla: `productos`
| Columna   | Tipo    | Descripción          |
|-----------|---------|----------------------|
| id        | TEXT    | ID único (PK)        |
| nombre    | TEXT    | Nombre del producto  |
| precio    | INTEGER | Precio en pesos      |
| categoria | TEXT    | Categoría del producto|

### Tabla: `kits_predefinidos`
| Columna     | Tipo    | Descripción          |
|-------------|---------|----------------------|
| id          | TEXT    | ID único (PK)        |
| nombre      | TEXT    | Nombre del kit       |
| descripcion | TEXT    | Descripción del kit  |
| imagen      | TEXT    | Ruta de la imagen    |

### Tabla: `kit_productos`
| Columna      | Tipo    | Descripción             |
|--------------|---------|-------------------------|
| kit_id       | TEXT    | ID del kit (FK)         |
| producto_id  | TEXT    | ID del producto (FK)    |
| cantidad     | INTEGER | Cantidad del producto   |

## 💻 API Compatible

Todas las funciones originales siguen funcionando igual:

```python
from data import PRODUCTOS, KITS_PREDEFINIDOS, get_producto_by_id

# Usar productos (igual que antes)
productos_limpieza = PRODUCTOS['limpieza']

# Obtener producto por ID
producto = get_producto_by_id('L001')

# Obtener kit con precio calculado
kit = get_kit_con_precio('kit_semanal')
```

## ✨ Nuevas Funcionalidades

### Agregar Producto

```python
from data import agregar_producto

agregar_producto(
    id='L011',
    nombre='Nuevo Producto',
    precio=5990,
    categoria='limpieza'
)
```

### Actualizar Producto

```python
from data import actualizar_producto

actualizar_producto(
    id='L001',
    precio=4500  # Solo actualizar precio
)
```

### Eliminar Producto

```python
from data import eliminar_producto

eliminar_producto('L011')
```

### Refrescar Cache

Si modificas la BD directamente y quieres actualizar las variables globales:

```python
from data import refrescar_cache

refrescar_cache()
```

## 🎯 Ventajas de la Migración

1. **Persistencia** - Los datos persisten entre reinicios
2. **Escalabilidad** - Fácil agregar/modificar productos
3. **Integridad** - Relaciones con claves foráneas
4. **Consultas** - Búsquedas y filtros más eficientes
5. **Compatibilidad** - No requiere cambios en app.py

## 🔍 Consultas Directas (Opcional)

Si necesitas hacer consultas personalizadas:

```python
from database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Ejemplo: Productos más caros
cursor.execute('''
    SELECT * FROM productos 
    WHERE precio > 10000 
    ORDER BY precio DESC
''')

productos_caros = cursor.fetchall()
conn.close()
```

## ⚠️ Notas Importantes

- El archivo `kitbox.db` NO debe subirse a Git (agregar al `.gitignore`)
- Las variables `PRODUCTOS` y `KITS_PREDEFINIDOS` se cargan al iniciar
- Si modificas la BD en tiempo real, usa `refrescar_cache()`
- Los precios se almacenan como INTEGER (en pesos chilenos)

## 🛠️ Troubleshooting

### Error: "no such table: productos"
```bash
python init_database.py --reset
```

### Error: "database is locked"
- Cierra todas las conexiones a la BD
- Reinicia la aplicación

### Datos no se actualizan
```python
from data import refrescar_cache
refrescar_cache()
```

## 📝 TODO Futuro

- [ ] Panel de administración para CRUD de productos
- [ ] Historial de ventas en la BD
- [ ] Sistema de usuarios y autenticación
- [ ] Reportes y analytics

---

**Versión:** 1.0  
**Última actualización:** Octubre 2025