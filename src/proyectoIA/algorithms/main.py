from dynamic import dynamic_weighting_search
from beam_search import beam_search
import time  


# Ejemplo de uso
if __name__ == "__main__":

    # ALgoritmo beam_search
    n = 5
    inicio = (0, 0)
    meta = (4, 4)
    obstaculos = [(1, 1), (2, 0), (2, 3),(3,1) ,(4, 2)]
    
    camino = beam_search(n, inicio, meta, obstaculos)
    
    if camino:
        print("Camino encontrado:")
        for i, pos in enumerate(camino):
            print(f"Paso {i}: {pos}")
        print(f"\nLongitud del camino: {len(camino)} pasos")
    else:
        print("No se encontró un camino hacia la meta")


    # Algoritmo dynamic
    n = 5
    inicio = (0, 0)
    meta = (4, 4)
    obstaculos = [(1,1), (2,0), (2,3), (3,1), (4,2)]

    camino = dynamic_weighting_search(n, inicio, meta, obstaculos)

    if camino:
        print("Camino encontrado:")
        for i, pos in enumerate(camino):
            print(f"Paso {i + 1}: la hormiga se mueve a {pos}")
            time.sleep(0.5) #para simular la animación
        print(f"\nLongitud total: {len(camino)} pasos")
    else:
        print("No se encontró un camino hacia la meta.")