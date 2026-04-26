import mysql.connector
from mysql.connector import Error
import mysql.connector.locales.eng.client_error  # <--- AÑADE ESTA LÍNEA MÁGICA

class ConexionDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conexion = None
            cls._instance._inicializar_conexion()
        return cls._instance
    
    def _inicializar_conexion(self):
        """Crea la conexión si no existe o si se ha perdido."""
        try:
            if self.conexion is None or not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="sistema_kardex_sena",
                    port=3306
                )
                if self.conexion.is_connected():
                    print("✅ Conexión establecida")
        except Error as e:
            print(f"❌ Error al conectar: {e}")
            self.conexion = None
    
    def obtener_cursor(self):
        """Retorna un cursor que devuelve diccionarios para facilitar el trabajo."""
        self._inicializar_conexion() # Verifica que la conexión siga viva
        if self.conexion and self.conexion.is_connected():
            # 'dictionary=True' hace que los resultados sean mucho más fáciles de leer
            return self.conexion.cursor(dictionary=True)
        return None
    
    def commit(self):
        if self.conexion and self.conexion.is_connected():
            self.conexion.commit()
    
    def cerrar(self):
        """Cierra la conexión global (usar solo al salir de la app)."""
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("✅ Conexión cerrada globalmente")