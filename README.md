# KitBox - Ecommerce de Kits (instrucciones de instalación)

Este repositorio contiene una pequeña aplicación Flask para crear y gestionar "kits" de productos y un asistente de IA que ayuda a generar kits personalizados.

Este README explica cómo clonar, instalar y ejecutar la app en macOS (zsh). Incluye los pasos para inicializar la base de datos SQLite y ejecutar tests.

---

## Requisitos

- macOS con Python 3.11 (o 3.10+)
- Git
- Una clave de OpenAI si deseas usar la funcionalidad de IA

---

## 1) Clonar el repositorio

```bash
git clone https://github.com/carlosldgm/ecommerce-kits.git
cd ecommerce-kits
```

## 2) Crear y activar entorno virtual (recomendado)

```bash
python3 -m venv myenv
source myenv/bin/activate
```

## 3) Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Dependencias principales incluidas: Flask, openai, httpx, jinja2, werkzeug, pydantic, entre otras.

## 4) Configurar la clave de OpenAI

Exporta tu clave en la terminal (no la subas al repositorio):

```bash
export OPENAI_API_KEY="tu_clave_aqui"
```

P. ej., para persistencia añade la línea anterior a `~/.zshrc`.

## 5) Inicializar la base de datos SQLite

La app usa SQLite y el script `init_database.py` facilita la creación o reset de la BD.

- Crear base de datos (si no existe):

```bash
python init_database.py
```

- Resetear y recrear (desde cero):

```bash
python init_database.py --reset
```

El script mostrará estadísticas (total productos, kits, productos por categoría).

> Nota: `kitbox.db` está en `.gitignore` y no debe subirse al repositorio.

## 6) Ejecutar la aplicación

Con el entorno activado y `OPENAI_API_KEY` configurada:

```bash
python app.py
```

Abrir en el navegador: http://127.0.0.1:5000

La app corre en modo debug por defecto (ver `app.py`). Para producción, usar un servidor WSGI y desactivar `debug`.

## 7) Ejecutar tests

Hay un archivo de pruebas `test_ai_assistant.py` para comprobar el comportamiento del asistente:

```bash
python test_ai_assistant.py
```

## 8) Troubleshooting rápido

- Error "no such table: productos":
  ```bash
  python init_database.py --reset
  ```
- Error por `OPENAI_API_KEY` faltante: exporta la variable en la terminal donde ejecutas la app.
- Error "database is locked": cierra otras conexiones a la BD y reintenta.

## 9) Buenas prácticas

- No subir claves ni el archivo `kitbox.db` al repositorio.
- Añadir cambios con `git add`, `git commit` y `git push origin main`.

---

Si quieres, puedo añadir un script `scripts/setup.sh` que automatice los pasos de creación del venv e instalación, o añadir GitHub Actions para ejecutar tests automáticamente.

Gracias — cualquier ajuste que quieras en el README lo hago y lo subo. 
