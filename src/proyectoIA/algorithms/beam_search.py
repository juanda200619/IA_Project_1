# Calcula la distancia manhattan entre 2 puntos
def manhattan(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


# Aplicación de los operadores (CORREGIDO)
def moverArriba(tupla_x_y):
    return (tupla_x_y[0] - 1, tupla_x_y[1])

def moverAbajo(tupla_x_y):
    return (tupla_x_y[0] + 1, tupla_x_y[1])

def moverIzquierda(posicion):
    return (posicion[0], posicion[1] - 1)

def moverDerecha(posicion):
    return (posicion[0], posicion[1] + 1)


# Determinar posibilidad de un movimiento
def isPosibleArriba(posicion):
    return posicion[0] - 1 >= 0

def isPosibleAbajo(posicion, n):
    return posicion[0] + 1 < n

def isPosibleIzquierda(posicion):
    return posicion[1] - 1 >= 0

def isPosibleDerecha(posicion, n):
    return posicion[1] + 1 < n

def isNodoMeta(meta, posicion):
    return meta[0] == posicion[0] and meta[1] == posicion[1]


def calcular_beam_width(n, num_obstaculos):
    """
    n: tamaño del tablero (nxn)
    num_obstaculos: cantidad de obstáculos en el tablero
    """
    densidad = num_obstaculos / (n * n)
    
    if n <= 10:
        base = 5
    elif n <= 30:
        base = 4
    elif n <= 50:
        base = 3
    else:
        base = 3
    
    # Ajustar por densidad de obstáculos
    if densidad > 0.4:  # Muchos obstáculos
        multiplicador = 1.5
    elif densidad > 0.2:  # Obstáculos moderados
        multiplicador = 1.2
    else:  # Pocos obstáculos
        multiplicador = 1.0
    
    beam_width = int(base * multiplicador)
    
    # Limitar entre valores razonables
    return max(3, min(beam_width, 10))


def expandir_nodo(nodo_actual, meta, obstaculos, n, indice_padre):
    """
    Expande un nodo generando todos sus sucesores válidos
    Retorna una lista de tuplas: (indice_padre, posicion, g_n, h_n, f_n)
    """
    posicion_actual = nodo_actual[0]
    g_actual = nodo_actual[2]
    
    sucesores = []
    
    # Definir movimientos posibles
    movimientos = [
        (isPosibleArriba(posicion_actual), moverArriba, "arriba"),
        (isPosibleAbajo(posicion_actual, n), moverAbajo, "abajo"),
        (isPosibleIzquierda(posicion_actual), moverIzquierda, "izquierda"),
        (isPosibleDerecha(posicion_actual, n), moverDerecha, "derecha")
    ]
    
    for es_posible, mover, direccion in movimientos:
        if es_posible:
            nueva_posicion = mover(posicion_actual)
            
            # Calcular costos
            costo_movimiento = 3 if nueva_posicion in obstaculos else 1
            g_n = g_actual + costo_movimiento
            h_n = manhattan(nueva_posicion, meta)
            f_n = g_n + h_n
            
            sucesores.append((indice_padre, nueva_posicion, g_n, h_n, f_n))
    
    return sucesores


def reconstruir_camino(closedList, indice_meta):
    """
    Reconstruye el camino desde el inicio hasta la meta
    siguiendo los índices de padres
    """
    camino = []
    indice_actual = indice_meta
    
    while indice_actual is not None:
        nodo = closedList[indice_actual]
        camino.append(nodo[0])  # Agregar la posición
        indice_actual = nodo[1]  # Moverse al padre
    
    camino.reverse()  # Invertir para tener el camino de inicio a meta
    return camino


def beam_search(n, inicio, meta, obstaculos):
    """
    Implementación del algoritmo Beam Search
    
    Args:
        n: tamaño del tablero (n x n)
        inicio: tupla (x, y) posición inicial
        meta: tupla (x, y) posición objetivo
        obstaculos: lista de tuplas con posiciones de obstáculos
    
    Returns:
        camino: lista de posiciones desde inicio hasta meta
        None si no se encuentra camino
    """
    
    # Definir el ancho de haz
    beamWidth = calcular_beam_width(n, len(obstaculos))
    
    # closedList: guarda nodos expandidos
    # Cada elemento: [posicion, indice_padre, g_n, h_n]
    closedList = []
    
    # Agregar nodo inicial
    h_inicial = manhattan(inicio, meta)
    closedList.append([inicio, None, 0, h_inicial])
    
    # Verificar si ya estamos en la meta
    if isNodoMeta(meta, inicio):
        return [inicio]
    
    # openList: nodos candidatos para expandir en la siguiente iteración
    openList = [0]  # Índices de nodos en closedList que están en el beam actual
    
    iteracion = 0
    max_iteraciones = n * n * 2  # Límite de seguridad
    
    while openList and iteracion < max_iteraciones:
        iteracion += 1
        
        # Lista para guardar todos los sucesores de los nodos en el beam
        todos_sucesores = []
        
        # Expandir cada nodo en el beam actual
        for indice_nodo in openList:
            nodo = closedList[indice_nodo]
            
            # Generar sucesores
            sucesores = expandir_nodo(nodo, meta, obstaculos, n, indice_nodo)
            
            for sucesor in sucesores:
                indice_padre, posicion, g_n, h_n, f_n = sucesor
                
                # Verificar si encontramos la meta
                if isNodoMeta(meta, posicion):
                    # Agregar el nodo meta a closedList
                    closedList.append([posicion, indice_padre, g_n, h_n])
                    indice_meta = len(closedList) - 1
                    
                    # Reconstruir y retornar el camino
                    return reconstruir_camino(closedList, indice_meta)
                
                # Verificar si ya visitamos esta posición
                ya_visitado = any(n[0] == posicion for n in closedList)
                
                if not ya_visitado:
                    todos_sucesores.append((posicion, indice_padre, g_n, h_n, f_n))
        
        # Si no hay sucesores, no hay camino
        if not todos_sucesores:
            return None
        
        # Ordenar sucesores por f(n) = g(n) + h(n)
        todos_sucesores.sort(key=lambda x: x[4])
        
        # Seleccionar los beamWidth mejores nodos (poda)
        mejores_sucesores = todos_sucesores[:beamWidth]
        
        # Agregar los mejores sucesores a closedList y actualizar openList
        openList = []
        for posicion, indice_padre, g_n, h_n, f_n in mejores_sucesores:
            closedList.append([posicion, indice_padre, g_n, h_n])
            openList.append(len(closedList) - 1)
    
    # No se encontró camino
    return None