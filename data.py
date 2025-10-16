# data.py - Catálogo de productos y kits predefinidos

"""
PRODUCTOS = {
    "limpieza": [
        {"id": "L001", "nombre": "Detergente líquido 1L", "precio": 3500, "categoria": "limpieza"},
        {"id": "L002", "nombre": "Cloro 1L", "precio": 1800, "categoria": "limpieza"},
        {"id": "L003", "nombre": "Desinfectante multiuso 500ml", "precio": 2200, "categoria": "limpieza"},
        {"id": "L004", "nombre": "Jabón líquido para manos 250ml", "precio": 1500, "categoria": "limpieza"},
        {"id": "L005", "nombre": "Esponjas pack x3", "precio": 1200, "categoria": "limpieza"},
        {"id": "L006", "nombre": "Papel higiénico pack x4", "precio": 2800, "categoria": "limpieza"},
        {"id": "L007", "nombre": "Toallas de papel pack x2", "precio": 2500, "categoria": "limpieza"},
        {"id": "L008", "nombre": "Limpiavidrios 500ml", "precio": 2000, "categoria": "limpieza"},
        {"id": "L009", "nombre": "Bolsas de basura pack x20", "precio": 1900, "categoria": "limpieza"},
        {"id": "L010", "nombre": "Guantes de limpieza", "precio": 1100, "categoria": "limpieza"},
    ],
    "snacks": [
        {"id": "S001", "nombre": "Papas fritas 150g", "precio": 1800, "categoria": "snacks"},
        {"id": "S002", "nombre": "Galletas de chocolate pack x3", "precio": 2500, "categoria": "snacks"},
        {"id": "S003", "nombre": "Maní salado 200g", "precio": 2200, "categoria": "snacks"},
        {"id": "S004", "nombre": "Chocolates variados pack x6", "precio": 3500, "categoria": "snacks"},
        {"id": "S005", "nombre": "Galletas saladas 200g", "precio": 1600, "categoria": "snacks"},
        {"id": "S006", "nombre": "Frutos secos mixtos 150g", "precio": 3800, "categoria": "snacks"},
        {"id": "S007", "nombre": "Gomitas pack x2", "precio": 2000, "categoria": "snacks"},
        {"id": "S008", "nombre": "Barras de cereal pack x6", "precio": 3200, "categoria": "snacks"},
        {"id": "S009", "nombre": "Palomitas de maíz para microondas pack x3", "precio": 2400, "categoria": "snacks"},
        {"id": "S010", "nombre": "Bebida energética pack x4", "precio": 4000, "categoria": "snacks"},
    ],
    "belleza": [
        {"id": "B001", "nombre": "Shampoo 400ml", "precio": 4500, "categoria": "belleza"},
        {"id": "B002", "nombre": "Acondicionador 400ml", "precio": 4500, "categoria": "belleza"},
        {"id": "B003", "nombre": "Crema hidratante facial 50ml", "precio": 6500, "categoria": "belleza"},
        {"id": "B004", "nombre": "Jabón corporal 250ml", "precio": 3200, "categoria": "belleza"},
        {"id": "B005", "nombre": "Desmaquillante 200ml", "precio": 4800, "categoria": "belleza"},
        {"id": "B006", "nombre": "Protector solar facial SPF50", "precio": 8500, "categoria": "belleza"},
        {"id": "B007", "nombre": "Mascarilla capilar 200ml", "precio": 5200, "categoria": "belleza"},
        {"id": "B008", "nombre": "Exfoliante facial 100ml", "precio": 5500, "categoria": "belleza"},
        {"id": "B009", "nombre": "Sérum facial 30ml", "precio": 9800, "categoria": "belleza"},
        {"id": "B010", "nombre": "Toallas húmedas desmaquillantes pack x25", "precio": 3500, "categoria": "belleza"},
    ],
    "bebe": [
        {"id": "BB001", "nombre": "Pañales pack x30", "precio": 12500, "categoria": "bebe"},
        {"id": "BB002", "nombre": "Toallas húmedas pack x80", "precio": 3800, "categoria": "bebe"},
        {"id": "BB003", "nombre": "Shampoo bebé 400ml", "precio": 4200, "categoria": "bebe"},
        {"id": "BB004", "nombre": "Crema para pañal 100g", "precio": 5500, "categoria": "bebe"},
        {"id": "BB005", "nombre": "Jabón líquido bebé 250ml", "precio": 3500, "categoria": "bebe"},
        {"id": "BB006", "nombre": "Aceite corporal bebé 200ml", "precio": 4800, "categoria": "bebe"},
        {"id": "BB007", "nombre": "Algodón pack x100", "precio": 2200, "categoria": "bebe"},
        {"id": "BB008", "nombre": "Colonia bebé 100ml", "precio": 6500, "categoria": "bebe"},
        {"id": "BB009", "nombre": "Protector solar bebé SPF50", "precio": 9500, "categoria": "bebe"},
        {"id": "BB010", "nombre": "Cotonitos pack x75", "precio": 1800, "categoria": "bebe"},
    ]
}
"""
PRODUCTOS = {
    "limpieza": [
        {"id": "L001", "nombre": "Detergente líquido Drive 1L", "precio": 3990, "categoria": "limpieza"},
        {"id": "L002", "nombre": "Cloro Clorinda 1L", "precio": 1490, "categoria": "limpieza"},
        {"id": "L003", "nombre": "Limpiador multiuso Lysol 500ml", "precio": 2690, "categoria": "limpieza"},
        {"id": "L004", "nombre": "Jabón líquido Lifebuoy 250ml", "precio": 1890, "categoria": "limpieza"},
        {"id": "L005", "nombre": "Esponjas Scotch-Brite pack x3", "precio": 1990, "categoria": "limpieza"},
        {"id": "L006", "nombre": "Papel higiénico Elite pack x4", "precio": 3290, "categoria": "limpieza"},
        {"id": "L007", "nombre": "Toallas de papel Nova pack x2", "precio": 2790, "categoria": "limpieza"},
        {"id": "L008", "nombre": "Limpiavidrios Windex 500ml", "precio": 2490, "categoria": "limpieza"},
        {"id": "L009", "nombre": "Bolsas de basura Gala pack x20", "precio": 2190, "categoria": "limpieza"},
        {"id": "L010", "nombre": "Guantes de látex pack x2", "precio": 1290, "categoria": "limpieza"}
    ],
    "snacks": [
        {"id": "S001", "nombre": "Papas fritas Lays 150g", "precio": 1990, "categoria": "snacks"},
        {"id": "S002", "nombre": "Galletas Sahne-Nuss pack x3", "precio": 2790, "categoria": "snacks"},
        {"id": "S003", "nombre": "Maní Ebner 200g", "precio": 2290, "categoria": "snacks"},
        {"id": "S004", "nombre": "Chocolates Ambrosoli pack x6", "precio": 3990, "categoria": "snacks"},
        {"id": "S005", "nombre": "Galletas TUC 200g", "precio": 1890, "categoria": "snacks"},
        {"id": "S006", "nombre": "Mezcla de frutos secos 150g", "precio": 4290, "categoria": "snacks"},
        {"id": "S007", "nombre": "Gomitas Mogul pack x2", "precio": 2190, "categoria": "snacks"},
        {"id": "S008", "nombre": "Barras de cereal Granola pack x6", "precio": 3490, "categoria": "snacks"},
        {"id": "S009", "nombre": "Palomitas Act II pack x3", "precio": 2690, "categoria": "snacks"},
        {"id": "S010", "nombre": "Bebida Red Bull pack x4", "precio": 4990, "categoria": "snacks"},
        {"id": "S011", "nombre": "Vino Casillero del Diablo 750ml", "precio": 8990, "categoria": "snacks"},
        {"id": "S012", "nombre": "Pisco Alto del Carmen 35° 750ml", "precio": 7990, "categoria": "snacks"},
        {"id": "S013", "nombre": "Champagne Brut Imperial 750ml", "precio": 15990, "categoria": "snacks"},
        {"id": "S014", "nombre": "Cerveza Corona 355ml", "precio": 1890, "categoria": "snacks"},
        {"id": "S015", "nombre": "Ron Bacardí Carta Blanca 750ml", "precio": 11990, "categoria": "snacks"},
        {"id": "S016", "nombre": "Whisky Johnnie Walker Red Label 750ml", "precio": 14990, "categoria": "snacks"},
        {"id": "S017", "nombre": "Vino Concha y Toro 750ml", "precio": 4990, "categoria": "snacks"},
        {"id": "S018", "nombre": "Pisco Mistral 35° 750ml", "precio": 6990, "categoria": "snacks"},
        {"id": "S019", "nombre": "Cerveza Kunstmann 1L", "precio": 2990, "categoria": "snacks"},
        {"id": "S020", "nombre": "Vodka Absolut 750ml", "precio": 9990, "categoria": "snacks"},
        {"id": "S021", "nombre": "Espumante Santa Carolina Brut 750ml", "precio": 5990, "categoria": "snacks"},
        {"id": "S022", "nombre": "Pisco Control 40° 750ml", "precio": 12990, "categoria": "snacks"},
        {"id": "S023", "nombre": "Cerveza Heineken 330ml", "precio": 1790, "categoria": "snacks"},
        {"id": "S024", "nombre": "Vino Santa Rita 120 750ml", "precio": 3990, "categoria": "snacks"},
        {"id": "S025", "nombre": "Gin Beefeater 750ml", "precio": 13990, "categoria": "snacks"}
    ],
    "belleza": [
        {"id": "B001", "nombre": "Shampoo Pantene 400ml", "precio": 4990, "categoria": "belleza"},
        {"id": "B002", "nombre": "Acondicionador Sedal 400ml", "precio": 4790, "categoria": "belleza"},
        {"id": "B003", "nombre": "Crema hidratante Nivea 50ml", "precio": 6990, "categoria": "belleza"},
        {"id": "B004", "nombre": "Jabón Dove 250ml", "precio": 3490, "categoria": "belleza"},
        {"id": "B005", "nombre": "Desmaquillante Garnier 200ml", "precio": 4990, "categoria": "belleza"},
        {"id": "B006", "nombre": "Protector solar Eucerin SPF50", "precio": 8990, "categoria": "belleza"},
        {"id": "B007", "nombre": "Mascarilla capilar TRESemmé 200ml", "precio": 5490, "categoria": "belleza"},
        {"id": "B008", "nombre": "Exfoliante Neutrogena 100ml", "precio": 5990, "categoria": "belleza"},
        {"id": "B009", "nombre": "Sérum facial L'Oréal 30ml", "precio": 10990, "categoria": "belleza"},
        {"id": "B010", "nombre": "Toallas desmaquillantes Nivea x25", "precio": 3990, "categoria": "belleza"}
    ],
    "bebe": [
        {"id": "BB001", "nombre": "Pañales Huggies pack x30", "precio": 13990, "categoria": "bebe"},
        {"id": "BB002", "nombre": "Toallas húmedas Huggies x80", "precio": 4290, "categoria": "bebe"},
        {"id": "BB003", "nombre": "Shampoo Johnson's Baby 400ml", "precio": 4490, "categoria": "bebe"},
        {"id": "BB004", "nombre": "Crema para pañal Babysec 100g", "precio": 5990, "categoria": "bebe"},
        {"id": "BB005", "nombre": "Jabón líquido Johnson's Baby 250ml", "precio": 3790, "categoria": "bebe"},
        {"id": "BB006", "nombre": "Aceite Johnson's Baby 200ml", "precio": 4990, "categoria": "bebe"},
        {"id": "BB007", "nombre": "Algodón Confort x100", "precio": 2490, "categoria": "bebe"},
        {"id": "BB008", "nombre": "Colonia Johnson's Baby 100ml", "precio": 6990, "categoria": "bebe"},
        {"id": "BB009", "nombre": "Protector solar Babysec SPF50", "precio": 10990, "categoria": "bebe"},
        {"id": "BB010", "nombre": "Cotonitos Confort x75", "precio": 2190, "categoria": "bebe"}
    ]
}

KITS_PREDEFINIDOS = {
    "semanal": {
        "id": "kit_semanal",
        "nombre": "Kit Semanal",
        "descripcion": "Todo lo esencial para una semana",
        "imagen": "imgs/kit_semana.png",
        "productos": [
            {"id": "L001", "cantidad": 1},
            {"id": "L006", "cantidad": 1},
            {"id": "L004", "cantidad": 1},
            {"id": "S001", "cantidad": 1},
            {"id": "S002", "cantidad": 1},
            {"id": "S004", "cantidad": 1},
            {"id": "S008", "cantidad": 1},
            {"id": "S010", "cantidad": 1},
        ]
    },
    "mensual": {
        "id": "kit_mensual",
        "nombre": "Kit Mensual",
        "descripcion": "Abastécete por todo un mes",
        "imagen": "imgs/kit_mes.png",
        "productos": [
            {"id": "L001", "cantidad": 2},
            {"id": "L002", "cantidad": 1},
            {"id": "L003", "cantidad": 1},
            {"id": "L004", "cantidad": 2},
            {"id": "L005", "cantidad": 1},
            {"id": "L006", "cantidad": 3},
            {"id": "L007", "cantidad": 2},
            {"id": "L009", "cantidad": 1},
            {"id": "S001", "cantidad": 4},
            {"id": "S002", "cantidad": 2},
            {"id": "S003", "cantidad": 2},
            {"id": "S004", "cantidad": 2},
            {"id": "S006", "cantidad": 1},
            {"id": "S008", "cantidad": 2},
        ]
    }
}

def get_producto_by_id(producto_id):
    """Obtiene un producto por su ID"""
    for categoria in PRODUCTOS.values():
        for producto in categoria:
            if producto["id"] == producto_id:
                return producto
    return None

def get_all_productos():
    """Obtiene todos los productos en una lista plana"""
    todos = []
    for categoria in PRODUCTOS.values():
        todos.extend(categoria)
    return todos

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
    if kit_id in KITS_PREDEFINIDOS:
        kit = KITS_PREDEFINIDOS[kit_id].copy()
        kit['precio'] = calcular_precio_kit(kit)
        return kit
    return None