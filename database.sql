-- Crear base de datos
CREATE DATABASE sistema_asistencia_qr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sistema_asistencia_qr;

-- Tabla EMPRESAS
CREATE TABLE EMPRESAS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo_empresa VARCHAR(10) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla EMPLEADOS
CREATE TABLE EMPLEADOS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empresa_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    dni VARCHAR(20) UNIQUE,
    codigo_qr_unico VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (empresa_id) REFERENCES EMPRESAS(id) ON DELETE CASCADE,
    INDEX idx_empresa_id (empresa_id),
    INDEX idx_codigo_qr (codigo_qr_unico)
);

-- Tabla HORARIOS_ESTANDAR
CREATE TABLE HORARIOS_ESTANDAR (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empresa_id INT NOT NULL,
    entrada_manana TIME DEFAULT '06:50:00',
    salida_manana TIME DEFAULT '12:50:00',
    entrada_tarde TIME DEFAULT '14:50:00',
    salida_tarde TIME DEFAULT '18:50:00',
    FOREIGN KEY (empresa_id) REFERENCES EMPRESAS(id) ON DELETE CASCADE,
    UNIQUE KEY unique_empresa (empresa_id)
);

-- Tabla ASISTENCIA
CREATE TABLE ASISTENCIA (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empleado_id INT NOT NULL,
    fecha DATE NOT NULL,
    entrada_manana_real TIME,
    salida_manana_real TIME,
    entrada_tarde_real TIME,
    salida_tarde_real TIME,
    total_horas_trabajadas DECIMAL(5,2) DEFAULT 0.00,
    horas_normales DECIMAL(5,2) DEFAULT 8.00,
    horas_extras DECIMAL(5,2) DEFAULT 0.00,
    estado_dia ENUM('COMPLETO', 'INCOMPLETO', 'FALTA', 'RETARDO') DEFAULT 'INCOMPLETO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (empleado_id) REFERENCES EMPLEADOS(id) ON DELETE CASCADE,
    UNIQUE KEY unique_empleado_fecha (empleado_id, fecha),
    INDEX idx_fecha (fecha),
    INDEX idx_empleado_fecha (empleado_id, fecha)
);

-- Tabla ADMINISTRADORES
CREATE TABLE ADMINISTRADORES (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empresa_id INT NULL,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    rol ENUM('SUPER_ADMIN', 'ADMIN_EMPRESA') DEFAULT 'ADMIN_EMPRESA',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES EMPRESAS(id) ON DELETE SET NULL
);

-- Tabla CONFIG_ALERTAS
CREATE TABLE CONFIG_ALERTAS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empresa_id INT,
    numero_faltas_para_alerta INT DEFAULT 4,
    mensaje_correo_falta TEXT,
    mensaje_correo_admin TEXT,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (empresa_id) REFERENCES EMPRESAS(id) ON DELETE CASCADE,
    UNIQUE KEY unique_empresa_config (empresa_id)
);

-- Tabla ESCANEOS_TRACKING (para anti-duplicado)
CREATE TABLE ESCANEOS_TRACKING (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_qr VARCHAR(100) NOT NULL,
    timestamp_escaneo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    INDEX idx_codigo_qr_timestamp (codigo_qr, timestamp_escaneo)
);

-- Insertar empresas iniciales
INSERT INTO EMPRESAS (nombre, codigo_empresa) VALUES 
('ENTI MAX', 'EMX'),
('ENTIR EIRL', 'EIR'),
('PRENTIX', 'PRT');

-- Insertar horarios estándar
INSERT INTO HORARIOS_ESTANDAR (empresa_id, entrada_manana, salida_manana, entrada_tarde, salida_tarde) VALUES 
(1, '06:50:00', '12:50:00', '14:50:00', '18:50:00'),
(2, '06:50:00', '12:50:00', '14:50:00', '18:50:00'),
(3, '06:50:00', '12:50:00', '14:50:00', '18:50:00');

CREATE TABLE ALERTAS_ENVIADAS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    empleado_id INT NOT NULL,
    numero_faltas INT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empleado_id) REFERENCES EMPLEADOS(id) ON DELETE CASCADE,
    INDEX idx_empleado_faltas (empleado_id, numero_faltas),
    INDEX idx_fecha_envio (fecha_envio)
);

-- Índices adicionales
CREATE INDEX idx_asistencia_fecha ON ASISTENCIA(fecha);
CREATE INDEX idx_empleados_empresa ON EMPLEADOS(empresa_id);

