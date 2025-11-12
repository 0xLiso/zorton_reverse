import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from zb_analyzer.config_manager import ConfigManager
from zb_analyzer.frame_buttons import FrameButtonManager
from zb_analyzer.hitbox_controls import HitboxControlsPanel
from zb_analyzer.hitbox_manager import HitboxManager
from zb_analyzer.playback_controls import PlaybackControls
from zb_analyzer.scene_loader import SceneDataLoader
from zb_analyzer.video_player import VideoPlayer


class FileSelectionDialog(QDialog):
    """seleccionar archivos de video y datos"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar archivos")
        self.setModal(True)
        self.resize(600, 200)

        self.config_manager = config_manager
        self.video_path = config_manager.get_last_video_path()
        self.json_path = config_manager.get_last_json_path()

        # layout principal
        layout = QVBoxLayout()

        video_label = QLabel("Archivo de video:")
        layout.addWidget(video_label)

        video_layout = QHBoxLayout()
        self.video_input = QLineEdit()
        self.video_input.setPlaceholderText("Selecciona un archivo de video...")
        self.video_input.setReadOnly(True)
        if self.video_path:
            self.video_input.setText(self.video_path)
        video_layout.addWidget(self.video_input)

        video_btn = QPushButton("Examinar...")
        video_btn.clicked.connect(self.select_video)
        video_layout.addWidget(video_btn)
        layout.addLayout(video_layout)

        json_label = QLabel("Archivo JSON de escenas:")
        layout.addWidget(json_label)

        json_layout = QHBoxLayout()
        self.json_input = QLineEdit()
        self.json_input.setPlaceholderText("Selecciona un archivo JSON...")
        self.json_input.setReadOnly(True)
        if self.json_path:
            self.json_input.setText(self.json_path)
        json_layout.addWidget(self.json_input)

        json_btn = QPushButton("Examinar...")
        json_btn.clicked.connect(self.select_json)
        json_layout.addWidget(json_btn)
        layout.addLayout(json_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("Aceptar")
        ok_btn.clicked.connect(self.accept_selection)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def select_video(self):
        """diálogo para seleccionar archivo de video"""
        start_dir = self.config_manager.get_last_video_directory()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de video",
            start_dir,
            "",
        )
        if file_path:
            self.video_input.setText(file_path)
            self.video_path = file_path

    def select_json(self):
        """diálogo para seleccionar archivo JSON"""
        start_dir = self.config_manager.get_last_json_directory()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo JSON",
            start_dir,
            "JSON (zb.json);;Todos los archivos (*.*)",
        )
        if file_path:
            self.json_input.setText(file_path)
            self.json_path = file_path

    def accept_selection(self):
        if not self.video_path:
            QMessageBox.warning(
                self, "Error", "Por favor, selecciona un archivo de video."
            )
            return
        if not self.json_path:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un archivo JSON.")
            return
        self.accept()

    def get_paths(self):
        return self.video_path, self.json_path


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""

    def __init__(self, video_path, json_path):  # noqa: PLR0915
        super().__init__()
        self.setWindowTitle("Zorton Brothers Analyzer")
        self.resize(1400, 800)

        self.scene_loader = SceneDataLoader(json_path)
        self.scenes = self.scene_loader.load_scenes()

        self.video_widget = VideoPlayer()
        self.video_widget.load_video(video_path)

        self.scene_selector = QComboBox()
        self.scene_selector.addItems(
            [
                f"Escena #{scene.get('id', i)} - {scene['offset']}"
                for i, scene in enumerate(self.scenes)
            ]
        )
        self.scene_selector.currentIndexChanged.connect(self.on_scene_changed)

        # navegación de escenas
        self.prev_scene_btn = QPushButton("↑")
        self.prev_scene_btn.setFixedWidth(40)
        self.prev_scene_btn.clicked.connect(self.prev_scene)

        self.next_scene_btn = QPushButton("↓")
        self.next_scene_btn.setFixedWidth(40)
        self.next_scene_btn.clicked.connect(self.next_scene)

        # información del video
        self.info_btn = QPushButton("ℹ️")
        self.info_btn.setFixedWidth(40)
        self.info_btn.setToolTip("Información del video")
        self.info_btn.clicked.connect(self.show_video_info)

        # selector de escenas
        scene_selector_layout = QHBoxLayout()
        scene_selector_layout.addWidget(self.scene_selector)
        scene_selector_layout.addWidget(self.prev_scene_btn)
        scene_selector_layout.addWidget(self.next_scene_btn)
        scene_selector_layout.addWidget(self.info_btn)

        # controles de reproducción
        self.playback_controls = PlaybackControls()
        self.playback_controls.connect_signals(
            self.toggle_play_pause,
            lambda: self.video_widget.seek_frame(-1),
            lambda: self.video_widget.seek_frame(1),
        )

        self.is_playing = False

        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.update_frame_display)
        self.frame_timer.start(100)

        manual_frame_widget = QWidget()
        manual_frame_main_layout = QHBoxLayout()
        manual_frame_widget.setLayout(manual_frame_main_layout)

        # loop manual
        loop_widget = QWidget()
        loop_layout = QVBoxLayout()
        loop_widget.setLayout(loop_layout)

        loop_label = QLabel("Loop manual:")
        loop_layout.addWidget(loop_label)

        loop_inputs_layout = QHBoxLayout()
        self.manual_start_spin = QSpinBox()
        self.manual_start_spin.setRange(0, 999999)
        self.manual_start_spin.setPrefix("Inicio: ")
        loop_inputs_layout.addWidget(self.manual_start_spin)

        self.manual_end_spin = QSpinBox()
        self.manual_end_spin.setRange(0, 999999)
        self.manual_end_spin.setPrefix("Fin: ")
        loop_inputs_layout.addWidget(self.manual_end_spin)
        loop_layout.addLayout(loop_inputs_layout)

        manual_play_btn = QPushButton("Reproducir loop")
        manual_play_btn.clicked.connect(self.play_manual_loop)
        loop_layout.addWidget(manual_play_btn)

        #
        goto_widget = QWidget()
        goto_layout = QVBoxLayout()
        goto_widget.setLayout(goto_layout)

        goto_label = QLabel("Ir a frame:")
        goto_layout.addWidget(goto_label)

        self.goto_frame_spin = QSpinBox()
        self.goto_frame_spin.setRange(0, 999999)
        self.goto_frame_spin.setPrefix("Frame: ")
        goto_layout.addWidget(self.goto_frame_spin)

        goto_frame_btn = QPushButton("Ir")
        goto_frame_btn.clicked.connect(self.goto_frame)
        goto_layout.addWidget(goto_frame_btn)

        manual_frame_main_layout.addWidget(loop_widget)
        manual_frame_main_layout.addWidget(goto_widget)

        left_layout = QVBoxLayout()
        left_layout.addLayout(scene_selector_layout)
        left_layout.addWidget(self.video_widget)
        left_layout.addWidget(self.playback_controls)
        left_layout.addWidget(manual_frame_widget)

        right_layout = QVBoxLayout()

        self.hitbox_controls = HitboxControlsPanel()

        self.checkbox_widget = QWidget()
        self.checkbox_layout = QVBoxLayout()
        self.checkbox_widget.setLayout(self.checkbox_layout)

        scroll = QScrollArea()
        scroll.setWidget(self.checkbox_widget)
        scroll.setWidgetResizable(True)

        self.hitbox_manager = HitboxManager(self.checkbox_layout, self.video_widget)

        # conectar controles de hitboxes
        self.hitbox_controls.connect_select_buttons(
            self.hitbox_manager.select_all, self.hitbox_manager.deselect_all
        )
        self.hitbox_controls.offset_x_spin.valueChanged.connect(
            lambda: self.hitbox_manager.apply_offset(
                self.hitbox_controls.offset_x_spin.value(),
                self.hitbox_controls.offset_y_spin.value(),
            )
        )
        self.hitbox_controls.offset_y_spin.valueChanged.connect(
            lambda: self.hitbox_manager.apply_offset(
                self.hitbox_controls.offset_x_spin.value(),
                self.hitbox_controls.offset_y_spin.value(),
            )
        )

        self.buttons_widget = QWidget()
        self.buttons_layout = QVBoxLayout()
        self.buttons_widget.setLayout(self.buttons_layout)

        scroll_buttons = QScrollArea()
        scroll_buttons.setWidget(self.buttons_widget)
        scroll_buttons.setWidgetResizable(True)

        self.frame_button_manager = FrameButtonManager(
            self.buttons_layout, self.play_frame_loop, self.update_frame_history
        )

        # historial de frames
        frames_header_layout = QHBoxLayout()
        frames_header_layout.addWidget(QLabel("Frames:"))

        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setFixedHeight(30)
        history_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        history_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.history_label = QLabel("-")
        self.history_label.setStyleSheet("color: #888; font-style: italic;")
        history_scroll.setWidget(self.history_label)

        frames_header_layout.addWidget(history_scroll, 1)

        reset_history_btn = QPushButton("↻")
        reset_history_btn.setFixedWidth(30)
        reset_history_btn.setToolTip("Resetear historial")
        reset_history_btn.clicked.connect(self.reset_frame_history)
        frames_header_layout.addWidget(reset_history_btn)

        # panel derecho
        right_layout.addWidget(QLabel("Hitboxes:"))
        right_layout.addWidget(self.hitbox_controls)
        right_layout.addWidget(scroll, 1)
        right_layout.addLayout(frames_header_layout)
        right_layout.addWidget(scroll_buttons, 1)

        main_layout = QHBoxLayout()
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        main_layout.addWidget(left_widget, 2)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.on_scene_changed(0)  # carga de primera escena del json

        # reproducción
        self.video_widget.play()
        self.is_playing = True
        self.playback_controls.set_play_state(self.is_playing)

    def on_scene_changed(self, index):
        if index < 0 or index >= len(self.scenes):
            return

        scene = self.scenes[index]
        print(f"Cambiando a escena {index + 1}: {scene['offset']}")

        self.hitbox_manager.update_hitboxes(scene["hitboxes"])
        self.frame_button_manager.update_frame_buttons(scene["frames"])
        self.frame_button_manager.reset_history()
        self.frame_button_manager.activate_first_frame()

    def toggle_play_pause(self):
        if self.is_playing:
            self.video_widget.pause()
            self.is_playing = False
        else:
            self.video_widget.play()
            self.is_playing = True

        self.playback_controls.set_play_state(self.is_playing)

    def play_frame_loop(self, start, end):
        self.video_widget.play_loop(start, end)
        if not self.is_playing:
            self.is_playing = True
            self.playback_controls.set_play_state(self.is_playing)

    def stop_loop(self):
        self.video_widget.stop_loop()
        if not self.is_playing:
            self.is_playing = True
            self.playback_controls.set_play_state(self.is_playing)

    def update_frame_display(self):
        current_frame = self.video_widget.get_current_frame_number()
        self.playback_controls.update_frame_label(current_frame)

    def prev_scene(self):
        """cambiar a la escena anterior"""
        current = self.scene_selector.currentIndex()
        if current > 0:
            self.scene_selector.setCurrentIndex(current - 1)

    def next_scene(self):
        """cambiar a la siguiente escena"""
        current = self.scene_selector.currentIndex()
        if current < len(self.scenes) - 1:
            self.scene_selector.setCurrentIndex(current + 1)

    def play_manual_loop(self):
        """reproducir loop con frames manuales"""
        start = self.manual_start_spin.value()
        end = self.manual_end_spin.value()

        if start > end:
            QMessageBox.warning(
                self, "Error", "El frame inicial debe ser menor o igual al final."
            )
            return

        # desmarcar el botón de frames activo para no confundir
        self.frame_button_manager.clear_active_button()

        self.play_frame_loop(start, end)

    def show_video_info(self):
        """mostrar información del video"""
        info = self.video_widget.get_video_info()

        if not info:
            QMessageBox.warning(
                self, "Error", "No hay información del video disponible."
            )
            return

        minutes = int(info["duration"] // 60)
        seconds = info["duration"] % 60

        message = f"""<b>Información del video</b><br><br>
<b>Ruta:</b> {info["path"]}<br>
<b>Resolución:</b> {info["width"]} x {info["height"]} px<br>
<b>FPS:</b> {info["fps"]:.2f}<br>
<b>Total de frames:</b> {info["total_frames"]}<br>
<b>Duración:</b> {minutes}m {seconds:.2f}s"""

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Información del video")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(message)
        msg_box.exec()

    def update_frame_history(self, history):
        """actualizar el label del historial de frames"""
        if history:
            history_text = ", ".join([f"#{num}" for num in history])
            self.history_label.setText(f"{history_text}")
        else:
            self.history_label.setText("-")

    def reset_frame_history(self):
        """resetear el historial de frames"""
        self.frame_button_manager.reset_history()

    def goto_frame(self):
        """saltar a un frame específico"""
        frame = self.goto_frame_spin.value()

        if frame < 0 or frame >= self.video_widget.total_frames:
            QMessageBox.warning(
                self,
                "Error",
                f"Frame fuera de rango. El video tiene {self.video_widget.total_frames} frames (0-{self.video_widget.total_frames - 1}).",
            )
            return

        # pausar si está reproduciendo
        if self.is_playing:
            self.video_widget.pause()
            self.is_playing = False
            self.playback_controls.set_play_state(self.is_playing)

        self.frame_button_manager.clear_active_button()

        self.video_widget.goto_frame(frame)


def main():
    app = QApplication(sys.argv)

    config_manager = ConfigManager()

    dialog = FileSelectionDialog(config_manager)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return 0

    video_path, json_path = dialog.get_paths()
    config_manager.set_paths(video_path, json_path)

    window = MainWindow(video_path, json_path)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
