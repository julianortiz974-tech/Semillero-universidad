from config.db_conexion import ConexionDB

class Producto:
    def __init__(self, nombre, descripcion, precio, stock, id_categoria=1, id_producto=None):
        self.id_producto = id_producto
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock
        self.id_categoria = id_categoria
    
    def insertar(self):
        # ... (Tu código de insertar se mantiene igual)
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if not cursor: return False, "❌ Sin conexión"
        
        sql = """
            INSERT INTO productos (nombre, descripcion, precio, stock, id_categoria, estado)
            VALUES (%s, %s, %s, %s, %s, 1)
        """
        valores = (self.nombre, self.descripcion, self.precio, self.stock, self.id_categoria)
        
        try:
            cursor.execute(sql, valores)
            db.commit()
            return True, "✅ Producto insertado correctamente"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
        finally:
            cursor.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todos los productos activos"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if not cursor: return []
        
        try:
            cursor.execute("""
                SELECT p.id_producto, p.nombre, p.descripcion, p.precio, 
                       p.stock, c.nombre_categoria
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.estado = 1
                ORDER BY p.id_producto DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()

    # --- AQUÍ AÑADIMOS EL NUEVO MÉTODO ---
    @staticmethod
    def obtener_por_categoria(id_categoria):
        """Obtiene productos filtrados por una categoría específica"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if not cursor: return []
        
        try:
            sql = """
                SELECT p.id_producto, p.nombre, p.descripcion, p.precio, 
                       p.stock, c.nombre_categoria
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.id_categoria = %s AND p.estado = 1
                ORDER BY p.nombre ASC
            """
            cursor.execute(sql, (id_categoria,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al filtrar por categoría: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def obtener_por_id(id_producto):
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if not cursor: return None
        
        try:
            cursor.execute("""
                SELECT id_producto, nombre, descripcion, precio, stock, id_categoria
                FROM productos 
                WHERE id_producto = %s AND estado = 1
            """, (id_producto,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            cursor.close()
    
    def actualizar(self):
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if not cursor: return False, "❌ Sin conexión"
        
        sql = """
            UPDATE productos 
            SET nombre=%s, descripcion=%s, precio=%s, stock=%s, id_categoria=%s
            WHERE id_producto=%s
        """
        valores = (self.nombre, self.descripcion, self.precio, self.stock, 
                   self.id_categoria, self.id_producto)
        
        try:
            cursor.execute(sql, valores)
            db.commit()
            return True, "✅ Producto actualizado correctamente"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
        finally:
            cursor.close()
    
    @staticmethod
    def eliminar(id_producto):
        """Elimina permanentemente un producto de la base de datos"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if not cursor: return False, "❌ Sin conexión"
        
        try:
            # Usamos DELETE para borrar la fila física en MySQL
            sql = "DELETE FROM productos WHERE id_producto = %s"
            cursor.execute(sql, (id_producto,))
            
            db.commit()
            return True, "✅ Producto eliminado físicamente de la base de datos"
        except Exception as e:
            # Si el producto está amarrado a una venta, MySQL dará error de Llave Foránea
            return False, f"❌ No se puede eliminar: El producto tiene registros asociados (Error: {str(e)})"
        finally:
            cursor.close()