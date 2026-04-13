from config.db_conexion import ConexionDB

class Cliente:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los clientes activos (estado = 1)"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        # Traemos todos los campos excepto la fecha y el estado para la tabla
        sql = """SELECT id_cliente, nombre, documento, telefono, correo, direccion 
                 FROM clientes WHERE estado = 1"""
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    def agregar(nombre, documento, telefono, correo, direccion):
        """Registra un nuevo cliente en la base de datos"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        sql = """INSERT INTO clientes (nombre, documento, telefono, correo, direccion) 
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (nombre, documento, telefono, correo, direccion))
        db.conexion.commit()
        return True

    @staticmethod
    def actualizar(id_cliente, nombre, documento, telefono, correo, direccion):
        """Actualiza los datos de un cliente existente"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        sql = """UPDATE clientes SET nombre=%s, documento=%s, telefono=%s, 
                 correo=%s, direccion=%s WHERE id_cliente=%s"""
        cursor.execute(sql, (nombre, documento, telefono, correo, direccion, id_cliente))
        db.conexion.commit()
        return True

    @staticmethod
    def eliminar(id_cliente):
        """Eliminación lógica: cambia el estado a 0 en lugar de borrarlo físicamente"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        sql = "UPDATE clientes SET estado = 0 WHERE id_cliente = %s"
        cursor.execute(sql, (id_cliente,))
        db.conexion.commit()
        return True
    
    @staticmethod
    def buscar_por_documento(documento):
        """Busca un cliente específico (útil para el futuro módulo de ventas)"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        sql = "SELECT * FROM clientes WHERE documento = %s AND estado = 1"
        cursor.execute(sql, (documento,))
        return cursor.fetchone()