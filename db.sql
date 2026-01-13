-- phpMyAdmin SQL Dump
-- version 5.1.1deb5ubuntu1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 12-01-2026 a las 23:33:19
-- Versión del servidor: 5.7.42
-- Versión de PHP: 8.1.2-1ubuntu2.22

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- --------------------------------------------------------
-- Creación de la base de datos
-- --------------------------------------------------------
CREATE DATABASE IF NOT EXISTS `ybook` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `ybook`;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `clientes`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `clientes` (
  `id_cliente` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `notas` text,
  `empleado` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `datos_configuracion`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `datos_configuracion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_config` varchar(100) NOT NULL,
  `valor` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre_config` (`nombre_config`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Insertar configuración inicial (solo esto se inserta)
-- --------------------------------------------------------
INSERT INTO `datos_configuracion` (`id`, `nombre_config`, `valor`) VALUES
(1, 'clave_admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'),
(2, 'correo_backup_destino', 'notificaciones.yalejo@gmail.com');

-- --------------------------------------------------------
-- Estructura de tabla para la tabla `transacciones`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `transacciones` (
  `id_transaccion` int(11) NOT NULL AUTO_INCREMENT,
  `fecha_creacion` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tipo_transaccion` enum('DEUDA','INGRESO') NOT NULL,
  `subtipo_transaccion` enum('FIADO','PRESTAMO','NEQUI_PENDIENTE','PAGO_DEUDA','NEQUI_RECIBIDO','OTROS_INGRESOS') NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `id_cliente` int(11) DEFAULT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `referencia_original` int(11) DEFAULT NULL,
  `saldo_afectado` decimal(10,2) NOT NULL,
  `estado_deuda` enum('PENDIENTE','PAGADA','CANCELADA') DEFAULT 'PENDIENTE',
  `id_empleado` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_transaccion`),
  KEY `id_cliente` (`id_cliente`),
  KEY `referencia_original` (`referencia_original`),
  CONSTRAINT `transacciones_ibfk_1` FOREIGN KEY (`id_cliente`) REFERENCES `clientes` (`id_cliente`) ON DELETE CASCADE,
  CONSTRAINT `transacciones_ibfk_2` FOREIGN KEY (`referencia_original`) REFERENCES `transacciones` (`id_transaccion`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Restablecer AUTO_INCREMENT para las tablas
-- --------------------------------------------------------
ALTER TABLE `clientes` AUTO_INCREMENT = 1;
ALTER TABLE `datos_configuracion` AUTO_INCREMENT = 3;
ALTER TABLE `transacciones` AUTO_INCREMENT = 1;

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;