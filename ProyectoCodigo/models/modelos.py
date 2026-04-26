import hashlib
from config.db_conexion import ConexionDB


def _hash(password: str) -> str:
    """SHA-256 para guardar contraseñas de forma segura."""
    return hashlib.sha256(password.strip().encode()).hexdigest()

# CLASE CATEGORÍA
class Categoria:
    @classmethod
    def obtener_todas(cls):
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if cursor:
            cursor.execute("SELECT * FROM categorias ORDER BY nombre_categoria ASC")
            return cursor.fetchall()
        return []

    @classmethod
    def insertar(cls, nombre):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                cursor.execute("INSERT INTO categorias (nombre_categoria) VALUES (%s)", (nombre,))
                db.commit()
                return True
        except Exception as e:
            print(f"Error al insertar categoría: {e}")
        return False

    @classmethod
    def actualizar(cls, id_categoria, nombre):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                cursor.execute("UPDATE categorias SET nombre_categoria = %s WHERE id_categoria = %s", (nombre, id_categoria))
                db.commit()
                return True
        except Exception as e:
            print(f"Error al actualizar categoría: {e}")
        return False

    @classmethod
    @classmethod
    def eliminar(cls, id_categoria):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                # --- 1. ESCUDO PROTECTOR (Verificación manual) ---
                # Le pedimos a MySQL que cuente cuántos productos usan esta categoría
                cursor.execute("SELECT COUNT(*) as total FROM productos WHERE id_categoria = %s", (id_categoria,))
                resultado = cursor.fetchone()
                
                # Si el total es mayor a 0, hay productos adentro. ¡Abortamos!
                if resultado and resultado['total'] > 0:
                    print("Operación bloqueada: La categoría tiene productos asignados.")
                    return False 
                # -------------------------------------------------

                # 2. Si pasa el escudo (total = 0), entonces sí la eliminamos
                cursor.execute("DELETE FROM categorias WHERE id_categoria = %s", (id_categoria,))
                db.commit()
                return True
                
        except Exception as e:
            print(f"Error al eliminar categoría: {e}")
            return False

# ==========================================
# CLASE PRODUCTO
# ==========================================
class Producto:
    def __init__(self, nombre, descripcion, costo, unidad, stock, stock_minimo,
                 imagen_path, id_categoria, id_producto=None):
        self.id_producto  = id_producto
        self.nombre       = nombre
        self.descripcion  = descripcion
        self.costo        = costo
        self.unidad       = unidad
        self.stock        = stock
        self.stock_minimo = stock_minimo
        self.imagen_path  = imagen_path
        self.id_categoria = id_categoria

    @classmethod
    def obtener_todos(cls):
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if cursor:
            sql = """
                SELECT p.id_producto, p.nombre, p.descripcion, p.costo, p.unidad,
                       p.stock, p.stock_minimo, p.imagen_path, c.nombre_categoria
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                ORDER BY p.nombre ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        return []

    @classmethod
    def obtener_por_categoria(cls, id_cat):
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if cursor:
            sql = """
                SELECT p.id_producto, p.nombre, p.descripcion, p.costo, p.unidad,
                       p.stock, p.stock_minimo, p.imagen_path, c.nombre_categoria
                FROM productos p
                LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
                WHERE p.id_categoria = %s
            """
            cursor.execute(sql, (id_cat,))
            return cursor.fetchall()
        return []

    def insertar(self):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                sql = """INSERT INTO productos
                         (nombre, descripcion, costo, unidad, stock, stock_minimo, imagen_path, id_categoria)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (self.nombre, self.descripcion, self.costo, self.unidad,
                                     self.stock, self.stock_minimo, self.imagen_path, self.id_categoria))
                db.commit()
                return True
        except Exception as e:
            print(f"Error al insertar producto: {e}")
        return False

    def actualizar(self):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                sql = """UPDATE productos SET
                         nombre=%s, descripcion=%s, costo=%s, unidad=%s,
                         stock=%s, stock_minimo=%s, imagen_path=%s, id_categoria=%s
                         WHERE id_producto=%s"""
                cursor.execute(sql, (self.nombre, self.descripcion, self.costo, self.unidad,
                                     self.stock, self.stock_minimo, self.imagen_path,
                                     self.id_categoria, self.id_producto))
                db.commit()
                return True
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
        return False

    @classmethod
    def eliminar(cls, id_producto):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
                db.commit()
                return True
        except Exception as e:
            print(f"Error al eliminar: {e}")
        return False


# ==========================================
# CLASE PROVEEDOR
# ==========================================
class Proveedor:
    def __init__(self, nombre_empresa, nombre_contacto, telefono, correo, id_proveedor=None):
        self.id_proveedor    = id_proveedor
        self.nombre_empresa  = nombre_empresa
        self.nombre_contacto = nombre_contacto
        self.telefono        = telefono
        self.correo          = correo

    @classmethod
    def obtener_todos(cls):
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if cursor:
            cursor.execute("SELECT * FROM proveedores ORDER BY nombre_empresa ASC")
            return cursor.fetchall()
        return []

    def insertar(self):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                sql = "INSERT INTO proveedores (nombre_empresa, nombre_contacto, telefono, correo) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (self.nombre_empresa, self.nombre_contacto,
                                     self.telefono, self.correo))
                db.commit()
                return True
        except Exception as e:
            print(f"Error al insertar proveedor: {e}")
        return False

    def actualizar(self, id_p):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                sql = "UPDATE proveedores SET nombre_empresa=%s, nombre_contacto=%s, telefono=%s, correo=%s WHERE id_proveedor=%s"
                cursor.execute(sql, (self.nombre_empresa, self.nombre_contacto,
                                     self.telefono, self.correo, id_p))
                db.commit()
                return True
        except Exception as e:
            print(f"Error al actualizar proveedor: {e}")
        return False

    @classmethod
    def eliminar(cls, id_p):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                cursor.execute("DELETE FROM proveedores WHERE id_proveedor = %s", (id_p,))
                db.commit()
                return True
        except Exception as e:
            print(f"Error al eliminar proveedor: {e}")
        return False


# ==========================================
# CLASE MOVIMIENTO
# ==========================================
class Movimiento:
    @classmethod
    def registrar(cls, id_producto, tipo, cantidad, motivo, id_usuario=1):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                sql_mov = """INSERT INTO movimientos_inventario
                             (id_producto, tipo_movimiento, cantidad, motivo, id_usuario)
                             VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql_mov, (id_producto, tipo, cantidad, motivo, id_usuario))
                if tipo == 'ENTRADA':
                    sql_stock = "UPDATE productos SET stock = stock + %s WHERE id_producto = %s"
                else:
                    sql_stock = "UPDATE productos SET stock = stock - %s WHERE id_producto = %s"
                cursor.execute(sql_stock, (cantidad, id_producto))
                db.commit()
                return True
            if tipo == 'SALIDA':
                cursor.execute("SELECT stock FROM productos WHERE id_producto=%s", (id_producto,))
                prod = cursor.fetchone()
                if not prod or prod['stock'] < cantidad:
                    print("Stock insuficiente")
                    return False

        except Exception as e:
            print(f"Error registrando movimiento: {e}")
        return False

    @classmethod
    def obtener_historial(cls):
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if cursor:
            sql = """SELECT m.id_movimiento,
                            DATE_FORMAT(m.fecha, '%d/%m/%Y %H:%i') as fecha_hora,
                            p.nombre as producto, m.tipo_movimiento, m.cantidad, m.motivo
                     FROM movimientos_inventario m
                     JOIN productos p ON m.id_producto = p.id_producto
                     ORDER BY m.fecha DESC"""
            cursor.execute(sql)
            return cursor.fetchall()
        return []


# ==========================================
# CLASE USUARIO  (con hashlib SHA-256)
# ==========================================
class Usuario:
    def __init__(self, username, nombre, rol, id_usuario=None):
        self.id_usuario = id_usuario
        self.username   = username
        self.nombre     = nombre
        self.rol        = rol

    # ── LOGIN ──────────────────────────────────────────────────────────────
    @classmethod
    def autenticar(cls, username, password):
        """
        Prueba primero con hash SHA-256.
        Si no coincide, intenta texto plano para compatibilidad con
        contraseñas creadas antes de agregar el cifrado.
        """
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if not cursor:
            return None

        # Intento 1: contraseña hasheada
        cursor.execute(
            "SELECT * FROM usuarios WHERE username=%s AND password=%s AND estado=1",
            (username, _hash(password))
        )
        usuario = cursor.fetchone()
        if usuario:
            return usuario

        # Intento 2: texto plano (compatibilidad con cuentas antiguas)
        cursor.execute(
            "SELECT * FROM usuarios WHERE username=%s AND password=%s AND estado=1",
            (username, password)
        )
        return cursor.fetchone()

    # ── CRUD ───────────────────────────────────────────────────────────────
    @classmethod
    def obtener_todos(cls):
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if cursor:
            cursor.execute(
                "SELECT id_usuario, nombre, username, rol, estado FROM usuarios ORDER BY nombre ASC"
            )
            return cursor.fetchall()
        return []

    @classmethod
    def insertar(cls, nombre, username, password, rol):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                cursor.execute("SELECT id_usuario FROM usuarios WHERE username=%s", (username,))
                if cursor.fetchone():
                    return False, f"El usuario '{username}' ya existe."
                sql = "INSERT INTO usuarios (nombre, username, password, rol, estado) VALUES (%s,%s,%s,%s,1)"
                cursor.execute(sql, (nombre, username, _hash(password), rol))
                db.commit()
                return True, "Usuario creado"
        except Exception as e:
            return False, str(e)
        return False, "Error desconocido"

    @classmethod
    def actualizar(cls, id_usuario, nombre, username, rol):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                cursor.execute(
                    "SELECT id_usuario FROM usuarios WHERE username=%s AND id_usuario!=%s",
                    (username, id_usuario)
                )
                if cursor.fetchone():
                    return False, f"El usuario '{username}' ya está en uso."
                cursor.execute(
                    "UPDATE usuarios SET nombre=%s, username=%s, rol=%s WHERE id_usuario=%s",
                    (nombre, username, rol, id_usuario)
                )
                db.commit()
                return True, "Actualizado"
        except Exception as e:
            return False, str(e)
        return False, "Error desconocido"

    @classmethod
    def cambiar_password(cls, id_usuario, nueva_password):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                cursor.execute(
                    "UPDATE usuarios SET password=%s WHERE id_usuario=%s",
                    (_hash(nueva_password), id_usuario)
                )
                db.commit()
                return True, "Contraseña actualizada"
        except Exception as e:
            return False, str(e)
        return False, "Error desconocido"

    @classmethod
    def cambiar_estado(cls, id_usuario, nuevo_estado):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                cursor.execute(
                    "UPDATE usuarios SET estado=%s WHERE id_usuario=%s",
                    (nuevo_estado, id_usuario)
                )
                db.commit()
                return True, "Estado actualizado"
        except Exception as e:
            return False, str(e)
        return False, "Error desconocido"

    @classmethod
    def cambiar_contraseña(cls, id_usuario, actual, nueva):
        """Verifica la contraseña actual antes de cambiarla (para perfil propio)."""
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                cursor.execute("SELECT password FROM usuarios WHERE id_usuario=%s", (id_usuario,))
                res = cursor.fetchone()
                if not res:
                    return False, "Usuario no encontrado"
                pwd_bd = res["password"]
                # Acepta hash o texto plano (compatibilidad)
                if pwd_bd != _hash(actual) and pwd_bd != actual:
                    return False, "La contraseña actual es incorrecta"
                cursor.execute(
                    "UPDATE usuarios SET password=%s WHERE id_usuario=%s",
                    (_hash(nueva), id_usuario)
                )
                db.commit()
                return True, "Contraseña actualizada"
        except Exception as e:
            return False, str(e)
        return False, "Error de conexión"


# ==========================================
# CLASE SISTEMA CONFIGURACIÓN
# ==========================================
class SistemaConfiguracion:
    def __init__(self, nombre_org, pais, codigo, moneda, simbolo, logo_path, id_config=None):
        self.id_config  = id_config
        self.nombre_org = nombre_org
        self.pais       = pais
        self.codigo     = codigo
        self.moneda     = moneda
        self.simbolo    = simbolo
        self.logo_path  = logo_path

    @classmethod
    def obtener(cls):
        db = ConexionDB()
        cursor = db.obtener_cursor()
        if cursor:
            cursor.execute("SELECT * FROM configuracion_sistema LIMIT 1")
            return cursor.fetchone()
        return None

    def actualizar(self):
        try:
            db = ConexionDB()
            cursor = db.obtener_cursor()
            if cursor:
                if self.id_config:
                    sql = """UPDATE configuracion_sistema SET
                             nombre_organizacion=%s, pais=%s, codigo_area=%s,
                             moneda=%s, simbolo_moneda=%s, logo_path=%s
                             WHERE id=%s"""
                    cursor.execute(sql, (self.nombre_org, self.pais, self.codigo,
                                         self.moneda, self.simbolo, self.logo_path, self.id_config))
                else:
                    sql = """INSERT INTO configuracion_sistema
                             (nombre_organizacion, pais, codigo_area, moneda, simbolo_moneda, logo_path)
                             VALUES (%s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (self.nombre_org, self.pais, self.codigo,
                                         self.moneda, self.simbolo, self.logo_path))
                db.commit()
                return True
        except Exception as e:
            print(f"Error al actualizar configuración: {e}")
        return False