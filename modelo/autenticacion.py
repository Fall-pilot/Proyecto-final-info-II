import os
import xml.etree.ElementTree as ET

class ModeloAutenticacion:
    def __init__(self, ruta_xml="usuarios.xml"):
        self.ruta_xml = ruta_xml
        self.usuarios = []
        self._cargar_usuarios()
    
    def _cargar_usuarios(self):
        if not os.path.exists(self.ruta_xml):
            print(f"ERROR: Archivo XML no encontrado: {self.ruta_xml}")
            print("El sistema no puede funcionar sin el archivo de usuarios.")
            self.usuarios = []
            return
        
        try:
            tree = ET.parse(self.ruta_xml)
            root = tree.getroot()
            
            for u in root.findall("usuario"):
                usuario_data = {
                    "id": u.find("id").text if u.find("id") is not None else "",
                    "nombre": u.find("nombre").text if u.find("nombre") is not None else "",
                    "correo": u.find("correo").text if u.find("correo") is not None else "",
                    "telefono": u.find("telefono").text if u.find("telefono") is not None else "",
                    "username": u.find("username").text if u.find("username") is not None else "",
                    "password": u.find("password").text if u.find("password") is not None else "",
                    "rol": u.find("rol").text if u.find("rol") is not None else "Usuario"
                }
                self.usuarios.append(usuario_data)
            
            if len(self.usuarios) == 0:
                print(f"ADVERTENCIA: El archivo XML {self.ruta_xml} está vacío")
            else:
                print(f"Cargados {len(self.usuarios)} usuarios desde {self.ruta_xml}")
                
        except ET.ParseError as e:
            print(f"ERROR: El archivo XML tiene errores de sintaxis: {e}")
            self.usuarios = []
        except Exception as e:
            print(f"ERROR inesperado cargando XML: {e}")
            self.usuarios = []
    
    def validar_usuario(self, username, password):
        if len(self.usuarios) == 0:
            print("No hay usuarios cargados. Verifique el archivo XML.")
            return False, None
        
        username = username.strip()
        password = password.strip()
        
        for user in self.usuarios:
            if user["username"] == username and user["password"] == password:
                return True, user.copy()
        
        return False, None
    
    def obtener_usuario_por_username(self, username):
        for user in self.usuarios:
            if user["username"] == username:
                return user.copy()
        return None
    
    def obtener_rol(self, username):
        user = self.obtener_usuario_por_username(username)
        return user["rol"] if user else None
        
    def obtener_todos_usuarios(self):
        return self.usuarios.copy() if self.usuarios else []
    
    def hay_usuarios(self):
        return len(self.usuarios) > 0
