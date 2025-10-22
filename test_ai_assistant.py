# test_ai_assistant.py - Suite de tests para el sistema mejorado
# Ejecutar con: python test_ai_assistant.py

import json
from ai_assistant import (
    extraer_contexto_conversacion,
    validar_contexto_completo,
    aplicar_reglas_composicion,
    calcular_precio_kit,
    REGLAS_COMPOSICION
)

# Mock de productos para testing
PRODUCTOS_TEST = [
    {'id': 'S001', 'nombre': 'Papas fritas Lays 150g', 'precio': 1990, 'categoria': 'snacks'},
    {'id': 'S002', 'nombre': 'Galletas Sahne-Nuss pack x3', 'precio': 2790, 'categoria': 'snacks'},
    {'id': 'S003', 'nombre': 'Maní Ebner 200g', 'precio': 2290, 'categoria': 'snacks'},
    {'id': 'S004', 'nombre': 'Chocolates Ambrosoli pack x6', 'precio': 3990, 'categoria': 'snacks'},
    {'id': 'S007', 'nombre': 'Gomitas Mogul pack x2', 'precio': 2190, 'categoria': 'snacks'},
    {'id': 'S010', 'nombre': 'Bebida Red Bull pack x4', 'precio': 4990, 'categoria': 'snacks'},
    {'id': 'S011', 'nombre': 'Vino Casillero del Diablo 750ml', 'precio': 8990, 'categoria': 'snacks'},
    {'id': 'S017', 'nombre': 'Vino Concha y Toro 750ml', 'precio': 4990, 'categoria': 'snacks'},
    {'id': 'S014', 'nombre': 'Cerveza Corona 355ml', 'precio': 1890, 'categoria': 'snacks'},
    {'id': 'L001', 'nombre': 'Detergente líquido Drive 1L', 'precio': 3990, 'categoria': 'limpieza'},
]

def test_validacion_contexto_completo():
    """Test 1: Validación de contexto completo"""
    print("\n" + "="*60)
    print("TEST 1: Validación de Contexto Completo")
    print("="*60)
    
    # Caso 1: Sin presupuesto
    contexto = {"presupuesto": None, "tipo_compra": "fiesta"}
    es_completo, pregunta = validar_contexto_completo(contexto, [])
    assert not es_completo, "❌ Debería detectar que falta presupuesto"
    assert "presupuesto" in pregunta.lower(), "❌ La pregunta debería mencionar presupuesto"
    print("✅ Caso 1 Pasado: Detecta falta de presupuesto")
    
    # Caso 2: Sin tipo de compra
    contexto = {"presupuesto": 30000, "tipo_compra": None, "categoria": None}
    es_completo, pregunta = validar_contexto_completo(contexto, [])
    assert not es_completo, "❌ Debería detectar que falta tipo de compra"
    print("✅ Caso 2 Pasado: Detecta falta de tipo de compra")
    
    # Caso 3: Fiesta sin especificar si es infantil
    contexto = {"presupuesto": 30000, "tipo_compra": "fiesta", "es_fiesta_infantil": None}
    es_completo, pregunta = validar_contexto_completo(contexto, [])
    assert not es_completo, "❌ Debería preguntar si es fiesta infantil"
    assert "infantil" in pregunta.lower() or "adultos" in pregunta.lower(), "❌ Debería preguntar edad"
    print("✅ Caso 3 Pasado: Pregunta si es fiesta infantil")
    
    # Caso 4: Contexto completo
    contexto = {"presupuesto": 30000, "tipo_compra": "fiesta", "es_fiesta_infantil": False}
    es_completo, pregunta = validar_contexto_completo(contexto, [])
    assert es_completo, "❌ Contexto debería estar completo"
    assert pregunta is None, "❌ No debería haber pregunta"
    print("✅ Caso 4 Pasado: Contexto completo reconocido")
    
    print("\n✅ TODOS LOS TESTS DE VALIDACIÓN PASARON")

def test_reglas_composicion_fiesta_infantil():
    """Test 2: Reglas de composición para fiesta infantil"""
    print("\n" + "="*60)
    print("TEST 2: Reglas de Composición - Fiesta Infantil")
    print("="*60)
    
    # Kit con alcohol (MALO)
    productos = [
        {'id': 'S001', 'cantidad': 2},
        {'id': 'S002', 'cantidad': 2},
        {'id': 'S011', 'cantidad': 1},  # Alcohol - debe eliminarse
        {'id': 'S017', 'cantidad': 1},  # Alcohol - debe eliminarse
    ]
    
    contexto = {"tipo_compra": "fiesta", "es_fiesta_infantil": True, "presupuesto": 30000}
    
    productos_ajustados, errores = aplicar_reglas_composicion(productos.copy(), contexto, PRODUCTOS_TEST)
    
    # Verificar que se eliminó el alcohol
    alcohol_ids = ['S011', 'S017', 'S012', 'S013', 'S014', 'S015']
    tiene_alcohol = any(p['id'] in alcohol_ids for p in productos_ajustados)
    
    assert not tiene_alcohol, "❌ No debería haber alcohol en fiesta infantil"
    assert len(errores) > 0, "❌ Debería reportar errores de corrección"
    print(f"✅ Alcohol eliminado correctamente. Errores reportados: {len(errores)}")
    print(f"   Productos finales: {[p['id'] for p in productos_ajustados]}")
    
    print("\n✅ TEST DE FIESTA INFANTIL PASADO")

def test_reglas_composicion_fiesta_adultos():
    """Test 3: Reglas de composición para fiesta de adultos"""
    print("\n" + "="*60)
    print("TEST 3: Reglas de Composición - Fiesta Adultos")
    print("="*60)
    
    # Kit desbalanceado: mucho alcohol, pocos snacks
    productos = [
        {'id': 'S001', 'cantidad': 1},  # 1 snack
        {'id': 'S011', 'cantidad': 2},  # 2 vinos
        {'id': 'S017', 'cantidad': 2},  # 2 vinos más
        {'id': 'S014', 'cantidad': 2},  # 2 cervezas
    ]
    
    contexto = {"tipo_compra": "fiesta", "es_fiesta_infantil": False, "presupuesto": 50000}
    
    productos_ajustados, errores = aplicar_reglas_composicion(productos.copy(), contexto, PRODUCTOS_TEST)
    
    # Contar snacks vs alcohol
    snacks = [p for p in productos_ajustados if p['id'].startswith('S') and int(p['id'][1:]) <= 10]
    alcohol = [p for p in productos_ajustados if p['id'].startswith('S') and int(p['id'][1:]) >= 11]
    
    count_snacks = sum(p.get('cantidad', 1) for p in snacks)
    count_alcohol = sum(p.get('cantidad', 1) for p in alcohol)
    
    print(f"   Snacks: {count_snacks} | Alcohol: {count_alcohol}")
    print(f"   Ratio: {count_snacks/count_alcohol if count_alcohol > 0 else 0:.2f}")
    print(f"   Errores corregidos: {len(errores)}")
    
    # Verificar que se agregaron snacks
    assert len(snacks) > 1, "❌ Debería haber agregado más snacks"
    assert len(errores) > 0, "❌ Debería reportar correcciones"
    
    print("✅ Balance de snacks/alcohol corregido")
    print("\n✅ TEST DE FIESTA ADULTOS PASADO")

def test_calculo_precios():
    """Test 4: Cálculo correcto de precios"""
    print("\n" + "="*60)
    print("TEST 4: Cálculo de Precios")
    print("="*60)
    
    productos = [
        {'id': 'S001', 'cantidad': 2},  # 2 x 1990 = 3980
        {'id': 'S002', 'cantidad': 1},  # 1 x 2790 = 2790
        {'id': 'S003', 'cantidad': 3},  # 3 x 2290 = 6870
    ]
    
    precio_total = calcular_precio_kit(productos, PRODUCTOS_TEST)
    precio_esperado = 3980 + 2790 + 6870  # 13640
    
    assert precio_total == precio_esperado, f"❌ Precio incorrecto: {precio_total} != {precio_esperado}"
    print(f"✅ Precio calculado correctamente: ${precio_total:,}")
    
    print("\n✅ TEST DE CÁLCULO DE PRECIOS PASADO")

def test_limite_tipos_alcohol():
    """Test 5: Límite de tipos de alcohol"""
    print("\n" + "="*60)
    print("TEST 5: Límite de Tipos de Alcohol")
    print("="*60)
    
    # Kit con demasiados tipos de alcohol
    productos = [
        {'id': 'S001', 'cantidad': 3},
        {'id': 'S002', 'cantidad': 2},
        {'id': 'S011', 'cantidad': 1},  # Vino 1
        {'id': 'S017', 'cantidad': 1},  # Vino 2
        {'id': 'S014', 'cantidad': 1},  # Cerveza
        {'id': 'S010', 'cantidad': 1},  # Red Bull (no alcohol)
    ]
    
    contexto = {"tipo_compra": "fiesta", "es_fiesta_infantil": False, "presupuesto": 40000}
    
    productos_ajustados, errores = aplicar_reglas_composicion(productos.copy(), contexto, PRODUCTOS_TEST)
    
    # Contar tipos de alcohol
    alcohol = [p for p in productos_ajustados if p['id'].startswith('S') and int(p['id'][1:]) >= 11]
    tipos_alcohol = len(alcohol)
    
    max_permitido = REGLAS_COMPOSICION['fiesta']['max_alcohol_tipos']
    
    print(f"   Tipos de alcohol: {tipos_alcohol} (máximo: {max_permitido})")
    print(f"   Alcohol en kit: {[p['id'] for p in alcohol]}")
    
    assert tipos_alcohol <= max_permitido, f"❌ Demasiados tipos de alcohol: {tipos_alcohol} > {max_permitido}"
    print(f"✅ Límite de tipos de alcohol respetado")
    
    print("\n✅ TEST DE LÍMITE DE ALCOHOL PASADO")

def test_productos_recomendados():
    """Test 6: Productos recomendados por tipo de kit"""
    print("\n" + "="*60)
    print("TEST 6: Productos Recomendados")
    print("="*60)
    
    # Verificar que existen productos recomendados para cada tipo
    tipos = ['fiesta', 'fiesta_infantil', 'hogar', 'bebe', 'cuidado_personal']
    
    for tipo in tipos:
        if tipo in REGLAS_COMPOSICION:
            reglas = REGLAS_COMPOSICION[tipo]
            recomendados = reglas.get('productos_recomendados', [])
            
            assert len(recomendados) > 0, f"❌ {tipo} debería tener productos recomendados"
            print(f"✅ {tipo}: {len(recomendados)} productos recomendados")
    
    print("\n✅ TEST DE PRODUCTOS RECOMENDADOS PASADO")

def test_integracion_completa():
    """Test 7: Integración completa del flujo"""
    print("\n" + "="*60)
    print("TEST 7: Integración Completa del Flujo")
    print("="*60)
    
    # Simular flujo completo: usuario pide kit → sistema valida → aplica reglas
    
    # Paso 1: Usuario pide kit para fiesta infantil
    contexto = {
        "presupuesto": 25000,
        "tipo_compra": "fiesta",
        "es_fiesta_infantil": True,
        "cantidad_personas": 10
    }
    
    # Paso 2: Validar contexto
    es_completo, pregunta = validar_contexto_completo(contexto, [])
    assert es_completo, "❌ Contexto debería estar completo"
    print("✅ Paso 1: Contexto validado")
    
    # Paso 3: Simular selección de productos (con alcohol por error)
    productos = [
        {'id': 'S001', 'cantidad': 3},
        {'id': 'S002', 'cantidad': 2},
        {'id': 'S004', 'cantidad': 2},
        {'id': 'S007', 'cantidad': 1},
        {'id': 'S011', 'cantidad': 1},  # Alcohol - debe eliminarse
    ]
    
    # Paso 4: Aplicar reglas
    productos_ajustados, errores = aplicar_reglas_composicion(productos.copy(), contexto, PRODUCTOS_TEST)
    
    # Verificaciones
    tiene_alcohol = any(p['id'].startswith('S') and int(p['id'][1:]) >= 11 for p in productos_ajustados)
    assert not tiene_alcohol, "❌ No debería haber alcohol después de aplicar reglas"
    print("✅ Paso 2: Reglas aplicadas correctamente")
    
    # Paso 5: Calcular precio
    precio_final = calcular_precio_kit(productos_ajustados, PRODUCTOS_TEST)
    assert precio_final <= contexto['presupuesto'], f"❌ Precio excede presupuesto: {precio_final} > {contexto['presupuesto']}"
    print(f"✅ Paso 3: Precio dentro del presupuesto (${precio_final:,} <= ${contexto['presupuesto']:,})")
    
    print(f"\n   Kit final: {len(productos_ajustados)} productos")
    for p in productos_ajustados:
        producto = next((prod for prod in PRODUCTOS_TEST if prod['id'] == p['id']), None)
        if producto:
            print(f"   - {producto['nombre']} x{p['cantidad']}")
    
    print("\n✅ TEST DE INTEGRACIÓN COMPLETA PASADO")

def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "🧪 "+"="*58 + " 🧪")
    print("🧪" + " "*20 + "SUITE DE TESTS" + " "*25 + "🧪")
    print("🧪 " + "="*58 + " 🧪")
    
    tests = [
        ("Validación de Contexto", test_validacion_contexto_completo),
        ("Fiesta Infantil (Sin Alcohol)", test_reglas_composicion_fiesta_infantil),
        ("Fiesta Adultos (Balance)", test_reglas_composicion_fiesta_adultos),
        ("Cálculo de Precios", test_calculo_precios),
        ("Límite de Tipos de Alcohol", test_limite_tipos_alcohol),
        ("Productos Recomendados", test_productos_recomendados),
        ("Integración Completa", test_integracion_completa),
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            test_func()
            resultados.append((nombre, "✅ PASÓ"))
        except AssertionError as e:
            resultados.append((nombre, f"❌ FALLÓ: {str(e)}"))
        except Exception as e:
            resultados.append((nombre, f"⚠️ ERROR: {str(e)}"))
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*60)
    
    for nombre, resultado in resultados:
        print(f"{resultado.split()[0]} {nombre}")
    
    total = len(resultados)
    pasados = sum(1 for _, r in resultados if "✅" in r)
    fallados = sum(1 for _, r in resultados if "❌" in r)
    errores = sum(1 for _, r in resultados if "⚠️" in r)
    
    print("\n" + "="*60)
    print(f"Total: {total} | ✅ Pasados: {pasados} | ❌ Fallados: {fallados} | ⚠️ Errores: {errores}")
    print("="*60)
    
    if pasados == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON! El sistema está listo.")
    else:
        print("\n⚠️ Algunos tests fallaron. Revisa los errores arriba.")
    
    return pasados == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)