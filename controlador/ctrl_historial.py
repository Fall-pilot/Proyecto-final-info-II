from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox


class ControladorHistorial:
    def __init__(self, vista, db_manager, usuario=None):
        self.vista = vista
        self.db_manager = db_manager
        self.usuario = usuario
        self._conectar_eventos()
        self.cargar_historial()

    def _conectar_eventos(self):
        if hasattr(self.vista, 'btnActualizar'):
            self.vista.btnActualizar.clicked.connect(self.cargar_historial)
        if hasattr(self.vista, 'btnEliminar'):
            self.vista.btnEliminar.clicked.connect(self.eliminar_sesion)
        if hasattr(self.vista, 'btnVolver'):
            self.vista.btnVolver.clicked.connect(self.vista.close)

    def cargar_historial(self):
        if not self.db_manager or not self.db_manager.conectado:
            QMessageBox.warning(self.vista, "Advertencia", "No hay conexion a MongoDB")
            return

        historial = self.db_manager.obtener_historial(self.usuario)

        if not hasattr(self.vista, 'tablaHistorial'):
            return

        self.vista.tablaHistorial.setRowCount(len(historial))
        self.vista.tablaHistorial.setColumnCount(6)
        self.vista.tablaHistorial.setHorizontalHeaderLabels(
            ["Usuario", "Fecha/Hora Login", "Acciones", "Tiene Foto", "Duracion", "ID"]
        )

        for i, sesion in enumerate(historial):
            item_usuario = QTableWidgetItem(str(sesion.get('usuario', '')))
            self.vista.tablaHistorial.setItem(i, 0, item_usuario)

            fecha_login = sesion.get('fecha_hora_login', '')
            item_fecha = QTableWidgetItem(str(fecha_login))
            self.vista.tablaHistorial.setItem(i, 1, item_fecha)

            num_acciones = len(sesion.get('acciones', []))
            item_acciones = QTableWidgetItem(str(num_acciones))
            self.vista.tablaHistorial.setItem(i, 2, item_acciones)

            tiene_foto = "Si" if sesion.get('foto_usuario') else "No"
            item_foto = QTableWidgetItem(tiene_foto)
            self.vista.tablaHistorial.setItem(i, 3, item_foto)

            duracion = f"{num_acciones} acciones"
            item_duracion = QTableWidgetItem(duracion)
            self.vista.tablaHistorial.setItem(i, 4, item_duracion)

            item_id = QTableWidgetItem(str(sesion.get('_id', '')))
            self.vista.tablaHistorial.setItem(i, 5, item_id)

        self.vista.tablaHistorial.resizeColumnsToContents()

    def eliminar_sesion(self):
        if not hasattr(self.vista, 'tablaHistorial'):
            return

        fila = self.vista.tablaHistorial.currentRow()
        if fila < 0:
            QMessageBox.warning(self.vista, "Advertencia", "Seleccione una sesion")
            return

        id_sesion = self.vista.tablaHistorial.item(fila, 5).text()

        confirmar = QMessageBox.question(
            self.vista,
            "Confirmar",
            "Desea eliminar esta sesion?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmar == QMessageBox.Yes:
            if self.db_manager.eliminar_sesion(id_sesion):
                QMessageBox.information(self.vista, "Exito", "Sesion eliminada")
                self.cargar_historial()
            else:
                QMessageBox.critical(self.vista, "Error", "No se pudo eliminar la sesion")