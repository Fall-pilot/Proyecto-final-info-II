import numpy as np
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem
from modelo import ModeloSenales


class ControladorSenales:
    def __init__(self, vista, db_manager=None, id_sesion=None):
        self.vista = vista
        self.modelo = ModeloSenales()
        self.db_manager = db_manager
        self.id_sesion = id_sesion
        self._conectar_eventos()

    def _conectar_eventos(self):
        if hasattr(self.vista, 'btnCargarSenal'):
            self.vista.btnCargarSenal.clicked.connect(self.cargar_senal)
        if hasattr(self.vista, 'btnGraficarSenal'):
            self.vista.btnGraficarSenal.clicked.connect(self.graficar_senal)
        if hasattr(self.vista, 'btnAnadirRuido'):
            self.vista.btnAnadirRuido.clicked.connect(self.aplicar_ruido)
        if hasattr(self.vista, 'btnCalcularEstadisticas'):
            self.vista.btnCalcularEstadisticas.clicked.connect(self.calcular_estadisticas)
        if hasattr(self.vista, 'btnVolver'):
            self.vista.btnVolver.clicked.connect(self.vista.close)
        if hasattr(self.vista, 'rbCanales'):
            self.vista.rbCanales.toggled.connect(self._cambiar_eje)
        if hasattr(self.vista, 'rbTiempo'):
            self.vista.rbTiempo.toggled.connect(self._cambiar_eje)
        if hasattr(self.vista, 'spinBoxCanal'):
            self.vista.spinBoxCanal.valueChanged.connect(self._cambiar_canal)
        if hasattr(self.vista, 'sliderInicio'):
            self.vista.sliderInicio.valueChanged.connect(self._actualizar_segmento)
        if hasattr(self.vista, 'sliderFinal'):
            self.vista.sliderFinal.valueChanged.connect(self._actualizar_segmento)

    def cargar_senal(self):
        ruta = QFileDialog.getOpenFileName(self.vista, "Cargar Senal", "", "MAT files (*.mat)")[0]
        if not ruta:
            return

        try:
            self.modelo.cargar_senal(ruta)

            num_canales = self.modelo.obtener_num_canales()
            if hasattr(self.vista, 'spinBoxCanal'):
                self.vista.spinBoxCanal.setMaximum(num_canales - 1)
                self.vista.spinBoxCanal.setMinimum(0)
            longitud = self.modelo.obtener_longitud_tiempo()
            if hasattr(self.vista, 'sliderInicio'):
                self.vista.sliderInicio.setMaximum(longitud - 1)
            if hasattr(self.vista, 'sliderFinal'):
                self.vista.sliderFinal.setMaximum(longitud - 1)
                self.vista.sliderFinal.setValue(longitud - 1)
            if hasattr(self.vista, 'lblArchivo'):
                self.vista.lblArchivo.setText(self.modelo.nombre_archivo)

            self._mostrar_info_canales()

            QMessageBox.information(self.vista, "Exito", f"Senal cargada. Canales: {num_canales}")

            if self.db_manager and self.id_sesion:
                self.db_manager.agregar_accion(self.id_sesion, f"Cargo senal: {ruta}")

            self.graficar_senal()

        except Exception as e:
            QMessageBox.critical(self.vista, "Error", str(e))

    def _mostrar_info_canales(self):
        if not hasattr(self.vista, 'tablaCanales'):
            return

        num_canales = self.modelo.obtener_num_canales()
        self.vista.tablaCanales.setRowCount(num_canales)
        self.vista.tablaCanales.setColumnCount(3)
        self.vista.tablaCanales.setHorizontalHeaderLabels(["Canal", "Media", "Desviacion"])

        for i in range(num_canales):
            datos = self.modelo.obtener_datos_canal(i)
            if datos is not None:
                media = round(float(datos.mean()), 4)
                desviacion = round(float(datos.std()), 4)
                self.vista.tablaCanales.setItem(i, 0, QTableWidgetItem(f"Canal {i+1}"))
                self.vista.tablaCanales.setItem(i, 1, QTableWidgetItem(str(media)))
                self.vista.tablaCanales.setItem(i, 2, QTableWidgetItem(str(desviacion)))

    def graficar_senal(self):
        if self.modelo.senal_2d is None:
            QMessageBox.warning(self.vista, "Advertencia", "Cargue una senal primero")
            return

        canal = self.vista.spinBoxCanal.value() if hasattr(self.vista, 'spinBoxCanal') else 0
        inicio = self.vista.sliderInicio.value() if hasattr(self.vista, 'sliderInicio') else 0
        final = self.vista.sliderFinal.value() if hasattr(self.vista, 'sliderFinal') else -1

        if final == -1:
            final = self.modelo.obtener_longitud_tiempo()

        segmento, tiempo = self.modelo.seleccionar_segmento(canal, inicio, final)

        if segmento is not None and hasattr(self.vista, 'canvasGrafica'):
            self.vista.canvasGrafica.axes.clear()
            self.vista.canvasGrafica.axes.plot(tiempo, segmento, 'b-', linewidth=1)
            self.vista.canvasGrafica.axes.set_xlabel('Tiempo (s)')
            self.vista.canvasGrafica.axes.set_ylabel('Amplitud')
            self.vista.canvasGrafica.axes.set_title(f'Canal {canal+1} - Senal Biomedica')
            self.vista.canvasGrafica.axes.grid(True, alpha=0.3)
            self.vista.canvasGrafica.draw()

    def aplicar_ruido(self):
        if self.modelo.senal_2d is None:
            QMessageBox.warning(self.vista, "Advertencia", "Cargue una senal primero")
            return

        canal = self.vista.spinBoxCanal.value() if hasattr(self.vista, 'spinBoxCanal') else 0
        tipo_ruido = 'gaussiano'
        intensidad = 0.1

        if hasattr(self.vista, 'cbTipoRuido'):
            tipo_ruido = self.vista.cbTipoRuido.currentText().lower()

        if hasattr(self.vista, 'spinIntensidad'):
            intensidad = self.vista.spinIntensidad.value() / 100.0

        original, ruidosa = self.modelo.anadir_ruido(canal, tipo_ruido, intensidad)

        if hasattr(self.vista, 'canvasGrafica'):
            self.vista.canvasGrafica.axes.clear()

            tiempo = np.arange(len(original)) / self.modelo.fs

            self.vista.canvasGrafica.axes.plot(tiempo, original, 'b-', linewidth=1, label='Original')
            self.vista.canvasGrafica.axes.plot(tiempo, ruidosa, 'r-', linewidth=1, label=f'Con ruido {tipo_ruido}')
            self.vista.canvasGrafica.axes.set_xlabel('Tiempo (s)')
            self.vista.canvasGrafica.axes.set_ylabel('Amplitud')
            self.vista.canvasGrafica.axes.set_title(f'Canal {canal+1} - Comparacion')
            self.vista.canvasGrafica.axes.legend()
            self.vista.canvasGrafica.axes.grid(True, alpha=0.3)
            self.vista.canvasGrafica.draw()

            if self.db_manager and self.id_sesion:
                self.db_manager.agregar_accion(self.id_sesion, f"Aplico ruido {tipo_ruido} al canal {canal+1}")

    def calcular_estadisticas(self):
        if self.modelo.senal_2d is None:
            QMessageBox.warning(self.vista, "Advertencia", "Cargue una senal primero")
            return

        eje = 'canales'
        if hasattr(self.vista, 'rbTiempo') and self.vista.rbTiempo.isChecked():
            eje = 'tiempo'

        promedios, desviaciones, etiquetas = self.modelo.calcular_promedio_std(eje)

        if hasattr(self.vista, 'canvasEstadisticas'):
            self.vista.canvasEstadisticas.axes.clear()
            self.vista.canvasEstadisticas.axes.stem(etiquetas, promedios, linefmt='b-', markerfmt='bo', basefmt='r-')
            self.vista.canvasEstadisticas.axes.set_title('Promedio')
            self.vista.canvasEstadisticas.axes.set_xlabel('Canales' if eje == 'canales' else 'Tiempo')
            self.vista.canvasEstadisticas.axes.set_ylabel('Promedio')
            self.vista.canvasEstadisticas.axes.grid(True, alpha=0.3)
            self.vista.canvasEstadisticas.draw()

            if hasattr(self.vista, 'lblDesviacion'):
                texto = "Desviaciones:\n"
                for i, (etiq, desv) in enumerate(zip(etiquetas, desviaciones)):
                    if i < 10:
                        texto += f"{etiq}: {desv:.4f}\n"
                self.vista.lblDesviacion.setText(texto)

    def _cambiar_eje(self):
        self.calcular_estadisticas()

    def _cambiar_canal(self):
        self.graficar_senal()

    def _actualizar_segmento(self):
        self.graficar_senal()