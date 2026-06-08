import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem
from modelo import ModeloTabular


class ControladorCSV:
    def __init__(self, vista, db_manager=None, id_sesion=None):
        self.vista = vista
        self.modelo = ModeloTabular()
        self.db_manager = db_manager
        self.id_sesion = id_sesion
        self.graficas_actuales = []
        self._conectar_eventos()

    def _conectar_eventos(self):
        if hasattr(self.vista, 'btnCargarArchivo'):
            self.vista.btnCargarArchivo.clicked.connect(self.cargar_archivo)
        if hasattr(self.vista, 'btnGraficar'):
            self.vista.btnGraficar.clicked.connect(self.graficar_columnas)
        if hasattr(self.vista, 'btnScatter'):
            self.vista.btnScatter.clicked.connect(self.graficar_scatter)
        if hasattr(self.vista, 'btnLimpiar'):
            self.vista.btnLimpiar.clicked.connect(self.limpiar_graficas)
        if hasattr(self.vista, 'btnVolver'):
            self.vista.btnVolver.clicked.connect(self.vista.close)
        if hasattr(self.vista, 'listColumnas'):
            self.vista.listColumnas.itemSelectionChanged.connect(self._actualizar_seleccion)
        if hasattr(self.vista, 'cbEjeX'):
            self.vista.cbEjeX.currentTextChanged.connect(self._actualizar_scatter)
        if hasattr(self.vista, 'cbEjeY'):
            self.vista.cbEjeY.currentTextChanged.connect(self._actualizar_scatter)

    def cargar_archivo(self):
        ruta = QFileDialog.getOpenFileName(
            self.vista,
            "Cargar archivo",
            "",
            "CSV files (*.csv);;Excel files (*.xlsx *.xls)"
        )[0]

        if not ruta:
            return

        try:
            self.modelo.cargar_archivo(ruta)
            columnas = self.modelo.obtener_columnas()
            if hasattr(self.vista, 'listColumnas'):
                self.vista.listColumnas.clear()
                self.vista.listColumnas.addItems(columnas)
            if hasattr(self.vista, 'cbEjeX'):
                self.vista.cbEjeX.clear()
                self.vista.cbEjeX.addItems(columnas)
            if hasattr(self.vista, 'cbEjeY'):
                self.vista.cbEjeY.clear()
                self.vista.cbEjeY.addItems(columnas)
            self._mostrar_info()
            self._mostrar_describe()
            self._mostrar_resumen()

            QMessageBox.information(self.vista, "Exito", "Archivo cargado")

            if self.db_manager and self.id_sesion:
                self.db_manager.agregar_accion(self.id_sesion, f"Cargó archivo: {ruta}")

        except Exception as e:
            QMessageBox.critical(self.vista, "Error", str(e))

    def _mostrar_info(self):
        info_df = self.modelo.obtener_info()
        if info_df is not None and hasattr(self.vista, 'tablaInfo'):
            self.vista.tablaInfo.setRowCount(len(info_df))
            self.vista.tablaInfo.setColumnCount(len(info_df.columns))
            self.vista.tablaInfo.setHorizontalHeaderLabels(info_df.columns)

            for i, row in info_df.iterrows():
                for j, col in enumerate(info_df.columns):
                    self.vista.tablaInfo.setItem(i, j, QTableWidgetItem(str(row[col])))

            self.vista.tablaInfo.resizeColumnsToContents()

    def _mostrar_describe(self):
        describe_df = self.modelo.obtener_describe()
        if describe_df is not None and hasattr(self.vista, 'tablaDescribe'):
            self.vista.tablaDescribe.setRowCount(len(describe_df))
            self.vista.tablaDescribe.setColumnCount(len(describe_df.columns))
            self.vista.tablaDescribe.setHorizontalHeaderLabels(describe_df.columns)

            for i, row in describe_df.iterrows():
                for j, col in enumerate(describe_df.columns):
                    self.vista.tablaDescribe.setItem(i, j, QTableWidgetItem(str(row[col])))

            self.vista.tablaDescribe.resizeColumnsToContents()

    def _mostrar_resumen(self):
        resumen = self.modelo.obtener_resumen()
        if resumen and hasattr(self.vista, 'lblResumen'):
            texto = f"Filas: {resumen['filas']} | Columnas: {resumen['columnas']} | Nulos: {resumen['valores_nulos_totales']}"
            self.vista.lblResumen.setText(texto)

    def graficar_columnas(self):
        if self.modelo.df is None:
            QMessageBox.warning(self.vista, "Advertencia", "Cargue un archivo primero")
            return

        columnas_seleccionadas = []
        if hasattr(self.vista, 'listColumnas'):
            columnas_seleccionadas = [item.text() for item in self.vista.listColumnas.selectedItems()]

        if not columnas_seleccionadas:
            QMessageBox.warning(self.vista, "Advertencia", "Seleccione al menos una columna")
            return

        if len(columnas_seleccionadas) > 4:
            columnas_seleccionadas = columnas_seleccionadas[:4]
            QMessageBox.information(self.vista, "Info", "Solo se graficaran las primeras 4 columnas")

        n = len(columnas_seleccionadas)
        fig, axes = plt.subplots(n, 1, figsize=(8, 3*n))
        if n == 1:
            axes = [axes]

        for i, col in enumerate(columnas_seleccionadas):
            datos = self.modelo.obtener_datos_columna(col)
            if datos is not None:
                axes[i].plot(datos.values, 'o-', markersize=3, linewidth=1)
                axes[i].set_title(f'{col}')
                axes[i].set_xlabel('Indice')
                axes[i].set_ylabel('Valor')
                axes[i].grid(True, alpha=0.3)

        plt.tight_layout()

        self._mostrar_en_canvas(fig, 'canvasGraficas')

        if self.db_manager and self.id_sesion:
            self.db_manager.agregar_accion(self.id_sesion, f"Grafico columnas: {columnas_seleccionadas}")

    def graficar_scatter(self):
        if self.modelo.df is None:
            QMessageBox.warning(self.vista, "Advertencia", "Cargue un archivo primero")
            return

        col_x = ''
        col_y = ''

        if hasattr(self.vista, 'cbEjeX'):
            col_x = self.vista.cbEjeX.currentText()
        if hasattr(self.vista, 'cbEjeY'):
            col_y = self.vista.cbEjeY.currentText()

        if not col_x or not col_y:
            QMessageBox.warning(self.vista, "Advertencia", "Seleccione dos columnas")
            return

        datos_x, datos_y = self.modelo.obtener_datos_scatter(col_x, col_y)

        if datos_x is not None and datos_y is not None:
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.scatter(datos_x, datos_y, alpha=0.6, s=30)
            ax.set_xlabel(col_x)
            ax.set_ylabel(col_y)
            ax.set_title(f'Scatter: {col_x} vs {col_y}')
            ax.grid(True, alpha=0.3)

            self._mostrar_en_canvas(fig, 'canvasScatter')

            if self.db_manager and self.id_sesion:
                self.db_manager.agregar_accion(self.id_sesion, f"Scatter: {col_x} vs {col_y}")

    def _mostrar_en_canvas(self, figura, nombre_canvas):
        if hasattr(self.vista, nombre_canvas):
            canvas = getattr(self.vista, nombre_canvas)
            # Limpiar canvas anterior
            for i in reversed(range(canvas.layout().count())):
                widget = canvas.layout().itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

            nuevo_canvas = FigureCanvas(figura)
            canvas.layout().addWidget(nuevo_canvas)
            self.graficas_actuales.append(nuevo_canvas)

    def limpiar_graficas(self):
        for grafica in self.graficas_actuales:
            grafica.deleteLater()
        self.graficas_actuales.clear()

        if hasattr(self.vista, 'canvasGraficas'):
            for i in reversed(range(self.vista.canvasGraficas.layout().count())):
                widget = self.vista.canvasGraficas.layout().itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

        if hasattr(self.vista, 'canvasScatter'):
            for i in reversed(range(self.vista.canvasScatter.layout().count())):
                widget = self.vista.canvasScatter.layout().itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

    def _actualizar_seleccion(self): #me falta terminar esta sección
        pass

    def _actualizar_scatter(self):
        pass
