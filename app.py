# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, session
from data import PRODUCTOS, KITS_PREDEFINIDOS, get_producto_by_id, get_all_productos, calcular_precio_kit, get_kit_con_precio
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = 'tu-clave-secreta-super-segura-12345'

# Configurar OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Sistema de prompt para el asistente
SYSTEM_PROMPT = """Eres un asistente de compras experto para KitBox, una tienda de kits de productos.

Tu trabajo es ayudar a los usuarios a crear kits personalizados según sus necesidades y presupuesto.

PRODUCTOS DISPONIBLES:
{productos_json}

INSTRUCCIONES IMPORTANTES:

1. MEMORIA Y CONTEXTO:
   - Recuerda toda la información que el usuario ya te dio en la conversación
   - NO repitas preguntas sobre información que ya tienes
   - Si el usuario ya mencionó el presupuesto y tipo de productos, NO vuelvas a preguntar

2. CUÁNDO HACER PREGUNTAS:
   - Solo haz 1-2 preguntas de seguimiento si REALMENTE necesitas información crítica
   - Si ya tienes presupuesto y categoría de productos, genera las opciones directamente
   - Preguntas válidas SOLO si hace falta:
     * Para fiestas: ¿cuántas personas? (solo si no es obvio)
     * Para bebés: ¿qué edad? (solo si es relevante para la selección)
   - NO preguntes cosas obvias o genéricas

3. CÁLCULO DE PRECIOS (MUY IMPORTANTE):
   - El precio de cada producto es UNITARIO
   - Si sugieres cantidad 3 de un producto de $1,800, el costo es: 3 × $1,800 = $5,400
   - El precio_total del kit debe ser la SUMA de (precio × cantidad) de cada producto
   - NUNCA excedas el presupuesto del usuario

4. Sé creativo y considera diferentes combinaciones
5. Explica brevemente por qué cada opción es buena

IMPORTANTE: Debes responder SIEMPRE en formato JSON válido.

FORMATO DE RESPUESTA JSON:

Si REALMENTE necesitas una información crítica (úsalo solo 1 vez):
{{
    "mensaje": "Tu pregunta específica y concreta",
    "opciones": []
}}

Si ya tienes suficiente información (LO MÁS COMÚN):
{{
    "mensaje": "Tu mensaje amigable explicando las opciones",
    "opciones": [
        {{
            "nombre": "Nombre descriptivo de la opción",
            "productos": [
                {{"id": "L001", "cantidad": 2}},
                {{"id": "S003", "cantidad": 1}}
            ],
            "precio_total": 15000,
            "descripcion": "Breve descripción de por qué es buena opción"
        }}
    ]
}}

EJEMPLO: 
Usuario dice: "Tengo $50,000 para una fiesta con amigos mayores de edad"
TU RESPUESTA: Genera directamente 3 opciones con snacks y bebidas. NO preguntes más."""

# Ruta principal - Home
@app.route('/')
def home():
    # Calcular precios dinámicamente para la vista
    kits_con_precio = {}
    for kit_id, kit_data in KITS_PREDEFINIDOS.items():
        kits_con_precio[kit_id] = get_kit_con_precio(kit_id)
    return render_template('home.html', kits=kits_con_precio)

# Ruta detalle de kit predefinido
@app.route('/kit/<kit_id>')
def kit_detail(kit_id):
    kit = get_kit_con_precio(kit_id)
    if not kit:
        return "Kit no encontrado", 404
    
    # Obtener detalles completos de los productos del kit
    productos_detalle = []
    for item in kit['productos']:
        producto = get_producto_by_id(item['id'])
        if producto:
            productos_detalle.append({
                'id': producto['id'],
                'nombre': producto['nombre'],
                'precio': producto['precio'],
                'categoria': producto.get('categoria', ''),
                'cantidad': item['cantidad']
            })
    
    return render_template('kit_detail.html', kit=kit, productos=productos_detalle)

# Ruta constructor de kit customizado
@app.route('/kit/custom')
def custom_kit():
    return render_template('custom_kit.html', productos=PRODUCTOS)

# Ruta ver carrito
@app.route('/carrito')
def ver_carrito():
    carrito = session.get('carrito', [])
    
    # Calcular total
    total = 0
    for item in carrito:
        total += item.get('precio', 0)
    
    return render_template('carrito.html', carrito=carrito, total=total)

# API: Eliminar producto individual de un kit
@app.route('/api/carrito/eliminar-producto', methods=['POST'])
def eliminar_producto_de_kit():
    data = request.json
    kit_index = data.get('kit_index')
    producto_index = data.get('producto_index')
    
    carrito = session.get('carrito', [])
    
    if 0 <= kit_index < len(carrito):
        kit = carrito[kit_index]
        
        # Solo permitir eliminar productos de kits customizados
        if kit.get('tipo') == 'kit_customizado' and kit.get('productos'):
            if 0 <= producto_index < len(kit['productos']):
                # Eliminar el producto
                producto_eliminado = kit['productos'].pop(producto_index)
                
                # Recalcular el precio del kit
                kit['precio'] -= producto_eliminado['precio']
                
                # Si el kit queda vacío, eliminarlo del carrito
                if len(kit['productos']) == 0:
                    carrito.pop(kit_index)
                    session['carrito'] = carrito
                    session.modified = True
                    return jsonify({
                        'success': True, 
                        'message': 'Kit eliminado porque quedó vacío',
                        'total_items': len(carrito)
                    })
                
                session['carrito'] = carrito
                session.modified = True
                return jsonify({
                    'success': True,
                    'total_items': len(carrito)
                })
        else:
            return jsonify({
                'success': False,
                'message': 'No se pueden eliminar productos individuales de kits predefinidos'
            }), 400
    
    return jsonify({'success': False, 'message': 'Índice inválido'}), 400

# API: Cambiar cantidad de producto en kit
@app.route('/api/carrito/cambiar-cantidad', methods=['POST'])
def cambiar_cantidad_producto():
    data = request.json
    kit_index = data.get('kit_index')
    producto_index = data.get('producto_index')
    cambio = data.get('cambio')  # +1 o -1
    
    carrito = session.get('carrito', [])
    
    if 0 <= kit_index < len(carrito):
        kit = carrito[kit_index]
        
        if kit.get('productos') and 0 <= producto_index < len(kit['productos']):
            producto = kit['productos'][producto_index]
            cantidad_actual = producto.get('cantidad', 1)
            nueva_cantidad = cantidad_actual + cambio
            
            # No permitir cantidad menor a 1
            if nueva_cantidad < 1:
                return jsonify({
                    'success': False,
                    'message': 'La cantidad mínima es 1'
                }), 400
            
            # Actualizar cantidad del producto
            producto['cantidad'] = nueva_cantidad
            
            # Recalcular precio total del kit sumando todos los productos
            precio_total = 0
            for prod in kit['productos']:
                # Obtener precio base del producto
                producto_base = get_producto_by_id(prod['id'])
                if producto_base:
                    precio_total += producto_base['precio'] * prod['cantidad']
            
            # Actualizar precio del kit
            kit['precio'] = precio_total
            
            session['carrito'] = carrito
            session.modified = True
            
            return jsonify({
                'success': True,
                'nueva_cantidad': nueva_cantidad,
                'nuevo_precio_kit': kit['precio']
            })
    
    return jsonify({'success': False, 'message': 'Índice inválido'}), 400

# API: Agregar producto al carrito
@app.route('/api/carrito/agregar', methods=['POST'])
def agregar_carrito():
    data = request.json
    
    if 'carrito' not in session:
        session['carrito'] = []
    
    # Agregar item al carrito
    session['carrito'].append(data)
    session.modified = True
    
    return jsonify({'success': True, 'total_items': len(session['carrito'])})

# API: Obtener carrito
@app.route('/api/carrito')
def obtener_carrito():
    carrito = session.get('carrito', [])
    return jsonify({'items': carrito, 'total': len(carrito)})

# API: Limpiar carrito
@app.route('/api/carrito/limpiar', methods=['POST'])
def limpiar_carrito():
    session['carrito'] = []
    session.modified = True
    return jsonify({'success': True})

# API: Eliminar item del carrito
@app.route('/api/carrito/eliminar/<int:index>', methods=['DELETE'])
def eliminar_item_carrito(index):
    carrito = session.get('carrito', [])
    if 0 <= index < len(carrito):
        carrito.pop(index)
        session['carrito'] = carrito
        session.modified = True
        return jsonify({'success': True, 'total_items': len(carrito)})
    return jsonify({'success': False, 'error': 'Índice inválido'}), 400

# API: Chat con IA
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    mensaje_usuario = data.get('mensaje', '')
    historial = data.get('historial', [])  # Recibir historial de conversación
    
    if not mensaje_usuario:
        return jsonify({'error': 'Mensaje vacío'}), 400
    
    try:
        # Preparar información de productos para el prompt
        import json
        productos_info = []
        for categoria, productos in PRODUCTOS.items():
            for producto in productos:
                productos_info.append({
                    'id': producto['id'],
                    'nombre': producto['nombre'],
                    'precio': producto['precio'],
                    'categoria': categoria
                })
        
        productos_json = json.dumps(productos_info, ensure_ascii=False, indent=2)
        
        print("[CHAT] Usuario preguntó: " + str(mensaje_usuario))
        print("[CHAT] Historial: {} mensajes previos".format(len(historial)))
        print("[CHAT] Llamando a OpenAI...")
        
        # Construir mensajes con historial
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(productos_json=productos_json)
            }
        ]
        
        # Agregar historial de conversación
        messages.extend(historial)
        
        # Agregar mensaje actual del usuario
        messages.append({
            "role": "user",
            "content": mensaje_usuario
        })
        
        # Llamar a OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        # Obtener respuesta
        respuesta_texto = response.choices[0].message.content
        print(f"[CHAT] Respuesta de OpenAI: {respuesta_texto[:200]}...")
        
        # Parsear como JSON
        respuesta_json = json.loads(respuesta_texto)
        
        # Enriquecer las opciones con información completa de productos Y VALIDAR PRECIOS
        if 'opciones' in respuesta_json:
            for opcion in respuesta_json['opciones']:
                productos_completos = []
                precio_calculado = 0
                
                for item in opcion.get('productos', []):
                    producto = get_producto_by_id(item['id'])
                    if producto:
                        cantidad = item['cantidad']
                        # Calcular precio correcto: precio unitario × cantidad
                        precio_producto = producto['precio'] * cantidad
                        precio_calculado += precio_producto
                        
                        productos_completos.append({
                            'id': producto['id'],
                            'nombre': producto['nombre'],
                            'precio': producto['precio'],
                            'categoria': producto.get('categoria', ''),
                            'cantidad': cantidad
                        })
                
                opcion['productos_completos'] = productos_completos
                
                # CORREGIR el precio_total si está mal calculado
                precio_original = opcion.get('precio_total', 0)
                opcion['precio_total'] = precio_calculado
                
                if precio_original != precio_calculado:
                    print(f"[WARNING] Precio corregido en '{opcion['nombre']}': IA dijo ${precio_original:,}, real ${precio_calculado:,}")
        
        print(f"[CHAT] Enviando {len(respuesta_json.get('opciones', []))} opciones al frontend")
        return jsonify(respuesta_json)
    
    except json.JSONDecodeError as e:
        print(f"[ERROR] No se pudo parsear JSON: {str(e)}")
        print(f"[ERROR] Respuesta recibida: {respuesta_texto}")
        return jsonify({
            'mensaje': 'Lo siento, hubo un error al procesar la respuesta. Por favor intenta de nuevo.',
            'opciones': []
        }), 500
    
    except Exception as e:
        print(f"[ERROR] Error en chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'mensaje': f'Lo siento, hubo un error: {str(e)}',
            'opciones': []
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
