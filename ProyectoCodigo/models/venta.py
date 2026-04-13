from config.db_conexion import ConexionDB

class Venta:
    @staticmethod
    def registrar_venta(id_cliente, total, lista_productos):
        """
        Registra la cabecera de la venta, los detalles y descuenta el stock de inventario.
        'lista_productos' debe ser una lista de diccionarios con la info del carrito.
        """
        db = ConexionDB()
        cursor = db.obtener_cursor()

        try:
            # 1. Crear la Factura General (Tabla ventas)
            sql_venta = "INSERT INTO ventas (id_cliente, total) VALUES (%s, %s)"
            cursor.execute(sql_venta, (id_cliente, total))
            
            # Obtener el número de factura que MySQL acaba de generar
            id_venta = cursor.lastrowid
            
            # 2. Guardar los Detalles y Descontar Inventario
            for prod in lista_productos:
                # Insertar en detalle_ventas
                sql_detalle = """INSERT INTO detalle_venta 
                                 (id_venta, id_producto, cantidad, precio_unitario, subtotal) 
                                 VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql_detalle, (
                    id_venta, 
                    prod['id_producto'], 
                    prod['cantidad'], 
                    prod['precio_unitario'], 
                    prod['subtotal']
                ))
                
                # Descontar la cantidad vendida de la tabla productos
                sql_stock = "UPDATE productos SET stock = stock - %s WHERE id_producto = %s"
                cursor.execute(sql_stock, (prod['cantidad'], prod['id_producto']))
            
            # 3. Confirmar la transacción (GUARDAR TODO DEFINITIVAMENTE)
            db.conexion.commit()
            
            # Devolvemos el ID de la venta para poder generar el PDF de la factura
            return id_venta
            
        except Exception as e:
            # Si hay un error (ej. se va la luz o un producto no existe), cancelamos todo
            db.conexion.rollback()
            raise Exception(f"Error al procesar la venta en BD: {e}")