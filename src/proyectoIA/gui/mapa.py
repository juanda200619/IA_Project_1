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
    CellTypes.EMPTY: QColor(240, 240, 240),  # Blanco   240 240 240
    CellTypes.ANT: QColor(240, 240, 0),      # Amarillo 255 255   0
    CellTypes.OBSTACLE: QColor(200, 0, 0),   # Rojo     200   0   0
    CellTypes.OBJECTIVE: QColor(0, 200, 0)   # Verde      0 200   0
}

# Funcion para cargar el mapa a partir de mapa.txt
def load_map():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_dir, "txt", "mapa.txt")

    try :
        with open(filename, 'r') as file:
            lines = file.readlines()

    except FileNotFoundError:
        print("Error")
        # Crea el archivo mapa.txt si no existe
        with open(filename, 'w') as file:
            file.write("Tamaño(5, 5)\n")
            file.write("Hormiga(1, 1)\n")
            file.write("Veneno((2,2),(1,3),(4,3),(2,4),(3,5))")
            file.write("Hongo(5, 5)\n")

        return load_map()

    grid_data = {}
    size = 0

    # Se interpreta el contenido del archivo mapa.txt
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("Tamaño"):
            match = re.search(r'Tamaño\((\d+),\s*(\d+)\)', line)
            if match:
                rows = int(match.group(1))
                cols = int(match.group(2))

        elif line.startswith("Hormiga"):
            match = re.search(r'Hormiga\((\d+),\s*(\d+)\)', line)
            if match:
                row = int(match.group(1)) - 1
                col = int(match.group(2)) - 1
                grid_data[(row, col)] = CellTypes.ANT

        elif line.startswith("Veneno"):
            coords = re.findall(r'\((\d+),\s*(\d+)\)', line)
            for r, c in coords:
                row = int(c) - 1
                col = int(r) - 1
                grid_data[(row, col)] = CellTypes.OBSTACLE

        elif line.startswith("Hongo"):
            match = re.search(r'Hongo\((\d+),\s*(\d+)\)', line)
            if match:
                row = int(match.group(1)) - 1
                col = int(match.group(2)) - 1
                grid_data[(row, col)] = CellTypes.OBJECTIVE

    return rows, cols, grid_data