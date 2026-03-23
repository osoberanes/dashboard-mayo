-- Creación de tipos enum
CREATE TYPE user_role AS ENUM ('A', 'B', 'C');
CREATE TYPE solicitud_estado AS ENUM ('pendiente', 'aprobada', 'rechazada', 'cancelada');

-- Tabla de departamentos
CREATE TABLE departamentos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de días festivos
CREATE TABLE dias_festivos (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(200) NOT NULL,
    rol user_role NOT NULL DEFAULT 'C',
    departamento_id INTEGER REFERENCES departamentos(id),
    usuario_espejo_id INTEGER REFERENCES usuarios(id),
    fecha_ingreso DATE NOT NULL,
    dias_acumulados DECIMAL(5,2) DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_usuario_espejo_diferente CHECK (id != usuario_espejo_id)
);

-- Tabla de solicitudes de vacaciones
CREATE TABLE solicitudes_vacaciones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    dias_solicitados INTEGER NOT NULL,
    motivo TEXT,
    estado solicitud_estado DEFAULT 'pendiente',
    aprobado_por INTEGER REFERENCES usuarios(id),
    fecha_aprobacion TIMESTAMP,
    comentarios_admin TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_fechas_validas CHECK (fecha_fin >= fecha_inicio),
    CONSTRAINT check_dias_positivos CHECK (dias_solicitados > 0)
);

-- Tabla de actividades de fin de semana
CREATE TABLE actividades_fin_semana (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    usuarios_asignados INTEGER[],
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_fechas_actividad_validas CHECK (fecha_fin >= fecha_inicio)
);

-- Tabla de configuración del sistema
CREATE TABLE configuracion_sistema (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descripcion TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de logs de sincronización con Google Sheets
CREATE TABLE logs_sincronizacion (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL, -- 'export', 'import', 'sync'
    estado VARCHAR(50) NOT NULL, -- 'success', 'error', 'warning'
    mensaje TEXT,
    datos_procesados JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimización
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_departamento ON usuarios(departamento_id);
CREATE INDEX idx_solicitudes_usuario ON solicitudes_vacaciones(usuario_id);
CREATE INDEX idx_solicitudes_fechas ON solicitudes_vacaciones(fecha_inicio, fecha_fin);
CREATE INDEX idx_solicitudes_estado ON solicitudes_vacaciones(estado);
CREATE INDEX idx_dias_festivos_fecha ON dias_festivos(fecha);
CREATE INDEX idx_actividades_fechas ON actividades_fin_semana(fecha_inicio, fecha_fin);