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
    QInputDialog,
    QWidget,
    QFrame,
)


class BlockItem(QGraphicsRectItem):
    SNAP_DISTANCE = 30
    CONNECTOR_RADIUS = 5

    def update_label_position(self) -> None:
        text_rect = self.label.boundingRect()
        rect = self.rect()

        label_x = (rect.width() - text_rect.width()) / 2
        label_y = (rect.height() - text_rect.height()) / 2
        self.label.setPos(label_x, label_y)


    def set_display_text(self, new_text: str) -> None:
        self.display_text = new_text
        self.label.setText(new_text)
        self.update_label_position()


    def mouseDoubleClickEvent(self, event) -> None:
        if self.block_type == "corner":
            super().mouseDoubleClickEvent(event)
            return

        current_text = self.display_text
        new_text, ok = QInputDialog.getText(
            None,
            "Edit Block Name",
            "Enter block name:",
            text=current_text,
        )

        if ok:
            cleaned_text = new_text.strip()
            if cleaned_text:
                self.set_display_text(cleaned_text)

        super().mouseDoubleClickEvent(event)

    def __init__(self, text: str, block_type: str, x: float = 0, y: float = 0) -> None:
        self.block_type = block_type
        self.display_text = text
        
        width, height = 140, 50

        super().__init__(0, 0, width, height)

        self.setBrush(QBrush(self.get_color()))
        self.setPen(QPen(QColor(220, 220, 220), 1))

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable
        )

        self.setPos(x, y)

        self.label = QGraphicsSimpleTextItem(text, self)
        self.label.setBrush(QBrush(Qt.white))
        self.label.setFont(QFont("Segoe UI", 10))

        self.update_label_position()

        self._create_connectors()

    def get_color(self) -> QColor:
        if self.block_type == "row":
            return QColor(70, 130, 180)   # blue
        if self.block_type == "column":
            return QColor(46, 125, 50)    # green
        if self.block_type == "corner":
            return QColor(120, 80, 160)   # purple
        return QColor(100, 100, 100)

    def _create_connectors(self) -> None:
        rect = self.rect()
        r = self.CONNECTOR_RADIUS
        connector_brush = QBrush(QColor(235, 235, 235))
        connector_pen = QPen(QColor(40, 40, 40), 1)

        mid_x = rect.width() / 2 - r
        mid_y = rect.height() / 2 - r

        self.connectors = {}

        # Column blocks connect horizontally
        if self.block_type in ("column", "corner"):
            self.connectors["left"] = QGraphicsEllipseItem(-r, mid_y, 2 * r, 2 * r, self)
            self.connectors["left"].setBrush(connector_brush)
            self.connectors["left"].setPen(connector_pen)

            self.connectors["right"] = QGraphicsEllipseItem(
                rect.width() - r, mid_y, 2 * r, 2 * r, self
            )
            self.connectors["right"].setBrush(connector_brush)
            self.connectors["right"].setPen(connector_pen)

        # Row blocks connect vertically
        if self.block_type in ("row", "corner"):
            self.connectors["top"] = QGraphicsEllipseItem(mid_x, -r, 2 * r, 2 * r, self)
            self.connectors["top"].setBrush(connector_brush)
            self.connectors["top"].setPen(connector_pen)

            self.connectors["bottom"] = QGraphicsEllipseItem(
                mid_x, rect.height() - r, 2 * r, 2 * r, self
            )
            self.connectors["bottom"].setBrush(connector_brush)
            self.connectors["bottom"].setPen(connector_pen)    

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

            # Column-to-column or column-to-corner horizontal snapping
            if self.block_type in ("column", "corner") and item.block_type in ("column", "corner"):
                # Snap my left to other's right
                if abs(my_rect.left() - other_rect.right()) < self.SNAP_DISTANCE:
                    if abs(my_rect.center().y() - other_rect.center().y()) < self.SNAP_DISTANCE:
                        self.setPos(other_rect.right(), other_rect.center().y() - my_rect.height() / 2)
                        return

                # Snap my right to other's left
                if abs(my_rect.right() - other_rect.left()) < self.SNAP_DISTANCE:
                    if abs(my_rect.center().y() - other_rect.center().y()) < self.SNAP_DISTANCE:
                        self.setPos(other_rect.left() - my_rect.width(), other_rect.center().y() - my_rect.height() / 2)
                        return

            # Row-to-row or row-to-corner vertical snapping
            if self.block_type in ("row", "corner") and item.block_type in ("row", "corner"):
                # Snap my top to other's bottom
                if abs(my_rect.top() - other_rect.bottom()) < self.SNAP_DISTANCE:
                    if abs(my_rect.center().x() - other_rect.center().x()) < self.SNAP_DISTANCE:
                        self.setPos(other_rect.center().x() - my_rect.width() / 2, other_rect.bottom())
                        return

                # Snap my bottom to other's top
                if abs(my_rect.bottom() - other_rect.top()) < self.SNAP_DISTANCE:
                    if abs(my_rect.center().x() - other_rect.center().x()) < self.SNAP_DISTANCE:
                        self.setPos(other_rect.center().x() - my_rect.width() / 2, other_rect.top() - my_rect.height())
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
            "Row",
            "Column",
            "Corner",
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

        selected_text = selected_item.text()

        if selected_text == "Row":
            block_type = "row"
        elif selected_text == "Column":
            block_type = "column"
        else:
            block_type = "corner"

        block = BlockItem(selected_text, block_type, x, y)
        self.scene.addItem(block)