-- Backup generado por SmartKardex
-- Fecha: 2026-04-29 17:08:00
-- -----------------------------------------------

SET FOREIGN_KEY_CHECKS=0;

-- ── Tabla: categorias ──
DROP TABLE IF EXISTS `categorias`;
CREATE TABLE `categorias` (
  `id_categoria` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_categoria` varchar(100) NOT NULL,
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `categorias` VALUES (2, 'Papelería');
INSERT INTO `categorias` VALUES (3, 'Herramientas');
INSERT INTO `categorias` VALUES (4, 'Insumos de Limpieza');
INSERT INTO `categorias` VALUES (6, 'Electronica');

-- ── Tabla: configuracion_sistema ──
DROP TABLE IF EXISTS `configuracion_sistema`;
CREATE TABLE `configuracion_sistema` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_organizacion` varchar(150) NOT NULL,
  `pais` varchar(100) DEFAULT NULL,
  `codigo_area` varchar(10) DEFAULT NULL,
  `moneda` varchar(50) DEFAULT NULL,
  `simbolo_moneda` varchar(10) DEFAULT NULL,
  `logo_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `configuracion_sistema` VALUES (1, 'smartsales', 'colombia', '804534-1', '3172601785', 'julianorti', 'C:/Users/julia/OneDrive/Imágenes/logoEmpresa.jpg');

-- ── Tabla: movimientos_inventario ──
DROP TABLE IF EXISTS `movimientos_inventario`;
CREATE TABLE `movimientos_inventario` (
  `id_movimiento` int(11) NOT NULL AUTO_INCREMENT,
  `id_producto` int(11) NOT NULL,
  `tipo_movimiento` enum('ENTRADA','SALIDA') NOT NULL,
  `cantidad` int(11) NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  `id_proveedor` int(11) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_movimiento`),
  KEY `id_producto` (`id_producto`),
  KEY `id_proveedor` (`id_proveedor`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `movimientos_inventario_ibfk_1` FOREIGN KEY (`id_producto`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE,
  CONSTRAINT `movimientos_inventario_ibfk_2` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedores` (`id_proveedor`) ON DELETE SET NULL,
  CONSTRAINT `movimientos_inventario_ibfk_3` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `movimientos_inventario` VALUES (4, 4, 'ENTRADA', 1, 'pruebas', '2026-04-25 21:06:54', NULL, 1);
INSERT INTO `movimientos_inventario` VALUES (5, 4, 'SALIDA', 8, 'prueba', '2026-04-25 21:07:20', NULL, 1);
INSERT INTO `movimientos_inventario` VALUES (6, 4, 'ENTRADA', 15, 'entrega de proveedor', '2026-04-28 18:32:54', NULL, 1);
INSERT INTO `movimientos_inventario` VALUES (7, 4, 'SALIDA', 12, 'venta', '2026-04-28 18:34:01', NULL, 1);
INSERT INTO `movimientos_inventario` VALUES (9, 10, 'ENTRADA', 6, 'prueba n 3', '2026-04-29 16:54:34', NULL, 1);

-- ── Tabla: productos ──
DROP TABLE IF EXISTS `productos`;
CREATE TABLE `productos` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `costo` decimal(10,2) DEFAULT 0.00,
  `unidad` varchar(20) DEFAULT 'Und',
  `stock` int(11) DEFAULT 0,
  `stock_minimo` int(11) DEFAULT 5,
  `imagen_path` varchar(255) DEFAULT NULL,
  `id_categoria` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_producto`),
  KEY `id_categoria` (`id_categoria`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `productos` VALUES (2, 'Teclado Mecánico RGB', '', '0.00', 'Und', 0, 5, '', 6);
INSERT INTO `productos` VALUES (3, 'Resma de Papel Carta', 'Papel bond 75g de alta blancura', '0.00', 'Und', 0, 20, NULL, 2);
INSERT INTO `productos` VALUES (4, 'Taladro Percutor 1/2', '', '0.00', 'Und', 10, 3, NULL, 3);
INSERT INTO `productos` VALUES (10, 'celular iphon', '', '130000.00', 'Caja', 6, 2, 'c:\\Users\\julia\\Documents\\Sena\\ProyectoCodigo1\\ProyectoCodigo\\assets\\productos\\demon-slayer-corps-kimetsu-no-yaiba-thumb.jpg', 6);

-- ── Tabla: proveedores ──
DROP TABLE IF EXISTS `proveedores`;
CREATE TABLE `proveedores` (
  `id_proveedor` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_empresa` varchar(150) NOT NULL,
  `nombre_contacto` varchar(150) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_proveedor`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `proveedores` VALUES (1, 'Distribuidora Tech S.A.', 'Juan Pérez', '3101234567', 'ventas@techsa.com');
INSERT INTO `proveedores` VALUES (2, 'Papeles del Sur', 'Marta Gómez', '6017654321', 'marta.gomez@papelessur.co');
INSERT INTO `proveedores` VALUES (3, 'Ferretería Central', 'Carlos Ruiz', '3159876543', 'contacto@ferrecentral.com');

-- ── Tabla: usuarios ──
DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol` enum('ADMIN','CAJERO') DEFAULT 'CAJERO',
  `estado` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `usuarios` VALUES (1, 'Administrador del Sistema', 'admin', '12345', 'ADMIN', 0);
INSERT INTO `usuarios` VALUES (2, 'Julian administrador', 'julian', 'ce0fee7e61f9c74f1110f0e5940a80b4f059f189217d0c3d26bb41960d4bf597', 'ADMIN', 1);
INSERT INTO `usuarios` VALUES (3, 'Cajero', 'empleado', 'admin123', 'CAJERO', 1);
INSERT INTO `usuarios` VALUES (4, 'Adrian Admin', 'adrian', '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5', 'ADMIN', 0);

SET FOREIGN_KEY_CHECKS=1;
