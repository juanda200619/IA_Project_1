import sys
from ..algorithms.beam_search import beam_search
from ..algorithms.dynamic import dynamic_weighting_search

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
)
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QWheelEvent,
    QBrush,
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

        #TODO: Animacion para mostrar los movimientos de la hormiga

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

    # Se encarga de actualizar el mapa
    def redraw_grid(self):
        self.scene.clear()
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

    # Funcion para reiniciar el mapa
    def reiniciar(self):
        self.rows, self.cols, self.grid_data = load_map()
        self.temp_grid_data = self.grid_data.copy()
        self.redraw_grid()

    def iniciar_beam(self):
        inicio, meta, obstaculos = self.extraer_datos_mapa()
        camino = beam_search(self.rows, inicio, meta, obstaculos)
        if camino:
            self.animar_camino(camino)
            
    def iniciar_dw(self):
        inicio, meta, obstaculos = self.extraer_datos_mapa()
        camino = dynamic_weighting_search(self.rows, inicio, meta, obstaculos)
        if camino:
            self.animar_camino(camino)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hormigas vs Venenos")
        self.setCentralWidget(GridWidget())