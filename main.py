import sys
import os

from PyQt5.QtWidgets import QApplication

def verificar_archivos_necesarios():
    archivos = ["usuarios.xml"]
    faltantes = []
    
    for archivo in archivos:
        if not os.path.exists(archivo):
            faltantes.append(archivo)
    
    return faltantes


def main():
    faltantes = verificar_archivos_necesarios()
    if faltantes:
        print("ADVERTENCIA: Faltan los siguientes archivos:")
        for archivo in faltantes:
            print(f"  - {archivo}")
        print("Ejecute 'python -m modelo.xml_manager' para crear el archivo de usuarios.")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Biomodal MSJS")
    app.setApplicationVersion("1.0")
    
    from vista.vista_login import VistaLogin
    from controlador.ctrl_login import ControladorLogin
    
    vista_login = VistaLogin()
    controlador_login = ControladorLogin(vista_login) #Ya se que sale advertencia pero no borren esta linea, es importante.
    vista_login.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()