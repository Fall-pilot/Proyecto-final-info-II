from pymongo import MongoClient
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.uri = "mongodb://localhost:27017/"
        self.db_name = "ProyectoFinal_Inf2"
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
            print("Conectado a MongoDB Local en puerto 27017")
        except Exception as e:
            print(f"No se pudo conectar a MongoDB Local: {e}")
            print("El historial no se guardará, pero la aplicación funcionará.")
            print("Asegúrate de que MongoDB esté ejecutándose: 'mongod'")
            self.db = None
            self.conectado = False
    
    def crear_sesion(self, usuario):
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
    
    def agregar_accion(self, id_sesion, accion):
        if not self.conectado or self.db is None or id_sesion is None:
            return
        
        try:
            from bson import ObjectId
            self.db["sesiones"].update_one(
                {"_id": ObjectId(id_sesion)},
                {"$push": {"acciones": accion}}
            )
        except Exception as e:
            print(f"Error agregando acción: {e}")
    
    def guardar_foto_usuario(self, id_sesion, ruta_foto):
        if not self.conectado or self.db is None or id_sesion is None:
            return
        
        try:
            from bson import ObjectId
            self.db["sesiones"].update_one(
                {"_id": ObjectId(id_sesion)},
                {"$set": {
                    "foto_usuario": ruta_foto,
                    "fecha_foto": datetime.now()
                }}
            )
            print(f"Foto guardada en sesión: {ruta_foto}")
        except Exception as e:
            print(f"Error guardando foto: {e}")
    
    def obtener_historial(self, usuario=None):
        if not self.conectado or self.db is None:
            return []
        
        query = {}
        if usuario:
            query["usuario"] = usuario
        
        try:
            return list(self.db["sesiones"].find(query).sort("fecha_hora_login", -1))
        except Exception as e:
            print(f"Error obteniendo historial: {e}")
            return []
    
    def eliminar_sesion(self, id_sesion):
        """Elimina una sesión del historial"""
        if not self.conectado or self.db is None:
            return False
        
        try:
            from bson import ObjectId
            result = self.db["sesiones"].delete_one({"_id": ObjectId(id_sesion)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error eliminando sesión: {e}")
            return False