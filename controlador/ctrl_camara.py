import cv2
import os
from datetime import datetime
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMessageBox


class ControladorCamara:
    def __init__(self, vista, db_manager=None, id_sesion=None, usuario=None):
        self.vista = vista
        self.db_manager = db_manager
        self.id_sesion = id_sesion
        self.usuario = usuario
        self.camara = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._actualizar_frame)
        self.foto_actual = None
        self._conectar_eventos()

    def _conectar_eventos(self):
        if hasattr(self.vista, 'btnIniciar'):
            self.vista.btnIniciar.clicked.connect(self.iniciar_camara)
        if hasattr(self.vista, 'btnCapturar'):
            self.vista.btnCapturar.clicked.connect(self.capturar_foto)
        if hasattr(self.vista, 'btnGuardar'):
            self.vista.btnGuardar.clicked.connect(self.guardar_foto)
        if hasattr(self.vista, 'btnCerrar'):
            self.vista.btnCerrar.clicked.connect(self.cerrar_camara)

    def iniciar_camara(self):
        self.camara = cv2.VideoCapture(0)
        if not self.camara.isOpened():
            QMessageBox.warning(self.vista, "Error", "No se pudo acceder a la camara")
            return False

        self.timer.start(30)
        if hasattr(self.vista, 'lblEstado'):
            self.vista.lblEstado.setText("Camara activa")
        return True

    def _actualizar_frame(self):
        if self.camara is None:
            return

        ret, frame = self.camara.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

            if hasattr(self.vista, 'lblStream'):
                self.vista.lblStream.setPixmap(QPixmap.fromImage(qimg).scaled(
                    self.vista.lblStream.size()))

    def capturar_foto(self):
        if self.camara is None:
            QMessageBox.warning(self.vista, "Advertencia", "Inicie la camara primero")
            return

        ret, frame = self.camara.read()
        if ret:
            self.foto_actual = frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

            if hasattr(self.vista, 'lblFoto'):
                self.vista.lblFoto.setPixmap(QPixmap.fromImage(qimg).scaled(
                    self.vista.lblFoto.size()))

            if hasattr(self.vista, 'lblEstado'):
                self.vista.lblEstado.setText("Foto capturada")

            QMessageBox.information(self.vista, "Exito", "Foto capturada")

    def guardar_foto(self):
        if self.foto_actual is None:
            QMessageBox.warning(self.vista, "Advertencia", "No hay foto capturada")
            return

        nombre = "usuario"
        if hasattr(self.vista, 'txtNombre'):
            nombre = self.vista.txtNombre.text()
        if not nombre:
            nombre = self.usuario if self.usuario else "usuario"

        os.makedirs("fotos_usuarios", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{nombre}_{timestamp}.jpg"
        ruta_foto = os.path.join("fotos_usuarios", nombre_archivo)
        cv2.imwrite(ruta_foto, self.foto_actual)

        if self.db_manager and self.id_sesion:
            self.db_manager.guardar_foto_usuario(self.id_sesion, ruta_foto)

        if hasattr(self.vista, 'lblEstado'):
            self.vista.lblEstado.setText(f"Foto guardada: {nombre_archivo}")

        QMessageBox.information(self.vista, "Exito", f"Foto guardada en: {ruta_foto}")

    def cerrar_camara(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.camara is not None:
            self.camara.release()
            self.camara = None
        if hasattr(self.vista, 'lblEstado'):
            self.vista.lblEstado.setText("Camara cerrada")
        self.vista.close()