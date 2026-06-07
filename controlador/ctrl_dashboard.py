class ControladorDashboard:
    def __init__(self, vista, usuario, id_sesion, db_manager):
        self.vista = vista
        self.usuario = usuario
        self.id_sesion = id_sesion
        self.db_manager = db_manager
        self.vista.lblusuarioactivo.setText(f"Bienvenido, {usuario['nombre']}")
        self._conectar_botones()

    def _conectar_botones(self):
        self.vista.btnImagenes.clicked.connect(self.abrir_imagenes)
        self.vista.btnSenales.clicked.connect(self.abrir_senales)
        self.vista.btnCSV.clicked.connect(self.abrir_csv)
        self.vista.btnHistorial.clicked.connect(self.abrir_historial)
        self.vista.btnCerrarSesion.clicked.connect(self.cerrar_sesion)

    def abrir_imagenes(self):
        from .ctrl_imagenes import ControladorImagenes
        from vista.vista_imagenes import VistaImagenes

        self.vista_imagenes = VistaImagenes()
        self.controlador_imagenes = ControladorImagenes(
            self.vista_imagenes,
            db_manager=self.db_manager,
            id_sesion=self.id_sesion
        )
        self.vista_imagenes.show()
        self._registrar_accion("Abrio modulo Imagenes")

    def abrir_senales(self):
        from .ctrl_senales import ControladorSenales
        from vista.vista_senales import VistaSenales

        self.vista_senales = VistaSenales()
        self.controlador_senales = ControladorSenales(
            self.vista_senales,
            db_manager=self.db_manager,
            id_sesion=self.id_sesion
        )
        self.vista_senales.show()
        self._registrar_accion("Abrio modulo Senales")

    def abrir_csv(self):
        from .ctrl_csv import ControladorCSV
        from vista.vista_csv import VistaCSV

        self.vista_csv = VistaCSV()
        self.controlador_csv = ControladorCSV(
            self.vista_csv,
            db_manager=self.db_manager,
            id_sesion=self.id_sesion
        )
        self.vista_csv.show()
        self._registrar_accion("Abrio modulo CSV")

    def abrir_historial(self):
        from .ctrl_historial import ControladorHistorial
        from vista.vista_historial import VistaHistorial

        self.vista_historial = VistaHistorial()
        self.controlador_historial = ControladorHistorial(
            self.vista_historial,
            db_manager=self.db_manager,
            usuario=self.usuario
        )
        self.vista_historial.show()
        self._registrar_accion("Abrio Historial")

    def cerrar_sesion(self):
        self._registrar_accion("Cerro sesion")
        self.vista.close()

        from .ctrl_login import ControladorLogin
        from vista.vista_login import VistaLogin

        self.vista_login = VistaLogin()
        self.controlador_login = ControladorLogin(self.vista_login)
        self.vista_login.show()

    def _registrar_accion(self, accion):
        if self.db_manager and self.id_sesion:
            self.db_manager.agregar_accion(self.id_sesion, accion)