-- Insertar departamentos iniciales
INSERT INTO departamentos (nombre, descripcion) VALUES
('Administración', 'Departamento administrativo y RRHH'),
('Tecnología', 'Departamento de desarrollo y sistemas'),
('Ventas', 'Departamento comercial y ventas'),
('Marketing', 'Departamento de marketing y comunicación'),
('Operaciones', 'Departamento de operaciones y logística');

-- Insertar configuración inicial del sistema
INSERT INTO configuracion_sistema (clave, valor, descripcion) VALUES
('DIAS_ACUMULACION_MENSUAL', '2.5', 'Días de vacaciones acumulados por mes'),
('PERIODO_LIMITE_DISFRUTE_MESES', '12', 'Período límite para disfrutar vacaciones en meses'),
('NOTIFICACIONES_EMAIL_ACTIVAS', 'true', 'Activar notificaciones por email'),
('SINCRONIZACION_GOOGLE_SHEETS_ACTIVA', 'false', 'Activar sincronización con Google Sheets'),
('PERMITIR_VACACIONES_VIERNES', 'false', 'Permitir que las vacaciones terminen en viernes'),
('DIAS_MINIMOS_ANTICIPACION', '7', 'Días mínimos de anticipación para solicitar vacaciones');

-- Insertar días festivos de México para 2024-2025
INSERT INTO dias_festivos (fecha, nombre, descripcion) VALUES
('2024-01-01', 'Año Nuevo', 'Celebración de Año Nuevo'),
('2024-02-05', 'Día de la Constitución', 'Conmemoración de la Constitución Mexicana'),
('2024-03-18', 'Natalicio de Benito Juárez', 'Conmemoración del natalicio de Benito Juárez'),
('2024-05-01', 'Día del Trabajo', 'Día Internacional del Trabajo'),
('2024-09-16', 'Día de la Independencia', 'Celebración de la Independencia de México'),
('2024-11-18', 'Revolución Mexicana', 'Conmemoración de la Revolución Mexicana'),
('2024-12-25', 'Navidad', 'Celebración de Navidad'),

('2025-01-01', 'Año Nuevo', 'Celebración de Año Nuevo'),
('2025-02-03', 'Día de la Constitución', 'Conmemoración de la Constitución Mexicana'),
('2025-03-17', 'Natalicio de Benito Juárez', 'Conmemoración del natalicio de Benito Juárez'),
('2025-05-01', 'Día del Trabajo', 'Día Internacional del Trabajo'),
('2025-09-16', 'Día de la Independencia', 'Celebración de la Independencia de México'),
('2025-11-17', 'Revolución Mexicana', 'Conmemoración de la Revolución Mexicana'),
('2025-12-25', 'Navidad', 'Celebración de Navidad');

-- Insertar usuario administrador inicial (password: admin123)
INSERT INTO usuarios (email, password_hash, nombre, apellidos, rol, departamento_id, fecha_ingreso, activo) VALUES
('admin@empresa.com', '$2a$10$8K1p/a0dqbQiUHUzrb.UzOd.yzk6pAJrYxoLtM/NnGwPLNfQ8M6iG', 'Administrador', 'Sistema', 'A', 1, '2024-01-01', true);

-- Crear vista para reportes de usuarios con días disponibles
CREATE VIEW vista_usuarios_dias_disponibles AS
SELECT 
    u.id,
    u.email,
    u.nombre,
    u.apellidos,
    u.rol,
    d.nombre as departamento,
    u.fecha_ingreso,
    u.dias_acumulados,
    COALESCE(SUM(CASE WHEN sv.estado = 'aprobada' THEN sv.dias_solicitados ELSE 0 END), 0) as dias_usados,
    (u.dias_acumulados - COALESCE(SUM(CASE WHEN sv.estado = 'aprobada' THEN sv.dias_solicitados ELSE 0 END), 0)) as dias_disponibles,
    COUNT(CASE WHEN sv.estado = 'pendiente' THEN 1 END) as solicitudes_pendientes
FROM usuarios u
LEFT JOIN departamentos d ON u.departamento_id = d.id
LEFT JOIN solicitudes_vacaciones sv ON u.id = sv.usuario_id
WHERE u.activo = true
GROUP BY u.id, u.email, u.nombre, u.apellidos, u.rol, d.nombre, u.fecha_ingreso, u.dias_acumulados;

-- Crear vista para calendario de vacaciones
CREATE VIEW vista_calendario_vacaciones AS
SELECT 
    sv.id,
    sv.fecha_inicio,
    sv.fecha_fin,
    sv.dias_solicitados,
    sv.estado,
    u.nombre || ' ' || u.apellidos as usuario_completo,
    u.email,
    d.nombre as departamento,
    sv.motivo,
    sv.created_at as fecha_solicitud
FROM solicitudes_vacaciones sv
JOIN usuarios u ON sv.usuario_id = u.id
LEFT JOIN departamentos d ON u.departamento_id = d.id
WHERE sv.estado IN ('pendiente', 'aprobada')
ORDER BY sv.fecha_inicio;