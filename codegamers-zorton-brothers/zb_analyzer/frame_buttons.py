from PySide6.QtWidgets import QHBoxLayout, QPushButton


class FrameButtonManager:
    """Gestiona los botones de reproducción de frames"""

    def __init__(
        self, buttons_layout, play_frame_loop_callback, history_update_callback=None
    ):
        self.buttons_layout = buttons_layout
        self.play_frame_loop_callback = play_frame_loop_callback
        self.history_update_callback = history_update_callback
        self.current_button = None
        self.frame_buttons = []
        self.frame_history = []

    def update_frame_buttons(self, frames):
        """Actualiza los botones de frames (2 por fila)"""
        # Limpiar botones anteriores
        self._clear_buttons()
        self.current_button = None
        self.frame_buttons = []

        row_layout = None
        for i, fr in enumerate(frames):
            if i % 2 == 0:
                row_layout = QHBoxLayout()
                self.buttons_layout.addLayout(row_layout)

            btn = self._create_frame_button(i, fr)
            self.frame_buttons.append((btn, fr["from"], fr["to"]))
            if row_layout:
                row_layout.addWidget(btn)

    def _clear_buttons(self):
        """Limpia todos los botones existentes"""
        while self.buttons_layout.count():
            child = self.buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():  # necesario limpiar layoits
                while child.layout().count():
                    subchild = child.layout().takeAt(0)
                    if subchild.widget():
                        subchild.widget().deleteLater()

    def _create_frame_button(self, index, frame_data):
        """botón para el frame inicio/fin"""
        start = frame_data["from"]
        end = frame_data["to"]
        duration = end - start + 1

        btn = QPushButton(f"#{index + 1}: {start}–{end} ({duration})")
        btn.clicked.connect(
            lambda checked, b=btn, idx=index: self._on_button_clicked(
                b, start, end, idx
            )
        )

        return btn

    def _on_button_clicked(self, button, start, end, index, add_to_history=True):
        """click en un botón de frame"""
        if self.current_button:
            self.current_button.setStyleSheet("")

        button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold;"
        )
        self.current_button = button

        if add_to_history:
            self.frame_history.append(index + 1)
            if self.history_update_callback:
                self.history_update_callback(self.frame_history)

        self.play_frame_loop_callback(start, end)

    def activate_first_frame(self):
        """activa el primer botón de frame"""
        if self.frame_buttons:
            first_button, start, end = self.frame_buttons[0]
            self._on_button_clicked(first_button, start, end, 0, add_to_history=False)

    def reset_history(self):
        """resetear el historial de frames"""
        self.frame_history = []
        if self.history_update_callback:
            self.history_update_callback(self.frame_history)

    def clear_active_button(self):
        """desmarca el botón activo sin ejecutar el callback"""
        if self.current_button:
            self.current_button.setStyleSheet("")
            self.current_button = None
