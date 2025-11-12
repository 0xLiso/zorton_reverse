from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class PlaybackControls(QWidget):
    """Panel de reproducción"""

    def __init__(self):
        super().__init__()

        self.play_pause_btn = QPushButton("Play")
        self.prev_btn = QPushButton("Frame anterior")
        self.next_btn = QPushButton("Frame posterior")
        self.frame_label = QLabel("Frame: 0")

        self._create_layout()

    def _create_layout(self):
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_pause_btn)
        controls_layout.addWidget(self.next_btn)

        frame_layout = QHBoxLayout()
        frame_layout.addWidget(self.frame_label)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(frame_layout)

        self.setLayout(main_layout)

    def connect_signals(self, play_pause_callback, prev_callback, next_callback):
        self.play_pause_btn.clicked.connect(play_pause_callback)
        self.prev_btn.clicked.connect(prev_callback)
        self.next_btn.clicked.connect(next_callback)

    def update_frame_label(self, frame_number):
        self.frame_label.setText(f"Frame: {frame_number}")

    def set_play_state(self, is_playing):
        if is_playing:
            self.play_pause_btn.setText("Pause")
        else:
            self.play_pause_btn.setText("Play")
