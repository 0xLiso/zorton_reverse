from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton


class FrameButtonManager:
    """Gestiona la navegación por paths del grafo y nodos dentro de cada path"""

    def __init__(
        self, buttons_layout, play_frame_loop_callback, history_update_callback=None
    ):
        self.buttons_layout = buttons_layout
        self.play_frame_loop_callback = play_frame_loop_callback
        self.history_update_callback = history_update_callback

        # grafo
        self.paths = []
        self.current_path_idx = 0
        self.current_node_idx = 0

        # UI
        self.path_nav_layout = None
        self.node_nav_layout = None
        self.info_label = None
        self.path_label = None
        self.node_label = None
        self.node_info_label = None

    def update_paths(self, paths):
        """Actualiza los paths del grafo"""
        self._clear_buttons()

        self.paths = paths
        self.current_path_idx = 0
        self.current_node_idx = 0

        if not paths:
            no_data_label = QLabel("No hay paths en esta escena")
            no_data_label.setStyleSheet(
                "color: #888; font-style: italic; padding: 10px;"
            )
            self.buttons_layout.addWidget(no_data_label)
            return

        # controles de navegación
        self._create_navigation_controls()
        self._update_display()

    def _create_navigation_controls(self):
        """Crea los controles de navegación de paths y nodos"""

        path_header = QLabel("Paths:")
        path_header.setStyleSheet("font-weight: bold; margin-top: 10px;")
        self.buttons_layout.addWidget(path_header)

        self.path_nav_layout = QHBoxLayout()

        prev_path_btn = QPushButton("◀ Path Anterior")
        prev_path_btn.clicked.connect(self._prev_path)
        self.path_nav_layout.addWidget(prev_path_btn)

        self.path_label = QLabel()
        self.path_label.setStyleSheet("text-align: center; padding: 5px;")
        self.path_nav_layout.addWidget(self.path_label, 1)

        next_path_btn = QPushButton("Path Siguiente ▶")
        next_path_btn.clicked.connect(self._next_path)
        self.path_nav_layout.addWidget(next_path_btn)

        self.buttons_layout.addLayout(self.path_nav_layout)

        # path actual
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #666; font-size: 18px; padding: 5px;")
        self.buttons_layout.addWidget(self.info_label)

        # nodos
        node_header = QLabel("Nodos en el path:")
        node_header.setStyleSheet("font-weight: bold; margin-top: 15px;")
        self.buttons_layout.addWidget(node_header)

        self.node_nav_layout = QHBoxLayout()

        prev_node_btn = QPushButton("◀ Nodo Anterior")
        prev_node_btn.clicked.connect(self._prev_node)
        self.node_nav_layout.addWidget(prev_node_btn)

        self.node_label = QLabel()
        self.node_label.setStyleSheet("text-align: center; padding: 5px;")
        self.node_nav_layout.addWidget(self.node_label, 1)

        next_node_btn = QPushButton("Nodo Siguiente ▶")
        next_node_btn.clicked.connect(self._next_node)
        self.node_nav_layout.addWidget(next_node_btn)

        self.buttons_layout.addLayout(self.node_nav_layout)

        # info adicional del nodo (mem offset y respawn)
        self.node_info_label = QLabel()
        self.node_info_label.setStyleSheet(
            "color: #888; font-size: 10px; padding: 5px; font-family: monospace;"
        )
        self.node_info_label.setWordWrap(True)
        self.buttons_layout.addWidget(self.node_info_label)

        # botónm para reproducir frames del nodo actual
        self.play_node_layout = QHBoxLayout()
        self.play_node_btn = QPushButton()
        self.play_node_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.play_node_btn.clicked.connect(self._replay_current_node)
        self.play_node_layout.addWidget(self.play_node_btn)

        self.buttons_layout.addLayout(self.play_node_layout)

    def _prev_path(self):
        """Navegar al path anterior"""
        if self.current_path_idx > 0:
            self.current_path_idx -= 1
            self.current_node_idx = 0
            self._update_display()

    def _next_path(self):
        """Navegar al path siguiente"""
        if self.current_path_idx < len(self.paths) - 1:
            self.current_path_idx += 1
            self.current_node_idx = 0
            self._update_display()

    def _prev_node(self):
        """Navegar al nodo anterior en el path actual"""
        if self.current_node_idx > 0:
            self.current_node_idx -= 1
            self._update_display()

    def _next_node(self):
        """Navegar al nodo siguiente en el path actual"""
        current_path = self.paths[self.current_path_idx]
        if self.current_node_idx < len(current_path["nodes"]) - 1:
            self.current_node_idx += 1
            self._update_display()

    def _update_display(self):
        """Actualiza la visualización del nodo actual"""
        if not self.paths or self.current_path_idx >= len(self.paths):
            return

        current_path = self.paths[self.current_path_idx]
        nodes = current_path["nodes"]

        if self.current_node_idx >= len(nodes):
            self.current_node_idx = 0

        current_node = nodes[self.current_node_idx]

        # actualizar labels
        self.path_label.setText(f"Path {self.current_path_idx + 1} / {len(self.paths)}")  # type: ignore

        total_frames = current_path.get("total_frames", 0)
        total_hitboxes = current_path.get("total_hitboxes", 0)
        self.info_label.setText(  # type: ignore
            f"Total: {len(nodes)} nodos | {total_frames} frames | {total_hitboxes} hitboxes"
        )

        self.node_label.setText(f"Nodo {self.current_node_idx + 1} / {len(nodes)}")  # type: ignore

        mem_offset = current_node.get("mem", "N/A")
        ptr_respawn = current_node.get("ptr_node_respawn")

        info_parts = [f"Mem: {mem_offset}"]

        if ptr_respawn:
            info_parts.append(f"💀 Respawn: {ptr_respawn}")

        self.node_info_label.setText(" | ".join(info_parts))  # type: ignore

        # reproducir frames del nodo actual
        frame_start = current_node.get("frame_start")
        frame_end = current_node.get("frame_end")

        if frame_start is not None and frame_end is not None:
            duration = frame_end - frame_start + 1
            self.play_node_btn.setText(
                f"▶ Reproducir nodo: {frame_start}-{frame_end} ({duration} frames)"
            )
            self.play_node_btn.setEnabled(True)
            self.play_frame_loop_callback(
                frame_start, frame_end, current_node.get("hitboxes", [])
            )
        else:
            self.play_node_btn.setText("▶ Reproducir nodo (sin frames)")
            self.play_node_btn.setEnabled(False)

    def _replay_current_node(self):
        """Reproduce nuevamente el nodo actual"""
        if not self.paths or self.current_path_idx >= len(self.paths):
            return

        current_path = self.paths[self.current_path_idx]
        nodes = current_path["nodes"]

        if self.current_node_idx >= len(nodes):
            return

        current_node = nodes[self.current_node_idx]
        frame_start = current_node.get("frame_start")
        frame_end = current_node.get("frame_end")

        if frame_start is not None and frame_end is not None:
            self.play_frame_loop_callback(
                frame_start, frame_end, current_node.get("hitboxes", [])
            )

    def get_current_node(self):
        """Retorna el nodo actual"""
        if not self.paths or self.current_path_idx >= len(self.paths):
            return None

        current_path = self.paths[self.current_path_idx]
        nodes = current_path["nodes"]

        if self.current_node_idx >= len(nodes):
            return None

        return nodes[self.current_node_idx]

    def _clear_buttons(self):
        """Limpia todos los botones existentes"""

        # TODO: overkill, esto no es eficiente, pyside debe tener mejor forma de manejar layouts
        while self.buttons_layout.count():
            child = self.buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    subchild = child.layout().takeAt(0)
                    if subchild.widget():
                        subchild.widget().deleteLater()

    def activate_first_node(self):
        """Activa el primer nodo del primer path"""
        if self.paths:
            self.current_path_idx = 0
            self.current_node_idx = 0
            self._update_display()

    def reset_history(self):
        """Resetear el historial"""
        if self.history_update_callback:
            self.history_update_callback([])

    def clear_active_button(self):
        """Desmarca el botón activo"""
        ...
