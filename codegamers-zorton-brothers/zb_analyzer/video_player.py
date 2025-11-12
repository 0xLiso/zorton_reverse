import cv2
from PySide6.QtCore import QRect, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel


class VideoPlayer(QLabel):
    """Widget para reproducir video y visualizar hitboxes"""

    HITBOX_COLORS = [
        QColor(255, 0, 0),  # Rojo
        QColor(0, 255, 0),  # Verde
        QColor(0, 100, 255),  # Azul
        QColor(255, 255, 0),  # Amarillo
        QColor(255, 0, 255),  # Magenta
        QColor(0, 255, 255),  # Cian
        QColor(255, 128, 0),  # Naranja
        QColor(128, 0, 255),  # Púrpura
        QColor(255, 192, 203),  # Rosa
        QColor(0, 255, 128),  # Verde menta
        QColor(255, 64, 64),  # Rojo claro
        QColor(64, 255, 64),  # Verde claro
        QColor(64, 64, 255),  # Azul claro
        QColor(255, 215, 0),  # Dorado
        QColor(255, 99, 71),  # Tomate
    ]

    def __init__(self):
        super().__init__()
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.current_frame = None
        self.hitboxes = []  # lista de (x0, y0, x1, y1, color_idx)
        # escala fija para Amiga 68k (320x256 → 720x576)
        self.amiga_width = 320
        self.amiga_height = 256
        self.display_width = 720
        self.display_height = 576
        self.scale_x = self.display_width / self.amiga_width  # 2.25
        self.scale_y = self.display_height / self.amiga_height  # 2.25
        self.setAlignment(Qt.AlignCenter)
        self.setText("No se ha podido cargar ningún vídeo.")
        self.loop_enabled = False
        self.loop_start = 0
        self.loop_end = 0
        self.total_frames = 0
        self.video_path = None

        self.setMouseTracking(True)
        self.mouse_x = -1
        self.mouse_y = -1
        self.show_mouse_coords = False

    def load_video(self, path):
        """cargar archivo de video"""
        self.video_path = path
        self.cap = cv2.VideoCapture(path)
        if self.cap.isOpened():
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            video_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"Video cargado: {video_width}x{video_height}")
            print(
                f"Escala Amiga: {self.amiga_width}x{self.amiga_height} → Display: {self.display_width}x{self.display_height}"
            )
            print(f"Escala: {self.scale_x:.4f}x (ancho), {self.scale_y:.4f}x (alto)")
        else:
            self.total_frames = 0
            print("Error: no se pudo abrir el video")
        self.timer.start(40)  # ~25 FPS

    def update_frame(self):
        """actualiza el frame actual del video"""
        if not (self.cap and self.cap.isOpened()):
            return

        current = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

        # reiniciar bucle
        if self.loop_enabled and current > self.loop_end:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.loop_start)
            current = self.loop_start

        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            self.display_frame()
        else:
            self.timer.stop()

    def display_frame(self):
        """mostrar el frame actual con hitboxes y coordenadas del mouse"""
        if self.current_frame is None:
            return
        frame = self.current_frame.copy()

        # convertir BGR (OpenCV) → RGB (Qt)
        # doc oficial de QT6
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        painter = QPainter(pixmap)

        self._draw_hitboxes(painter, pixmap)
        self._draw_mouse_coords(painter, pixmap)

        painter.end()

        self.setPixmap(
            pixmap.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        )

    def _draw_hitboxes(self, painter, pixmap):
        """dibujar hitboxes en el frame"""
        for hitbox_data in self.hitboxes:
            x0, y0, x1, y1, color_idx = hitbox_data
            color = self.HITBOX_COLORS[color_idx % len(self.HITBOX_COLORS)]
            pen = QPen(color, 3)
            painter.setPen(pen)

            scaled_rect = QRect(
                int(x0 * self.scale_x),
                int(y0 * self.scale_y),
                int((x1 - x0) * self.scale_x),
                int((y1 - y0) * self.scale_y),
            )
            painter.drawRect(scaled_rect)

    def _draw_mouse_coords(self, painter, pixmap):
        """dibujar coordenadas del mouse y una cruz de guía"""
        if not (self.show_mouse_coords and self.mouse_x >= 0 and self.mouse_y >= 0):
            return

        video_x = int(self.mouse_x / self.scale_x)
        video_y = int(self.mouse_y / self.scale_y)

        # doc oficial de QT6
        pen = QPen(QColor(255, 255, 0), 2)
        painter.setPen(pen)
        painter.drawLine(0, self.mouse_y, pixmap.width(), self.mouse_y)
        painter.drawLine(self.mouse_x, 0, self.mouse_x, pixmap.height())

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)

        text = f"X: {video_x}, Y: {video_y}"
        text_rect = painter.boundingRect(0, 0, 0, 0, 0, text)
        text_x = self.mouse_x + 10
        text_y = self.mouse_y - 10

        if text_x + text_rect.width() > pixmap.width():
            text_x = self.mouse_x - text_rect.width() - 10
        if text_y - text_rect.height() < 0:
            text_y = self.mouse_y + 20

        bg_rect = QRect(
            text_x - 3,
            text_y - text_rect.height() - 3,
            text_rect.width() + 6,
            text_rect.height() + 6,
        )
        painter.fillRect(bg_rect, QColor(0, 0, 0, 180))

        pen = QPen(QColor(255, 255, 0))
        painter.setPen(pen)
        painter.drawText(text_x, text_y, text)

    def set_hitboxes(self, boxes):
        """establecer hitboxes a mostrar"""
        self.hitboxes = [
            (b["x0"], b["y0"], b["x1"], b["y1"], b.get("color_index", 0)) for b in boxes
        ]
        if self.current_frame is not None:
            self.display_frame()

    def pause(self):
        """pauser la reproducción"""
        self.timer.stop()

    def play(self):
        if self.cap:
            self.timer.start(40)

    # TODO: refactorizar seek_frame y goto_frame

    def seek_frame(self, delta):
        """saltar a un frame relativo"""
        if not self.cap:
            return
        current = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        new_frame = max(0, current + delta)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            self.display_frame()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

    def goto_frame(self, frame_number):
        """saltar a un frame específico"""
        if not self.cap:
            return

        frame_number = max(0, min(frame_number, self.total_frames - 1))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            self.display_frame()
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    def play_loop(self, start_frame, end_frame):
        """reproducir en bucle entre dos frames"""
        if not self.cap:
            return

        start_frame = max(0, min(start_frame, self.total_frames - 1))
        end_frame = max(start_frame, min(end_frame, self.total_frames - 1))

        self.loop_enabled = True
        self.loop_start = start_frame
        self.loop_end = end_frame

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame.copy()
            self.display_frame()
        else:
            print(f"Error: no se pudo leer el frame {start_frame}")

        self.play()

    def stop_loop(self):
        """detener el modo bucle"""
        self.loop_enabled = False
        self.play()

    def get_current_frame_number(self):
        if self.cap and self.cap.isOpened():
            return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        return 0

    def get_video_info(self):
        """obtener información del video"""
        if not self.cap or not self.cap.isOpened():
            return None

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = self.total_frames
        duration = total_frames / fps if fps > 0 else 0

        return {
            "path": self.video_path,
            "width": width,
            "height": height,
            "fps": fps,
            "total_frames": total_frames,
            "duration": duration,
        }

    def mouseMoveEvent(self, event):
        if self.pixmap() and not self.pixmap().isNull():
            pixmap_rect = self.pixmap().rect()
            widget_rect = self.rect()

            x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
            y_offset = (widget_rect.height() - pixmap_rect.height()) // 2

            pos = event.position()
            self.mouse_x = int(pos.x()) - x_offset
            self.mouse_y = int(pos.y()) - y_offset

            if (
                0 <= self.mouse_x < pixmap_rect.width()
                and 0 <= self.mouse_y < pixmap_rect.height()
            ):
                self.show_mouse_coords = True
                self.display_frame()
            else:
                self.show_mouse_coords = False
                self.display_frame()

    def leaveEvent(self, event):
        self.show_mouse_coords = False
        self.display_frame()
