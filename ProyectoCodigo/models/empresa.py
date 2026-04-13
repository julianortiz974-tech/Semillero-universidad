from config.db_conexion import ConexionDB

class Empresa:
    @staticmethod
    def obtener_datos():
        db = ConexionDB()
        cursor = db.obtener_cursor()
        cursor.execute("SELECT * FROM empresa WHERE id = 1")
        return cursor.fetchone()

    @staticmethod
    def actualizar(nombre, nit, direccion, telefono, correo, logo):
        db = ConexionDB()
        cursor = db.obtener_cursor()
        sql = """UPDATE empresa SET nombre=%s, nit=%s, direccion=%s, 
                 telefono=%s, correo=%s, ruta_logo=%s WHERE id=1"""
        cursor.execute(sql, (nombre, nit, direccion, telefono, correo, logo))
        db.conexion.commit()
        return True