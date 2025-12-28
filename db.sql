CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    notas TEXT,
    empleado BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE transacciones (
    id_transaccion INT AUTO_INCREMENT PRIMARY KEY,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    tipo_transaccion ENUM('DEUDA', 'INGRESO') NOT NULL,
    
    subtipo_transaccion ENUM(
        'FIADO', 
        'PRESTAMO', 
        'NEQUI_PENDIENTE', 
        'PAGO_DEUDA', 
        'NEQUI_RECIBIDO', 
        'OTROS_INGRESOS'
    ) NOT NULL,
    
    monto DECIMAL(10, 2) NOT NULL,

    id_cliente INT,              -- Cliente afectado
    id_empleado INT NOT NULL,    -- ✅ NUEVO: Empleado que registra

    descripcion VARCHAR(255),
    referencia_original INT,
    saldo_afectado DECIMAL(10, 2) NOT NULL,

    estado_deuda ENUM('PENDIENTE', 'PAGADA', 'CANCELADA') DEFAULT 'PENDIENTE',

    -- Relaciones
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_empleado) REFERENCES clientes(id_cliente),
    FOREIGN KEY (referencia_original) REFERENCES transacciones(id_transaccion)
);

CREATE TABLE datos_configuracion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_config VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT NOT NULL
);

INSERT INTO `datos_configuracion` (`id`, `nombre_config`, `valor`) VALUES
(1, 'clave_admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');

INSERT INTO datos_configuracion (nombre_config, valor)
VALUES ('correo_backup_destino', 'notificaciones.yalejo@gmail.com');