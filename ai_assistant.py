# ai_assistant_improved.py - Sistema mejorado con reglas de composición y validación
# Arquitectura: LLM selecciona → Python calcula → Python valida reglas → Python ajusta

from openai import OpenAI
import os
from datetime import datetime, timedelta
from collections import defaultdict
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ============================================================================
# REGLAS DE COMPOSICIÓN
# ============================================================================

REGLAS_COMPOSICION = {
    "fiesta": {
        "min_snacks": 3,  # Mínimo 3 tipos diferentes de snacks
        "max_alcohol_tipos": 3,  # Máximo 3 tipos de alcohol
        "ratio_snacks_alcohol": 1.5,  # 1.5x más items de snacks que alcohol
        "productos_recomendados": ["S001", "S002", "S003", "S004", "S005", "S008"],  # Papas, galletas, maní, chocolates, TUC, barras
        "productos_evitar": ["S007", "BB001", "BB002", "BB003", "L001"],  # Gomitas, pañales, etc.
        "descripcion": "Fiesta de ADULTOS: Balance entre snacks y bebidas alcohólicas"
    },
    "fiesta_infantil": {
        "min_snacks": 4,
        "max_alcohol_tipos": 0,  # SIN alcohol
        "productos_recomendados": ["S001", "S002", "S004", "S007", "S009"],  # Incluir gomitas y snacks infantiles
        "productos_evitar": ["S010",  # Bebidas energéticas
                           "S011", "S012", "S013", "S014", "S015", "S016", "S017", "S018", "S019", "S020", "S021", "S022", "S023", "S024", "S025"],  # Todo el alcohol
        "descripcion": "Fiesta INFANTIL: Solo snacks y bebidas sin alcohol ni energéticas"
    },
    "hogar": {
        "min_limpieza": 4,
        "ratio_limpieza_otros": 2.0,
        "productos_recomendados": ["L001", "L002", "L003", "L004", "L006", "L009"],
        "descripcion": "Hogar: Productos de limpieza esenciales"
    },
    "bebe": {
        "min_productos": 5,
        "productos_recomendados": ["BB001", "BB002", "BB003", "BB004", "BB005"],
        "productos_evitar": ["S011", "S012", "S013", "S014", "S015"],  # Alcohol
        "descripcion": "Bebé: Productos de cuidado infantil"
    },
    "cuidado_personal": {
        "min_productos": 4,
        "productos_recomendados": ["B001", "B002", "B003", "B004", "B005"],
        "descripcion": "Cuidado personal: Productos de belleza y cuidado"
    }
}

# ============================================================================
# EXTRACTOR DE CONTEXTO MEJORADO
# ============================================================================

CONTEXTO_EXTRACTION_PROMPT = """Analiza la conversación y extrae información en formato JSON.

CONVERSACIÓN:
{conversacion_completa}

Extrae:
1. presupuesto: número entero, null si no se menciona
2. tipo_compra: "fiesta", "hogar", "bebe", "cuidado_personal", "mixto", null
3. categoria: "limpieza", "snacks", "belleza", "bebe", "mixto", null
4. es_fiesta_infantil: true/false/null (solo si es fiesta)
5. limite_alcohol: número entero o null
6. cantidad_personas: número o null
7. ocasion_especifica: "cumpleaños", "reunion_amigos", "cena_familiar", "picnic", null
8. preferencias_explicitas: lista de strings con preferencias mencionadas
9. restricciones: lista de restricciones mencionadas

IMPORTANTE:
- Si mencionan "niños", "infantil", "cumpleaños de niños" → es_fiesta_infantil: true
- Si mencionan "adultos", "mayores de edad", "18+" → es_fiesta_infantil: false
- Si no especifican edad para fiesta → es_fiesta_infantil: null

Responde en JSON:
{{
    "presupuesto": null,
    "tipo_compra": null,
    "categoria": null,
    "es_fiesta_infantil": null,
    "limite_alcohol": null,
    "cantidad_personas": null,
    "ocasion_especifica": null,
    "preferencias_explicitas": [],
    "restricciones": []
}}"""

def extraer_contexto_conversacion(mensaje_usuario, historial):
    conversacion_completa = ""
    for msg in historial:
        role = "Usuario" if msg.get('role') == 'user' else "Asistente"
        conversacion_completa += f"{role}: {msg.get('content', '')}\n"
    conversacion_completa += f"Usuario: {mensaje_usuario}\n"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": CONTEXTO_EXTRACTION_PROMPT.format(conversacion_completa=conversacion_completa)}],
            temperature=0.1,
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        contexto = json.loads(response.choices[0].message.content)
        print(f"[IA] Contexto extraído: {contexto}")
        return contexto
        
    except Exception as e:
        print(f"[ERROR] Error extracción: {e}")
        return {
            "presupuesto": None,
            "tipo_compra": None,
            "categoria": None,
            "es_fiesta_infantil": None,
            "limite_alcohol": None,
            "cantidad_personas": None,
            "ocasion_especifica": None,
            "preferencias_explicitas": [],
            "restricciones": []
        }

# ============================================================================
# VALIDADOR DE CONTEXTO COMPLETO (NUEVO)
# ============================================================================

def validar_contexto_completo(contexto, historial):
    """
    Determina si necesitamos más información CRÍTICA antes de generar kits
    Retorna: (es_completo: bool, pregunta_necesaria: str|None)
    """
    
    # Regla 1: Si no hay presupuesto, SIEMPRE preguntar
    if not contexto.get('presupuesto'):
        return False, "¿Cuál es tu presupuesto aproximado?"
    
    # Regla 2: Si no hay tipo de compra NI categoría, preguntar
    if not contexto.get('tipo_compra') and not contexto.get('categoria'):
        return False, "¿Para qué tipo de ocasión necesitas el kit? (fiesta, hogar, bebé, cuidado personal)"
    
    # Regla 3: Si es fiesta pero no sabemos si es infantil
    if contexto.get('tipo_compra') == 'fiesta' and contexto.get('es_fiesta_infantil') is None:
        # Solo preguntar si no hemos preguntado antes
        preguntas_edad = ['edad', 'infantil', 'adultos', 'niños', 'mayores']
        if not any(any(palabra in msg.get('content', '').lower() for palabra in preguntas_edad) 
                   for msg in historial if msg.get('role') == 'assistant'):
            return False, "¿Es una fiesta infantil o para adultos?"
    
    # Regla 4: Si menciona fiesta con presupuesto alto pero no sabemos cantidad de personas (opcional)
    if (contexto.get('tipo_compra') == 'fiesta' and 
        contexto.get('presupuesto', 0) > 50000 and 
        not contexto.get('cantidad_personas')):
        # Preguntar solo si no lo hemos hecho
        if not any('personas' in msg.get('content', '').lower() or 'cuántos' in msg.get('content', '').lower()
                   for msg in historial if msg.get('role') == 'assistant'):
            return False, "¿Para cuántas personas aproximadamente?"
    
    # Contexto suficiente
    return True, None

# ============================================================================
# MOTOR DE REGLAS DE COMPOSICIÓN (NUEVO)
# ============================================================================

def aplicar_reglas_composicion(productos_seleccionados, contexto, productos_db):
    """
    Valida y ajusta productos según reglas de composición
    Retorna: (productos_ajustados, errores_encontrados)
    """
    tipo_compra = contexto.get('tipo_compra', 'general')
    es_infantil = contexto.get('es_fiesta_infantil', False)
    
    # Determinar reglas aplicables
    if es_infantil:
        reglas = REGLAS_COMPOSICION.get('fiesta_infantil', {})
        tipo_regla = 'fiesta_infantil'
    else:
        reglas = REGLAS_COMPOSICION.get(tipo_compra, {})
        tipo_regla = tipo_compra
    
    errores = []
    
    print(f"[REGLAS] Aplicando reglas de composición para: {tipo_regla}")
    
    # Regla 1: Eliminar alcohol y bebidas energéticas en fiestas infantiles
    if es_infantil:
        alcohol_ids = [f"S{str(i).zfill(3)}" for i in range(11, 26)]
        productos_prohibidos = [p for p in productos_seleccionados if p['id'] in alcohol_ids or p['id'] == 'S010']  # S010 es bebida energética
        
        if productos_prohibidos:
            errores.append(f"Eliminando {len(productos_prohibidos)} productos no aptos para niños (alcohol/energéticas)")
            productos_seleccionados[:] = [p for p in productos_seleccionados if p['id'] not in alcohol_ids and p['id'] != 'S010']
    
    # Regla 2: Balancear snacks vs alcohol (para fiestas de adultos)
    if tipo_compra == 'fiesta' and not es_infantil:
        snacks_no_alcohol = [p for p in productos_seleccionados if p['id'].startswith('S') and int(p['id'][1:]) <= 10]
        alcohol = [p for p in productos_seleccionados if p['id'].startswith('S') and int(p['id'][1:]) >= 11]
        
        count_snacks = sum(p.get('cantidad', 1) for p in snacks_no_alcohol)
        count_alcohol = sum(p.get('cantidad', 1) for p in alcohol)
        
        ratio_minimo = reglas.get('ratio_snacks_alcohol', 1.5)
        
        # Si hay alcohol pero pocos snacks, agregar más snacks
        if count_alcohol > 0 and (count_snacks == 0 or count_snacks / count_alcohol < ratio_minimo):
            errores.append(f"Desbalance snacks/alcohol (ratio: {count_snacks}/{count_alcohol}) - agregando más snacks")
            
            # Agregar snacks recomendados que no estén ya
            productos_agregar = []
            for prod_id in reglas.get('productos_recomendados', [])[:3]:
                if not any(p['id'] == prod_id for p in productos_seleccionados):
                    productos_agregar.append({'id': prod_id, 'cantidad': 2})
            
            productos_seleccionados.extend(productos_agregar)
            print(f"[REGLAS] Agregados {len(productos_agregar)} snacks para balance")
        
        # Limitar tipos de alcohol
        max_alcohol_tipos = reglas.get('max_alcohol_tipos', 3)
        tipos_alcohol = len(alcohol)
        
        if tipos_alcohol > max_alcohol_tipos:
            errores.append(f"Demasiados tipos de alcohol ({tipos_alcohol} > {max_alcohol_tipos}) - reduciendo")
            # Mantener solo los primeros N tipos
            alcohol_ids_mantener = [p['id'] for p in alcohol[:max_alcohol_tipos]]
            productos_seleccionados[:] = [
                p for p in productos_seleccionados 
                if not (p['id'].startswith('S') and int(p['id'][1:]) >= 11) or p['id'] in alcohol_ids_mantener
            ]
    
    # Regla 3: Evitar productos no apropiados
    productos_evitar = reglas.get('productos_evitar', [])
    productos_inapropiados = [p for p in productos_seleccionados if p['id'] in productos_evitar]
    
    if productos_inapropiados:
        errores.append(f"Eliminando {len(productos_inapropiados)} productos inapropiados para {tipo_regla}")
        productos_seleccionados[:] = [p for p in productos_seleccionados if p['id'] not in productos_evitar]
    
    # Regla 4: Mínimo de productos específicos
    if 'min_snacks' in reglas:
        snacks_actuales = [p for p in productos_seleccionados if p['id'].startswith('S') and int(p['id'][1:]) <= 10]
        if len(snacks_actuales) < reglas['min_snacks']:
            errores.append(f"Pocos snacks ({len(snacks_actuales)} < {reglas['min_snacks']}) - agregando más")
            # Agregar snacks recomendados
            for prod_id in reglas.get('productos_recomendados', []):
                if not any(p['id'] == prod_id for p in productos_seleccionados):
                    productos_seleccionados.append({'id': prod_id, 'cantidad': 1})
                    if len([p for p in productos_seleccionados if p['id'].startswith('S') and int(p['id'][1:]) <= 10]) >= reglas['min_snacks']:
                        break
    
    print(f"[REGLAS] Aplicadas {len(errores)} correcciones")
    return productos_seleccionados, errores

# ============================================================================
# GENERADOR DE SELECCIÓN DE PRODUCTOS MEJORADO
# ============================================================================

def generar_seleccion_productos(contexto, productos_info, tipo_kit):
    """El LLM solo selecciona productos con instrucciones más específicas"""
    
    productos_json = json.dumps(productos_info, ensure_ascii=False, indent=2)
    
    presupuesto = contexto.get('presupuesto', 30000)
    tipo_compra = contexto.get('tipo_compra', 'general')
    es_infantil = contexto.get('es_fiesta_infantil', False)
    cantidad_personas = contexto.get('cantidad_personas')
    
    # Determinar reglas aplicables
    if es_infantil:
        reglas_aplicables = REGLAS_COMPOSICION['fiesta_infantil']
        descripcion_reglas = f"""Fiesta INFANTIL:
- SIN alcohol bajo ninguna circunstancia
- Mínimo {reglas_aplicables['min_snacks']} tipos de snacks diferentes
- Priorizar snacks dulces y salados que gustan a niños
- Incluir bebidas sin alcohol (S010)
- Productos recomendados: {', '.join(reglas_aplicables['productos_recomendados'][:5])}"""
    elif tipo_compra == 'fiesta':
        reglas_aplicables = REGLAS_COMPOSICION['fiesta']
        descripcion_reglas = f"""Fiesta de ADULTOS:
- Mínimo {reglas_aplicables['min_snacks']} tipos de snacks diferentes
- Máximo {reglas_aplicables['max_alcohol_tipos']} tipos de alcohol DIFERENTES
- RATIO CRÍTICO: Por cada bebida alcohólica, incluir 1.5x más snacks para comer
- Ejemplo: Si incluyes 2 vinos, debes tener al menos 3 snacks diferentes
- Priorizar snacks para "picotear": {', '.join(reglas_aplicables['productos_recomendados'][:5])}
- Evitar gomitas (muy infantil para adultos)"""
    elif tipo_compra == 'hogar':
        reglas_aplicables = REGLAS_COMPOSICION['hogar']
        descripcion_reglas = f"""Kit de Hogar:
- Mínimo {reglas_aplicables['min_limpieza']} productos de limpieza
- Priorizar esenciales: {', '.join(reglas_aplicables['productos_recomendados'][:5])}"""
    elif tipo_compra == 'bebe':
        reglas_aplicables = REGLAS_COMPOSICION['bebe']
        descripcion_reglas = f"""Kit de Bebé:
- Productos de cuidado infantil
- Priorizar: {', '.join(reglas_aplicables['productos_recomendados'][:5])}"""
    else:
        reglas_aplicables = {}
        descripcion_reglas = "Kit general balanceado"
    
    # Ajustar presupuesto objetivo según tipo de kit
    if tipo_kit == "economico":
        presupuesto_objetivo = int(presupuesto * 0.65)
        descripcion = "económico con buena variedad"
    elif tipo_kit == "premium":
        presupuesto_objetivo = int(presupuesto * 0.90)
        descripcion = "premium con productos de calidad"
    else:  # equilibrado
        presupuesto_objetivo = int(presupuesto * 0.85)
        descripcion = "equilibrado"
    
    # Ajuste por cantidad de personas
    nota_personas = ""
    if cantidad_personas:
        if cantidad_personas <= 5:
            nota_personas = f"Para {cantidad_personas} personas: Cantidades moderadas (1-2 unidades por producto)"
        elif cantidad_personas <= 10:
            nota_personas = f"Para {cantidad_personas} personas: Cantidades generosas (2-3 unidades por producto)"
        else:
            nota_personas = f"Para {cantidad_personas} personas: Cantidades abundantes (3-4 unidades por producto)"
    
    prompt = f"""Eres un selector EXPERTO de productos para kits. Tu trabajo es elegir productos que la gente REALMENTE usaría en situaciones reales.

PRODUCTOS DISPONIBLES:
{productos_json}

CONTEXTO:
- Tipo: {tipo_compra}
- Presupuesto objetivo: ${presupuesto_objetivo:,} (aproximado)
- Kit: {descripcion}
{nota_personas}

REGLAS DE COMPOSICIÓN CRÍTICAS:
{descripcion_reglas}

REGLAS GENERALES:
1. Variedad: 6-10 productos DIFERENTES
2. Cantidades realistas: 1-4 unidades por producto
3. Piensa: "¿Yo compraría este kit para esta ocasión?" - Si no, ajusta
4. Balance: No todo caro ni todo barato

EJEMPLOS DE BUENOS KITS:
- Fiesta adultos $30k: 2x Papas Lays (S001), 2x Galletas Sahne-Nuss (S002), 1x Maní (S003), 1x Chocolates (S004), 1x Vino Concha y Toro (S017), 1x Pack Cerveza Corona (S014)
- Fiesta infantil $25k: 3x Papas Lays (S001), 2x Galletas (S002), 2x Chocolates (S004), 2x Gomitas (S007), 1x Palomitas (S009), 2x Red Bull sin alcohol (S010)
- Hogar $20k: 1x Detergente Drive (L001), 1x Cloro Clorinda (L002), 1x Papel higiénico (L006), 1x Jabón líquido (L004), 1x Bolsas basura (L009)

TU TAREA: Selecciona productos que sumen aproximadamente ${presupuesto_objetivo:,}

NO calcules precios exactos, solo selecciona productos apropiados y balanceados.

Responde en JSON:
{{
    "nombre": "Nombre descriptivo del kit",
    "productos": [
        {{"id": "S001", "cantidad": 2}},
        {{"id": "S003", "cantidad": 3}}
    ],
    "descripcion": "Por qué es buena opción (máximo 2 líneas)"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,  # Bajado para más consistencia
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        seleccion = json.loads(response.choices[0].message.content)
        return seleccion
        
    except Exception as e:
        print(f"[ERROR] Error generando selección: {e}")
        return None

# ============================================================================
# AJUSTADOR AUTOMÁTICO
# ============================================================================

def calcular_precio_kit(productos_seleccionados, productos_db):
    """Calcula el precio real del kit"""
    total = 0
    for item in productos_seleccionados:
        producto = next((p for p in productos_db if p['id'] == item['id']), None)
        if producto:
            total += producto['precio'] * item.get('cantidad', 1)
    return total

def ajustar_kit_a_presupuesto(seleccion, presupuesto_max, productos_db, contexto):
    """Ajusta automáticamente el kit para que quepa en el presupuesto"""
    productos = seleccion.get('productos', [])
    
    precio_actual = calcular_precio_kit(productos, productos_db)
    print(f"[AJUSTE] Precio inicial: ${precio_actual:,} | Presupuesto: ${presupuesto_max:,}")
    
    if precio_actual <= presupuesto_max:
        return productos, precio_actual
    
    max_intentos = 10
    intento = 0
    
    while precio_actual > presupuesto_max and intento < max_intentos and len(productos) > 2:
        intento += 1
        
        productos_con_precio = []
        for item in productos:
            producto = next((p for p in productos_db if p['id'] == item['id']), None)
            if producto:
                precio_total_item = producto['precio'] * item.get('cantidad', 1)
                productos_con_precio.append({
                    'item': item,
                    'precio_unitario': producto['precio'],
                    'precio_total': precio_total_item
                })
        
        productos_con_precio.sort(key=lambda x: x['precio_total'], reverse=True)
        
        if productos_con_precio:
            mas_caro = productos_con_precio[0]['item']
            
            if mas_caro['cantidad'] > 1:
                mas_caro['cantidad'] -= 1
                print(f"[AJUSTE] Reduciendo {mas_caro['id']} a cantidad {mas_caro['cantidad']}")
            else:
                productos.remove(mas_caro)
                print(f"[AJUSTE] Eliminando {mas_caro['id']}")
        
        precio_actual = calcular_precio_kit(productos, productos_db)
    
    print(f"[AJUSTE] Precio final: ${precio_actual:,}")
    return productos, precio_actual

def validar_restricciones(productos, contexto, productos_db):
    """Valida y corrige restricciones básicas"""
    errores = []
    
    # Validación de alcohol y bebidas energéticas en fiesta infantil (redundante con reglas, pero por seguridad)
    if contexto.get('es_fiesta_infantil'):
        alcohol_ids = [f"S{str(i).zfill(3)}" for i in range(11, 26)]
        tiene_alcohol = any(p['id'] in alcohol_ids for p in productos)
        tiene_energeticas = any(p['id'] == 'S010' for p in productos)  # S010 es bebida energética
        
        if tiene_alcohol or tiene_energeticas:
            errores.append("Tiene alcohol o bebidas energéticas en fiesta infantil (validación de seguridad)")
            productos[:] = [p for p in productos if p['id'] not in alcohol_ids and p['id'] != 'S010']
    
    # Validación de límite de alcohol
    if contexto.get('limite_alcohol') is not None:
        alcohol_ids = [f"S{str(i).zfill(3)}" for i in range(11, 26)]
        tipos_alcohol = set(p['id'] for p in productos if p['id'] in alcohol_ids)
        
        if len(tipos_alcohol) > contexto['limite_alcohol']:
            errores.append(f"Excede límite de alcohol ({len(tipos_alcohol)} > {contexto['limite_alcohol']})")
            mantener = list(tipos_alcohol)[:contexto['limite_alcohol']]
            productos[:] = [p for p in productos if p['id'] not in alcohol_ids or p['id'] in mantener]
    
    return len(errores) == 0, errores

# ============================================================================
# GENERADOR DE 3 KITS MEJORADO
# ============================================================================

def generar_3_kits_validos(contexto, productos_info):
    """Genera 3 kits válidos: LLM selecciona → Python ajusta → Python valida reglas"""
    kits_validos = []
    tipos = ["equilibrado", "economico", "premium"]
    presupuesto_max = contexto.get('presupuesto', 30000)
    
    for tipo in tipos:
        print(f"\n[KIT] Generando kit {tipo}...")
        
        # Paso 1: LLM selecciona productos
        seleccion = generar_seleccion_productos(contexto, productos_info, tipo)
        
        if not seleccion:
            continue
        
        # Paso 2: Python ajusta a presupuesto
        productos_ajustados, precio_ajustado = ajustar_kit_a_presupuesto(
            seleccion,
            presupuesto_max,
            productos_info,
            contexto
        )
        
        # Paso 3: NUEVO - Aplicar reglas de composición
        productos_con_reglas, errores_composicion = aplicar_reglas_composicion(
            productos_ajustados.copy(),  # Copia para no modificar el original hasta confirmar
            contexto,
            productos_info
        )
        
        # Paso 4: Re-ajustar si las reglas agregaron productos que exceden presupuesto
        if calcular_precio_kit(productos_con_reglas, productos_info) > presupuesto_max:
            productos_finales, precio_final = ajustar_kit_a_presupuesto(
                {'productos': productos_con_reglas},
                presupuesto_max,
                productos_info,
                contexto
            )
        else:
            productos_finales = productos_con_reglas
            precio_final = calcular_precio_kit(productos_finales, productos_info)
        
        # Paso 5: Validar restricciones básicas
        es_valido, errores = validar_restricciones(productos_finales, contexto, productos_info)
        
        # Recalcular precio final
        precio_final = calcular_precio_kit(productos_finales, productos_info)
        
        if errores + errores_composicion:
            print(f"[KIT] Correcciones aplicadas: {errores + errores_composicion}")
        
        kit = {
            "nombre": seleccion.get('nombre', f'Kit {tipo.title()}'),
            "productos": productos_finales,
            "precio_total": precio_final,
            "descripcion": seleccion.get('descripcion', '')
        }
        
        kits_validos.append(kit)
        print(f"[KIT] ✓ {tipo.title()}: ${precio_final:,} ({len(productos_finales)} productos)")
    
    return kits_validos

# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    def __init__(self):
        self.user_requests = defaultdict(list)
        self.MAX_REQUESTS_PER_HOUR = 20
        self.MAX_REQUESTS_PER_SESSION = 10
        
    def can_make_request(self, session_id, current_turn):
        now = datetime.now()
        if current_turn >= self.MAX_REQUESTS_PER_SESSION:
            return False, "Has alcanzado el límite de mensajes por sesión."
        session_requests = self.user_requests[session_id]
        recent_requests = [req for req in session_requests if now - req < timedelta(hours=1)]
        if len(recent_requests) >= self.MAX_REQUESTS_PER_HOUR:
            return False, "Has alcanzado el límite de mensajes por hora."
        self.user_requests[session_id].append(now)
        self.user_requests[session_id] = recent_requests + [now]
        return True, None

# ============================================================================
# ROUTING
# ============================================================================

ROUTING_PROMPT = """Clasifica el mensaje en UNA categoría:

1. SALUDO - Solo saluda
2. DESPEDIDA - Solo se despide
3. CREAR_KIT - Quiere crear un kit (menciona productos, presupuesto, necesidades)
4. INFO_PRODUCTOS - Pregunta genérica sobre productos
5. FUERA_CONTEXTO - No relacionado con compras

IMPORTANTE:
"Snacks para fiesta, $30,000" = CREAR_KIT
"Necesito limpieza" = CREAR_KIT
"¿Qué tienen?" = INFO_PRODUCTOS
"Hola" = SALUDO

Mensaje: "{mensaje}"

Responde solo: SALUDO, DESPEDIDA, CREAR_KIT, INFO_PRODUCTOS o FUERA_CONTEXTO"""

def clasificar_intencion(mensaje, historial=None):
    if historial and len(historial) > 0 and len(mensaje.strip()) < 20:
        for msg in reversed(historial):
            if msg.get('role') == 'assistant' and '?' in msg.get('content', ''):
                return "CREAR_KIT"
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": ROUTING_PROMPT.format(mensaje=mensaje)}],
            temperature=0.1,
            max_tokens=20
        )
        
        intencion = response.choices[0].message.content.strip().upper()
        
        if intencion not in ["SALUDO", "DESPEDIDA", "CREAR_KIT", "INFO_PRODUCTOS", "FUERA_CONTEXTO"]:
            return "CREAR_KIT"
        
        print(f"[ROUTING] '{mensaje[:50]}' → {intencion}")
        return intencion
        
    except Exception as e:
        print(f"[ERROR] Routing: {e}")
        return "CREAR_KIT"

# ============================================================================
# FUNCIÓN PRINCIPAL MEJORADA
# ============================================================================

def procesar_mensaje_ia(mensaje_usuario, historial, productos_info, session_id=None, current_turn=0):
    """
    Función principal mejorada con validación de contexto completo
    """
    rate_limiter = RateLimiter()
    if session_id:
        puede, error = rate_limiter.can_make_request(session_id, current_turn)
        if not puede:
            return {"mensaje": error, "opciones": [], "limite_alcanzado": True}
    
    # Paso 1: Extraer contexto
    contexto = extraer_contexto_conversacion(mensaje_usuario, historial)
    
    # Paso 2: Clasificar intención
    intencion = clasificar_intencion(mensaje_usuario, historial)
    print(f"[IA] Intención: {intencion}")
    
    # Paso 3: Manejar intenciones simples
    if intencion == "SALUDO":
        return {"mensaje": "¡Hola! 👋 Soy tu asistente de KitBox. Dime qué necesitas y tu presupuesto, y te armaré el kit perfecto.", "opciones": []}
    elif intencion == "DESPEDIDA":
        return {"mensaje": "¡Hasta pronto! 😊 Vuelve cuando necesites armar otro kit.", "opciones": []}
    elif intencion == "FUERA_CONTEXTO":
        return {"mensaje": "Solo ayudo con kits de productos. ¿Qué tipo de kit necesitas? (fiesta, hogar, bebé, cuidado personal)", "opciones": []}
    elif intencion == "INFO_PRODUCTOS":
        return {"mensaje": "Tenemos productos de limpieza, snacks, belleza y bebé. ¿Para qué ocasión buscas armar un kit?", "opciones": []}
    
    # Paso 4: NUEVO - Validar si tenemos contexto completo
    es_completo, pregunta = validar_contexto_completo(contexto, historial)
    
    if not es_completo:
        print(f"[IA] Contexto incompleto - preguntando: {pregunta}")
        return {"mensaje": pregunta, "opciones": []}
    
    # Paso 5: Generar kits con todas las mejoras
    try:
        print(f"\n[IA] Generando 3 kits para ${contexto.get('presupuesto'):,}")
        print(f"[IA] Tipo: {contexto.get('tipo_compra')} | Infantil: {contexto.get('es_fiesta_infantil')}")
        
        kits = generar_3_kits_validos(contexto, productos_info)
        
        if not kits:
            return {"mensaje": "No pude generar kits. Intenta ajustar tu presupuesto o especificar mejor tus necesidades.", "opciones": []}
        
        # Mensaje personalizado según contexto
        if contexto.get('es_fiesta_infantil'):
            mensaje = "¡Perfecto! He preparado 3 opciones especiales para fiesta infantil (sin alcohol):"
        elif contexto.get('tipo_compra') == 'fiesta':
            mensaje = "¡Perfecto! He preparado 3 opciones balanceadas para tu fiesta:"
        else:
            mensaje = "¡Perfecto! He preparado 3 opciones que se ajustan a tu presupuesto:"
        
        return {
            "mensaje": mensaje,
            "opciones": kits
        }
        
    except Exception as e:
        print(f"[ERROR] Generando kits: {e}")
        import traceback
        traceback.print_exc()
        return {"mensaje": "Hubo un error al generar los kits. ¿Podrías intentar de nuevo con más detalles?", "opciones": []}

def generar_session_id():
    import uuid
    return str(uuid.uuid4())