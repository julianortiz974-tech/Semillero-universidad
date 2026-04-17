# models/usuario.py
from config.db_conexion import ConexionDB

class UsuarioModel:
    @staticmethod
    def validar_usuario(username, password):
        db = ConexionDB()
        cursor = db.obtener_cursor() # <-- Usamos tu método
        
        if cursor is None:
            return None

        sql = """
            SELECT id_usuario, nombre, rol 
            FROM usuarios 
            WHERE username = %s AND password = %s AND estado = 1
        """
        try:
            cursor.execute(sql, (username, password))
            usuario = cursor.fetchone() # Ahora esto es un diccionario {}
            cursor.close() # Cerramos solo el cursor, no la conexión global
            return usuario
        except Exception as e:
            print(f"Error en login: {e}")
            return None