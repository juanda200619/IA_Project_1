import sys
from ..algorithms.beam_search import beam_search
from ..algorithms.dynamic import dynamic_weighting_search
from PySide6.QtCore import QTimer

from .mapa import (
    load_map,
    CellTypes,
    color_map,
)
from PySide6.QtWidgets import (
    QMainWindow,
    QGraphicsView,
    QWidget,
    QGraphicsScene,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QGraphicsRectItem,
    QPushButton,
    QGraphicsTextItem,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QWheelEvent,
    QBrush,
    QFont,
)

# Clase para crear un mapa zoomable
class ZoomableGridView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(self.renderHints())
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    # Zoom con la rueda del mouse
    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

# Cuerpo principal de la ventana
class GridWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Tamaño de las celdas
        self.cell_size = 20  # pixeles

        # Configuración de la animación
        self.camino_actual = []
        self.indice_animacion = 0
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self.actualizar_animacion)
        self.velocidad_animacion = 300 

        self.ant_item = None
        self.mushroom_item = None

        # Cargar mapa inicial
        self.rows, self.cols, self.grid_data = load_map()

        # Auxiliar para mostrar movimientos sin perder el mapa original
        # Modificar para las animaciones
        self.temp_grid_data = self.grid_data.copy()

        self.scene = QGraphicsScene()
        self.view = ZoomableGridView(self.scene)
        self.view.setMinimumSize(600, 400)

        # Boton iniciar Beam Search
        self.btn_beam = QPushButton("Iniciar Beam Search")
        self.btn_beam.clicked.connect(self.iniciar_beam)

        # Boton iniciar Dynamic Weighting
        self.btn_dw = QPushButton("Iniciar Dynamic Weighting")
        self.btn_dw.clicked.connect(self.iniciar_dw)

        

        # Boton resetear mapa
        self.reiniciar_todo = QPushButton("Reiniciar")
        self.reiniciar_todo.clicked.connect(self.reiniciar)

        # Panel lateral
        self.panel = QVBoxLayout()
        self.panel.addWidget(self.btn_beam)
        self.panel.addWidget(self.btn_dw)
        self.panel.addWidget(self.reiniciar_todo)
        self.panel.addStretch()

        self.side_widget = QWidget()
        self.side_widget.setLayout(self.panel)
        self.side_widget.setFixedWidth(200)

        # Grid + Panel
        self.main_area = QHBoxLayout()
        self.main_area.addWidget(self.view)
        self.main_area.addWidget(self.side_widget)

        layout = QVBoxLayout()
        layout.addLayout(self.main_area)
        self.setLayout(layout)

        self.redraw_grid()

    # Reajusta los limites del mapa
    def set_grid_size(self, size):
        self.rows, self.cols = size

    def redraw_grid(self):
        self.scene.clear()
        self.ant_item = None
        self.mushroom_item = None
        
        width = self.cols * self.cell_size
        height = self.rows * self.cell_size
        self.scene.setSceneRect(0, 0, width, height)

        for row in range(self.rows):
            for col in range(self.cols):
                cell_type = self.temp_grid_data.get((row, col), CellTypes.EMPTY)
                color = color_map[cell_type]

                rect = QGraphicsRectItem(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                rect.setBrush(QBrush(color))
                self.scene.addItem(rect)
                
                if cell_type == CellTypes.ANT:
                    self.ant_item = QGraphicsTextItem("🐜")
                    font = QFont()
                    font.setPointSize(int(self.cell_size * 0.8))
                    self.ant_item.setFont(font)
                    # Center the emoji in the cell
                    self.ant_item.setPos(
                        col * self.cell_size + self.cell_size * 0.1,
                        row * self.cell_size - self.cell_size * 0.2
                    )
                    self.scene.addItem(self.ant_item)
                
                elif cell_type == CellTypes.OBJECTIVE:
                    self.mushroom_item = QGraphicsTextItem("🍄")
                    font = QFont()
                    font.setPointSize(int(self.cell_size * 0.8))
                    self.mushroom_item.setFont(font)
                    # Center the emoji in the cell
                    self.mushroom_item.setPos(
                        col * self.cell_size + self.cell_size * 0.1,
                        row * self.cell_size - self.cell_size * 0.2
                    )
                    self.mushroom_item.setZValue(1)
                    self.scene.addItem(self.mushroom_item)

    # Funcion para reiniciar el mapa
    def reiniciar(self):
        self.timer_animacion.stop()
        self.rows, self.cols, self.grid_data = load_map()
        self.temp_grid_data = self.grid_data.copy()
        self.redraw_grid()
        print("Mapa reiniciado")

    def iniciar_beam(self):
        try:
            self.timer_animacion.stop()

            inicio, meta, obstaculos = self.extraer_datos_mapa()
            
            print(f"   Inicio: {inicio}, Meta: {meta}, Obstáculos: {len(obstaculos)}")
            
            camino = beam_search(self.rows, inicio, meta, obstaculos)
            
            if camino:
                print(f"Camino encontrado con {len(camino)-1} pasos")
                self.animar_camino(camino)
            else:
                print("No se encontró un camino")
        except Exception as e:
            print(f"Error: {e}")

    def iniciar_dw(self):
        try:
            self.timer_animacion.stop()
            inicio, meta, obstaculos = self.extraer_datos_mapa()
            print(f"   Inicio: {inicio}, Meta: {meta}, Obstáculos: {len(obstaculos)}")
            
            camino = dynamic_weighting_search(self.rows, inicio, meta, obstaculos)
            
            if camino:
                print(f"Camino encontrado con {len(camino)-1} pasos")
                self.animar_camino(camino)
            else:
                print("No se encontró un camino")
        except Exception as e:
            print(f"Error: {e}")
        
    def extraer_datos_mapa(self):
        
        # Se extrae inicio, meta y obstáculos desde grid_data
        inicio = None
        meta = None
        obstaculos = []
        
        for pos, cell_type in self.grid_data.items():
            if cell_type == CellTypes.ANT:
                inicio = pos
            elif cell_type == CellTypes.OBJECTIVE:
                meta = pos
            elif cell_type == CellTypes.OBSTACLE:
                obstaculos.append(pos)
        
        if inicio is None or meta is None:
            raise ValueError("El mapa debe tener una hormiga y un hongo definidos")
        
        return inicio, meta, obstaculos
    
    def animar_camino(self, camino):
        
        #Anima el recorrido de la hormiga paso a paso
        
        if not camino:
            print("No hay camino para animar")
            return
        
        # Reiniciar animación
        self.timer_animacion.stop()
        self.camino_actual = camino
        self.indice_animacion = 0
        
        # Restaurar mapa original (quitar hormiga de posición inicial)
        self.temp_grid_data = self.grid_data.copy()
        
        for pos, cell_type in list(self.temp_grid_data.items()):
            if cell_type == CellTypes.ANT:
                self.temp_grid_data[pos] = CellTypes.EMPTY
        
        self.redraw_grid()
        
        if len(camino) > 0:
            start_pos = camino[0]
            self.ant_item = QGraphicsTextItem("🐜")
            font = QFont()
            font.setPointSize(int(self.cell_size * 0.8))
            self.ant_item.setFont(font)
            self.ant_item.setPos(
                start_pos[1] * self.cell_size + self.cell_size * 0.1,
                start_pos[0] * self.cell_size - self.cell_size * 0.2
            )
            self.ant_item.setZValue(1)
            self.scene.addItem(self.ant_item)
        
        # Iniciar animación
        self.timer_animacion.start(self.velocidad_animacion)

    def actualizar_animacion(self):
        
        #Actualizar la posición de la hormiga en cada paso de la animación
        
        if self.indice_animacion >= len(self.camino_actual):
            # Animación completada
            self.timer_animacion.stop()
            print(f"¡Camino completado en {len(self.camino_actual)-1} pasos!")
            return
        
        # Obtener posición actual del camino
        posicion_actual = self.camino_actual[self.indice_animacion]
        
        if self.temp_grid_data.get(posicion_actual) != CellTypes.OBJECTIVE:
            self.temp_grid_data[posicion_actual] = CellTypes.ANT
            
            # Redraw only the current cell
            row, col = posicion_actual
            color = color_map[CellTypes.ANT]
            rect = QGraphicsRectItem(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
            rect.setBrush(QBrush(color))
            self.scene.addItem(rect)
        
        # Move the ant emoji to the new position
        if self.ant_item:
            self.ant_item.setPos(
                posicion_actual[1] * self.cell_size + self.cell_size * 0.1,
                posicion_actual[0] * self.cell_size - self.cell_size * 0.2
            )
            self.ant_item.setZValue(1)
        
        # Avanzar al siguiente paso
        self.indice_animacion += 1

        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hormigas vs Venenos")
        self.setCentralWidget(GridWidget())
