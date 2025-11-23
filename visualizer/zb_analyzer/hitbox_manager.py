"""
Gestor de hitboxes que maneja la creación de checkboxes y la aplicación de offsets.
"""

from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QPushButton, QWidget

from .video_player import VideoPlayer


class HitboxManager:
    """Gestiona los hitboxes, checkboxes y offsets"""

    def __init__(self, checkbox_layout, video_widget, play_frame_callback=None):
        self.checkbox_layout = checkbox_layout
        self.video_widget = video_widget
        self.play_frame_callback = play_frame_callback
        self.checkboxes = []
        self.original_hitboxes = []
        self.current_offset_x = 0
        self.current_offset_y = 0

    def update_hitboxes(self, hitboxes):
        """Actualiza los checkboxes de hitboxes"""
        # Guardar hitboxes originales para aplicar offset
        self.original_hitboxes = [hb.copy() for hb in hitboxes]

        # Limpiar checkboxes anteriores
        self._clear_checkboxes()

        self.checkboxes = []

        # Crear nuevos checkboxes con texto en color
        for i, hb in enumerate(hitboxes):
            checkbox = self._create_hitbox_checkbox(i, hb)
            self.checkbox_layout.addWidget(checkbox)

        # Aplicar el offset actual a los nuevos hitboxes
        if self.current_offset_x != 0 or self.current_offset_y != 0:
            self.apply_offset(self.current_offset_x, self.current_offset_y)
        else:
            self.video_widget.set_hitboxes([])

    def _clear_checkboxes(self):
        """Limpia todos los checkboxes existentes"""
        while self.checkbox_layout.count():
            child = self.checkbox_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _create_hitbox_checkbox(self, index, hitbox):
        """Crea un checkbox para un hitbox con botón de reproducción"""
        points = hitbox.get("points", 500)
        hb_with_index = hitbox.copy()
        hb_with_index["color_index"] = index

        # Calcular dimensiones
        x0, y0 = hitbox.get("x0", 0), hitbox.get("y0", 0)
        x1, y1 = hitbox.get("x1", 0), hitbox.get("y1", 0)
        ancho = x1 - x0
        alto = y1 - y0

        frame_start = hitbox.get("frame_start")
        frame_end = hitbox.get("frame_end")

        # Obtener color
        color = VideoPlayer.HITBOX_COLORS[index % len(VideoPlayer.HITBOX_COLORS)]
        color_hex = color.name()

        row_widget = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_widget.setLayout(row_layout)

        # Crear checkbox con valores decimales
        checkbox_text = f"Hb {index + 1} ({x0}, {y0}) → ({x1}, {y1})"

        cb = QCheckBox(checkbox_text)
        cb.setStyleSheet(f"""
            QCheckBox {{
                color: {color_hex};
                font-weight: bold;
            }}
        """)

        # Tooltip con información
        tooltip = f"""Hitbox #{index + 1}
Puntos: {points}
Coordenadas: ({x0}, {y0}) → ({x1}, {y1})
Hexadecimal: (0x{x0:02X}, 0x{y0:02X}) → (0x{x1:02X}, 0x{y1:02X})
Ancho: {ancho} px
Alto: {alto} px"""

        if frame_start is not None and frame_end is not None:
            tooltip += f"\nFrames: {frame_start} - {frame_end} ({frame_end - frame_start + 1} frames)"

        cb.setToolTip(tooltip)

        cb.stateChanged.connect(
            lambda state, h=hb_with_index: self._on_checkbox_changed(state, h)
        )

        row_layout.addWidget(cb)

        # botón de reproducción
        if (
            frame_start is not None
            and frame_end is not None
            and self.play_frame_callback
        ):
            play_btn = QPushButton(f"▶ {frame_start}-{frame_end}")
            # print(f"Botón para frames {frame_start}-{frame_end}")
            play_btn.setFixedWidth(30)
            play_btn.setToolTip(f"Reproducir frames {frame_start}-{frame_end}")
            play_btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    opacity: 0.8;
                }
            """)
            play_btn.clicked.connect(
                lambda: self._play_hitbox_frames(
                    frame_start, frame_end, [hb_with_index]
                )
            )
            row_layout.addWidget(play_btn)

        self.checkboxes.append((cb, hb_with_index))

        return row_widget

    def _on_checkbox_changed(self, state, hitbox):
        """Se llama cuando cambia el estado de un checkbox"""
        self._update_active_hitboxes()

    def _update_active_hitboxes(self):
        """Actualiza los hitboxes activos en el video"""
        active_boxes = []
        for cb, hb in self.checkboxes:
            if cb.isChecked():
                active_boxes.append(hb)
        self.video_widget.set_hitboxes(active_boxes)

    def apply_offset(self, offset_x, offset_y):
        """Aplica el offset global a todos los hitboxes"""
        self.current_offset_x = offset_x
        self.current_offset_y = offset_y

        # Actualizar coordenadas
        for i, (_, hb) in enumerate(self.checkboxes):
            original = self.original_hitboxes[i]
            hb["x0"] = original["x0"] + offset_x
            hb["y0"] = original["y0"] + offset_y
            hb["x1"] = original["x1"] + offset_x
            hb["y1"] = original["y1"] + offset_y

        # Re-dibujar hitboxes activos
        self._update_active_hitboxes()

    def select_all(self):
        """Marca todos los checkboxes"""
        for cb, _ in self.checkboxes:
            cb.setChecked(True)

    def deselect_all(self):
        """Desmarca todos los checkboxes"""
        for cb, _ in self.checkboxes:
            cb.setChecked(False)

    def _play_hitbox_frames(self, start, end, hitboxes):
        """Reproduce los frames específicos del hitbox sin reconstruir la UI"""
        self.video_widget.set_hitboxes(hitboxes)

        # reproducir los frames usando el video widget directamente
        # para evitar que el callback reconstruya la UI
        self.video_widget.play_loop(start, end)
