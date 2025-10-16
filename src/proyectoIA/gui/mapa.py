import re
import os
from PySide6.QtGui import QColor

# Tipos de celdas
class CellTypes:
    EMPTY = 0
    ANT = 1
    OBSTACLE = 2
    OBJECTIVE = 3

# Colores asignados a cada tipo de celda
color_map = {
    CellTypes.EMPTY: QColor(240, 240, 240),  # Blanco
    CellTypes.ANT: QColor(240, 240, 0),      # Amarillo
    CellTypes.OBSTACLE: QColor(200, 0, 0),   # Rojo
    CellTypes.OBJECTIVE: QColor(0, 200, 0)   # Verde
}

# Funcion para cargar el mapa a partir de mapa.txt
def load_map():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, "txt", "mapa.txt")

    print(f"\n=== CARGANDO MAPA ===")
    print(f"Buscando archivo: {filename}")

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        print(f"Archivo encontrado. {len(lines)} líneas leídas")

    except FileNotFoundError:
        print("Archivo mapa.txt no encontrado. Creando archivo por defecto...")
        # Crear el directorio txt si no existe
        txt_dir = os.path.join(current_dir, "txt")
        os.makedirs(txt_dir, exist_ok=True)
        
        # Crea el archivo mapa.txt si no existe
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("Tamaño(6,6)\n")
            file.write("Hormiga(1,1)\n")
            file.write("Veneno((2,2),(1,3),(4,3),(2,4),(3,5))\n")
            file.write("Hongo(5,5)\n")

        print("Archivo creado. Reintentando carga...")
        return load_map()

    # Inicializar variables por defecto
    rows = 5
    cols = 5
    grid_data = {}
    
    tamano_encontrado = False

    # Se interpreta el contenido del archivo mapa.txt
    for i, line in enumerate(lines, 1):
        line_original = line
        line = line.strip()
        
        print(f"\nLínea {i}: '{line_original.rstrip()}'")
        
        if not line:
            print("  -> Línea vacía, ignorando")
            continue

        if line.startswith("Tamaño") or line.startswith("Tamano"):
            # Intentar con y sin tilde
            match = re.search(r'Tama[ñn]o\((\d+)\s*,\s*(\d+)\)', line)
            if match:
                rows = int(match.group(1))
                cols = int(match.group(2))
                tamano_encontrado = True
                print(f"  -> Tamaño detectado: {rows}x{cols}")
            else:
                print(f"  -> ERROR: No se pudo parsear el tamaño. Formato esperado: Tamaño(n,m)")

        elif line.startswith("Hormiga"):
            match = re.search(r'Hormiga\((\d+)\s*,\s*(\d+)\)', line)
            if match:
                row = int(match.group(1)) - 1
                col = int(match.group(2)) - 1
                grid_data[(row, col)] = CellTypes.ANT
                print(f"  -> Hormiga en posición ({row}, {col})")
            else:
                print(f"  -> ERROR: No se pudo parsear la hormiga")

        elif line.startswith("Veneno"):
            coords = re.findall(r'\((\d+)\s*,\s*(\d+)\)', line)
            print(f"  -> Encontrados {len(coords)} venenos")
            for r, c in coords:
                row = int(r) - 1
                col = int(c) - 1
                grid_data[(row, col)] = CellTypes.OBSTACLE
                print(f"     Veneno en ({row}, {col})")

        elif line.startswith("Hongo"):
            match = re.search(r'Hongo\((\d+)\s*,\s*(\d+)\)', line)
            if match:
                row = int(match.group(1)) - 1
                col = int(match.group(2)) - 1
                grid_data[(row, col)] = CellTypes.OBJECTIVE
                print(f"  -> Hongo en posición ({row}, {col})")
            else:
                print(f"  -> ERROR: No se pudo parsear el hongo")
        else:
            print(f"  -> Línea no reconocida")

    # print(f"\n=== RESUMEN ===")
    # print(f"Tamaño encontrado: {tamano_encontrado}")
    # print(f"Dimensiones finales: {rows}x{cols}")
    # print(f"Elementos en el mapa: {len(grid_data)}")
    # print(f"=================\n")

    return rows, cols, grid_data