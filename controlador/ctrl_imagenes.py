from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from modelo import ModeloImagenes

class ControladorImagenes:
    def __init__(self, vista, db_manager=None, id_sesion=None):
        self.vista = vista
        self.modelo = ModeloImagenes()
        self.db_manager = db_manager
        self.id_sesion = id_sesion
        self._conectar_eventos()

    def _conectar_eventos(self):
        if hasattr(self.vista, 'btnCargarImagenMedica'):
            self.vista.btnCargarImagenMedica.clicked.connect(self.cargar_dicom)
        if hasattr(self.vista, 'btnConvertirNifti'):
            self.vista.btnConvertirNifti.clicked.connect(self.convertir_nifti)
        if hasattr(self.vista, 'btnGuardarMetadata'):
            self.vista.btnGuardarMetadata.clicked.connect(self.guardar_metadata)
        if hasattr(self.vista, 'btnVolver'):
            self.vista.btnVolver.clicked.connect(self.vista.close)

        if hasattr(self.vista, 'sliderAxial'):
            self.vista.sliderAxial.valueChanged.connect(self.actualizar_axial)
        if hasattr(self.vista, 'sliderCoronal'):
            self.vista.sliderCoronal.valueChanged.connect(self.actualizar_coronal)
        if hasattr(self.vista, 'sliderSagital'):
            self.vista.sliderSagital.valueChanged.connect(self.actualizar_sagital)

        if hasattr(self.vista, 'btnZoom'):
            self.vista.btnZoom.clicked.connect(self.aplicar_zoom)
        if hasattr(self.vista, 'btnSegmentar'):
            self.vista.btnSegmentar.clicked.connect(self.aplicar_segmentacion)
        if hasattr(self.vista, 'btnMorfologia'):
            self.vista.btnMorfologia.clicked.connect(self.aplicar_morfologia)

    def cargar_dicom(self):
        ruta = QFileDialog.getExistingDirectory(self.vista, "Seleccionar carpeta DICOM")
        if not ruta:
            return

        try:
            matriz, metadata = self.modelo.cargar_dicom(ruta)
            self._mostrar_metadata(metadata)
            self._configurar_sliders()

            QMessageBox.information(self.vista, "Exito", "DICOM cargado correctamente")

            if self.db_manager and self.id_sesion:
                self.db_manager.agregar_accion(self.id_sesion, f"Cargo DICOM: {ruta}")

        except Exception as e:
            QMessageBox.critical(self.vista, "Error", str(e))

    def _mostrar_metadata(self, metadata):
        if hasattr(self.vista, 'lbl_paciente_id'):
            self.vista.lbl_paciente_id.setText(metadata.get('Patient ID', 'N/A'))
        if hasattr(self.vista, 'lbl_paciente_nombre'):
            self.vista.lbl_paciente_nombre.setText(metadata.get('Patient Name', 'N/A'))
        if hasattr(self.vista, 'lbl_fecha_estudio'):
            self.vista.lbl_fecha_estudio.setText(metadata.get('Study Date', 'N/A'))
        if hasattr(self.vista, 'lbl_modalidad'):
            self.vista.lbl_modalidad.setText(metadata.get('Study Modality', 'N/A'))

    def _configurar_sliders(self):
        dims = self.modelo.obtener_dimensiones()
        if hasattr(self.vista, 'sliderAxial'):
            self.vista.sliderAxial.setMaximum(dims[0] - 1)
        if hasattr(self.vista, 'sliderCoronal'):
            self.vista.sliderCoronal.setMaximum(dims[1] - 1)
        if hasattr(self.vista, 'sliderSagital'):
            self.vista.sliderSagital.setMaximum(dims[2] - 1)

    def actualizar_axial(self, valor):
        img = self.modelo.obtener_corte_axial(valor)
        if img is not None and hasattr(self.vista, 'lbl_axial'):
            self._mostrar_imagen(self.vista.lbl_axial, img)

    def actualizar_coronal(self, valor):
        img = self.modelo.obtener_corte_coronal(valor)
        if img is not None and hasattr(self.vista, 'lbl_coronal'):
            self._mostrar_imagen(self.vista.lbl_coronal, img)

    def actualizar_sagital(self, valor):
        img = self.modelo.obtener_corte_sagital(valor)
        if img is not None and hasattr(self.vista, 'lbl_sagital'):
            self._mostrar_imagen(self.vista.lbl_sagital, img)

    def _mostrar_imagen(self, label, imagen_np):
        h, w = imagen_np.shape
        qimg = QImage(imagen_np.data, w, h, w, QImage.Format_Grayscale8)
        label.setPixmap(QPixmap.fromImage(qimg).scaled(label.size()))

    def convertir_nifti(self):
        if self.modelo.matriz_3d is None:
            QMessageBox.warning(self.vista, "Advertencia", "Cargue una imagen DICOM primero")
            return

        ruta = QFileDialog.getSaveFileName(self.vista, "Guardar como NIFTI", "", "NIFTI (*.nii)")[0]
        if ruta:
            try:
                salida = self.modelo.convertir_dicom_a_nifti(ruta)
                QMessageBox.information(self.vista, "Exito", f"Convertido a: {salida}")
            except Exception as e:
                QMessageBox.critical(self.vista, "Error", str(e))

    def guardar_metadata(self):
        if not self.modelo.metadata:
            QMessageBox.warning(self.vista, "Advertencia", "No hay metadata para guardar")
            return

        ruta = QFileDialog.getSaveFileName(self.vista, "Guardar CSV", "", "CSV (*.csv)")[0]
        if ruta:
            try:
                self.modelo.guardar_metadata_csv(ruta)
                QMessageBox.information(self.vista, "Exito", "Metadata guardada")
            except Exception as e:
                QMessageBox.critical(self.vista, "Error", str(e))

    def aplicar_zoom(self):

    def aplicar_segmentacion(self):

    def aplicar_morfologia(self):