from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPen
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QGraphicsEllipseItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFrame,
)


class BlockItem(QGraphicsRectItem):
    SNAP_DISTANCE = 30
    CONNECTOR_RADIUS = 5

    def __init__(self, text: str, x: float = 0, y: float = 0) -> None:
        super().__init__(0, 0, 140, 50)

        self.setBrush(QBrush(QColor(70, 130, 180)))
        self.setPen(QPen(QColor(220, 220, 220), 1))

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )

        self.setPos(x, y)

        self.label = QGraphicsSimpleTextItem(text, self)
        self.label.setBrush(QBrush(Qt.white))
        self.label.setFont(QFont("Segoe UI", 10))

        text_rect = self.label.boundingRect()
        rect = self.rect()

        label_x = (rect.width() - text_rect.width()) / 2
        label_y = (rect.height() - text_rect.height()) / 2
        self.label.setPos(label_x, label_y)

        self._create_connectors()

    def _create_connectors(self) -> None:
        rect = self.rect()
        r = self.CONNECTOR_RADIUS
        connector_brush = QBrush(QColor(235, 235, 235))
        connector_pen = QPen(QColor(40, 40, 40), 1)

        center_y = rect.height() / 2 - r

        self.left_connector = QGraphicsEllipseItem(-r, center_y, 2 * r, 2 * r, self)
        self.left_connector.setBrush(connector_brush)
        self.left_connector.setPen(connector_pen)

        self.right_connector = QGraphicsEllipseItem(
            rect.width() - r, center_y, 2 * r, 2 * r, self
        )
        self.right_connector.setBrush(connector_brush)
        self.right_connector.setPen(connector_pen)

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        self.snap_to_nearest_block()

    def snap_to_nearest_block(self) -> None:
        scene = self.scene()
        if scene is None:
            return

        my_rect = self.sceneBoundingRect()

        for item in scene.items():
            if item is self:
                continue

            if not isinstance(item, BlockItem):
                continue

            other_rect = item.sceneBoundingRect()

            # Snap my left side to other's right side
            if abs(my_rect.left() - other_rect.right()) < self.SNAP_DISTANCE:
                if abs(my_rect.center().y() - other_rect.center().y()) < self.SNAP_DISTANCE:
                    new_x = other_rect.right()
                    new_y = other_rect.center().y() - my_rect.height() / 2
                    self.setPos(new_x, new_y)
                    return

            # Snap my right side to other's left side
            if abs(my_rect.right() - other_rect.left()) < self.SNAP_DISTANCE:
                if abs(my_rect.center().y() - other_rect.center().y()) < self.SNAP_DISTANCE:
                    new_x = other_rect.left() - my_rect.width()
                    new_y = other_rect.center().y() - my_rect.height() / 2
                    self.setPos(new_x, new_y)
                    return


class WorkspaceView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)
        self.setRenderHint(self.renderHints())
        self.setFrameShape(QFrame.StyledPanel)
        self.setSceneRect(0, 0, 2000, 1200)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setBackgroundBrush(QBrush(QColor(45, 45, 48)))

    def drawBackground(self, painter, rect: QRectF) -> None:
        super().drawBackground(painter, rect)

        grid_size = 40
        pen = QPen(QColor(60, 60, 65))
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        x = left
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += grid_size

        y = top
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += grid_size


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Excel Lego Builder")
        self.resize(1200, 800)

        self.block_counter = 0

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        title = QLabel("Blocks")
        left_layout.addWidget(title)

        self.block_list = QListWidget()
        self.block_list.addItems([
            "Investment",
            "Revenue",
            "Cost",
            "Category",
            "Date",
        ])
        left_layout.addWidget(self.block_list)

        self.add_button = QPushButton("Add Block")
        left_layout.addWidget(self.add_button)

        # Workspace scene/view
        self.scene = QGraphicsScene()
        self.workspace_view = WorkspaceView(self.scene)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(self.workspace_view, 3)

        self.add_button.clicked.connect(self.add_block)

    def add_block(self) -> None:
        selected_item = self.block_list.currentItem()
        if selected_item is None:
            return

        self.block_counter += 1

        x = 60 + (self.block_counter % 5) * 160
        y = 60 + (self.block_counter // 5) * 80

        block = BlockItem(selected_item.text(), x, y)
        self.scene.addItem(block)