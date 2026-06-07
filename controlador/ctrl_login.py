from PyQt5.QtWidgets import QMessageBox
from modelo import ModeloAutenticacion, DatabaseManager


class ControladorLogin:
    def __init__(self, vista):
        self.vista = vista
        self.modelo_autenticacion = ModeloAutenticacion()
        self.db_manager = DatabaseManager()
        self._conectar_signales()

    def _conectar_signales(self):
        self.vista.btnIngresar.clicked.connect(self.login)
        self.vista.btnSalir.clicked.connect(self.vista.close)

    def login(self):
        username = self.vista.lnputUsuario.text()
        password = self.vista.InputContrasena.text()

        exito, usuario = self.modelo_autenticacion.validar_usuario(username, password)

        if exito:
            id_sesion = self.db_manager.crear_sesion(username)

            from .ctrl_dashboard import ControladorDashboard
            from vista.vista_dashboard import VistaDashboard

            self.vista_dashboard = VistaDashboard()
            self.controlador_dashboard = ControladorDashboard(
                self.vista_dashboard,
                usuario=usuario,
                id_sesion=id_sesion,
                db_manager=self.db_manager
            )
            self.vista_dashboard.show()
            self.vista.close()
        else:
            QMessageBox.warning(self.vista, "Error", "Usuario o contraseña incorrectos")