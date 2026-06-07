import xml.etree.ElementTree as ET
import os

def generar_xml_usuarios(ruta="usuarios.xml"):
    if os.path.exists(ruta):
        print(f"ADVERTENCIA: El archivo {ruta} ya existe.")
        respuesta = input("Desea sobrescribirlo? (s/n): ")
        if respuesta.lower() != 's':
            print("Operacion cancelada.")
            return
    
    root = ET.Element("usuarios")
    tree = ET.ElementTree(root)
    tree.write(ruta, encoding="utf-8", xml_declaration=True)
    
    print(f"Archivo XML base creado en: {ruta}")
    print("El archivo esta vacio. Debe agregar los usuarios manualmente.")
    print("")
    print("Estructura esperada para cada usuario:")
    print('''
    <usuario>
        <id>001</id>
        <nombre>Nombre Completo</nombre>
        <correo>email@udea.edu.co</correo>
        <telefono>1234567890</telefono>
        <username>usuario</username>
        <password>contraseña</password>
        <rol>Usuario</rol>
    </usuario>
    ''')


def agregar_usuario_a_xml(ruta, id_usuario, nombre, correo, telefono, username, password, rol="Usuario"):
    if not os.path.exists(ruta):
        print(f"Error: El archivo {ruta} no existe. Ejecute primero generar_xml_usuarios()")
        return False
    
    try:
        tree = ET.parse(ruta)
        root = tree.getroot()
        
        usuario = ET.SubElement(root, "usuario")
        ET.SubElement(usuario, "id").text = id_usuario
        ET.SubElement(usuario, "nombre").text = nombre
        ET.SubElement(usuario, "correo").text = correo
        ET.SubElement(usuario, "telefono").text = telefono
        ET.SubElement(usuario, "username").text = username
        ET.SubElement(usuario, "password").text = password
        ET.SubElement(usuario, "rol").text = rol
        
        tree.write(ruta, encoding="utf-8", xml_declaration=True)
        print(f"Usuario {username} agregado correctamente.")
        return True
        
    except Exception as e:
        print(f"Error agregando usuario: {e}")
        return False


def obtener_todos_usuarios(ruta="usuarios.xml"):
    if not os.path.exists(ruta):
        print(f"ERROR: El archivo {ruta} no existe.")
        return []
    
    usuarios = []
    try:
        tree = ET.parse(ruta)
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
            usuarios.append(usuario_data)
        return usuarios
    except Exception as e:
        print(f"ERROR leyendo XML: {e}")
        return []


if __name__ == "__main__":
    print("GESTOR DE XML DE USUARIOS")
    print("")
    print("Opciones:")
    print("1. Crear archivo XML base (vacio)")
    print("2. Agregar un usuario al XML existente")
    print("3. Ver todos los usuarios")
    print("")
    
    opcion = input("Seleccione una opcion (1, 2 o 3): ")
    
    if opcion == "1":
        generar_xml_usuarios()
    elif opcion == "2":
        ruta = input("Ruta del archivo XML (Enter para usuarios.xml): ")
        if not ruta:
            ruta = "usuarios.xml"
        
        print("\nIngrese los datos del usuario:")
        id_usuario = input("ID: ")
        nombre = input("Nombre completo: ")
        correo = input("Correo: ")
        telefono = input("Telefono: ")
        username = input("Username: ")
        password = input("Password: ")
        rol = input("Rol (Usuario/Administrador): ")
        
        if not rol:
            rol = "Usuario"
        
        agregar_usuario_a_xml(ruta, id_usuario, nombre, correo, telefono, username, password, rol)
    elif opcion == "3":
        ruta = input("Ruta del archivo XML (Enter para usuarios.xml): ")
        if not ruta:
            ruta = "usuarios.xml"
        usuarios = obtener_todos_usuarios(ruta)
        if usuarios:
            print("\nUsuarios registrados:")
            print("-" * 40)
            for u in usuarios:
                print(f"ID: {u['id']} | Username: {u['username']} | Rol: {u['rol']}")
        else:
            print("No hay usuarios registrados.")
    else:
        print("Opcion no valida")