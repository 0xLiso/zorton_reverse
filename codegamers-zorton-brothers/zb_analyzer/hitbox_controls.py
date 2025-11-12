from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class HitboxControlsPanel(QWidget):
    """Panel de controles para gestión global de hitboxes"""

    def __init__(self):
        super().__init__()
        self.offset_x_spin = None
        self.offset_y_spin = None
        self.select_all_btn = None
        self.deselect_all_btn = None
        self._create_layout()

    def _create_layout(self):
        """layout vertical"""
        layout = QVBoxLayout()

        # marcar/desmarcar todos
        select_buttons_layout = self._create_select_buttons()
        layout.addLayout(select_buttons_layout)

        offset_layout = self._create_offset_controls()
        layout.addLayout(offset_layout)

        self.setLayout(layout)

    def _create_select_buttons(self):
        """layout horizontal botones marcar/desmarcar"""
        layout = QHBoxLayout()

        self.select_all_btn = QPushButton("Marcar todos")
        self.deselect_all_btn = QPushButton("Desmarcar todos")

        layout.addWidget(self.select_all_btn)
        layout.addWidget(self.deselect_all_btn)

        return layout

    def _create_offset_controls(self):
        """controles de offset X e Y"""
        layout = QVBoxLayout()

        offset_label = QLabel("Offset Global:")
        offset_label.setStyleSheet("font-weight: bold;")

        offset_xy_layout = QHBoxLayout()

        offset_x_label = QLabel("X:")
        self.offset_x_spin = QSpinBox()
        self.offset_x_spin.setRange(-100, 100)
        self.offset_x_spin.setValue(0)
        self.offset_x_spin.setSuffix(" px")

        offset_y_label = QLabel("Y:")
        self.offset_y_spin = QSpinBox()
        self.offset_y_spin.setRange(-100, 100)
        self.offset_y_spin.setValue(0)
        self.offset_y_spin.setSuffix(" px")

        offset_xy_layout.addWidget(offset_x_label)
        offset_xy_layout.addWidget(self.offset_x_spin)
        offset_xy_layout.addWidget(offset_y_label)
        offset_xy_layout.addWidget(self.offset_y_spin)

        layout.addWidget(offset_label)
        layout.addLayout(offset_xy_layout)

        return layout

    def get_offset_values(self):
        """return de valores actuales de offset"""
        if self.offset_x_spin and self.offset_y_spin:
            return (self.offset_x_spin.value(), self.offset_y_spin.value())
        return (0, 0)

    def connect_select_buttons(self, select_all_callback, deselect_all_callback):
        """callbacks de los botones de selección"""
        if self.select_all_btn and self.deselect_all_btn:
            self.select_all_btn.clicked.connect(select_all_callback)
            self.deselect_all_btn.clicked.connect(deselect_all_callback)
