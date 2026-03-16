from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QFrame,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Excel Lego Builder")
        self.resize(1200, 800)

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

        # Workspace
        workspace = QFrame()
        workspace.setFrameShape(QFrame.StyledPanel)
        workspace_layout = QVBoxLayout()
        workspace.setLayout(workspace_layout)

        workspace_label = QLabel("Workspace")
        workspace_layout.addWidget(workspace_label)

        self.workspace_info = QLabel("Empty for now")
        workspace_layout.addWidget(self.workspace_info)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(workspace, 3)

        self.add_button.clicked.connect(self.add_block)

    def add_block(self) -> None:
        selected_item = self.block_list.currentItem()
        if selected_item is not None:
            self.workspace_info.setText(f"Added block: {selected_item.text()}")