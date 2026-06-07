from pymongo import MongoClient
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.uri = "mongodb+srv://msjs8933_db_user:C30PXM0gjBKbASzb@cluster0.hy12ifc.mongodb.net/?appName=Cluster0"
        self.db_name = "Biomodal_MSJS"
        self.client = None
        self.db = None
        self.conectado = False
        self._conectar()
    
    def _conectar(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.conectado = True
            print("Conectado a MongoDB exitosamente")
        except Exception as e:
            print(f"No se pudo conectar a MongoDB: {e}")
            print("El historial no se guardará, pero la aplicación funcionará.")
            self.db = None
            self.conectado = False
    
    def crear_sesion(self, usuario):
        """
        Crea un registro único de sesión cuando el usuario hace login
        Devuelve el _id del registro, o None si no hay conexión
        """
        if not self.conectado or self.db is None:
            print("Sin conexión a MongoDB - No se creó sesión")
            return None
        
        sesion = {
            "usuario": usuario,
            "fecha_hora_login": datetime.now(),
            "acciones": [],
            "ruta_resultados": "Resultados",
            "foto_usuario": None,
            "fecha_foto": None
        }
        
        try:
            result = self.db["sesiones"].insert_one(sesion)
            print(f"Sesión creada con ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"Error creando sesión: {e}")
            return None