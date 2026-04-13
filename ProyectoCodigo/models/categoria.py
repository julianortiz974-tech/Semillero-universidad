# models/categoria.py
from config.db_conexion import ConexionDB

class Categoria:
    @staticmethod
    def obtener_todas():
        """Lee todas las categorías (READ)"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        try:
            cursor.execute("SELECT id_categoria, nombre_categoria FROM categorias ORDER BY nombre_categoria ASC")
            return cursor.fetchall() 
        except Exception as e:
            print(f"Error al obtener categorías: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def insertar(nombre):
        """Crea una nueva categoría (CREATE)"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        try:
            sql = "INSERT INTO categorias (nombre_categoria) VALUES (%s)"
            cursor.execute(sql, (nombre,))
            db.commit()
            return True, "✅ Categoría añadida correctamente"
        except Exception as e:
            return False, f"❌ Error al insertar: {str(e)}"
        finally:
            cursor.close()

    @staticmethod
    def eliminar(id_categoria):
        """Elimina una categoría (DELETE)"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        try:
            # Nota: MySQL dará error si intentas borrar una categoría que tiene productos
            sql = "DELETE FROM categorias WHERE id_categoria = %s"
            cursor.execute(sql, (id_categoria,))
            db.commit()
            return True, "✅ Categoría eliminada de la base de datos"
        except Exception as e:
            return False, f"❌ No se puede eliminar: Tiene productos asociados."
        finally:
            cursor.close()
    
    @staticmethod
    def contar_productos(id_categoria):
        """Cuenta cuántos productos están amarrados a esta categoría"""
        db = ConexionDB()
        cursor = db.obtener_cursor()
        try:
            sql = "SELECT COUNT(*) as total FROM productos WHERE id_categoria = %s AND estado = 1"
            cursor.execute(sql, (id_categoria,))
            resultado = cursor.fetchone()
            return resultado['total'] if resultado else 0
        except:
            return 0
        finally:
            cursor.close()