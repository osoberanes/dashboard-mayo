-- Función para actualizar timestamp de updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_departamentos_updated_at BEFORE UPDATE ON departamentos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_solicitudes_updated_at BEFORE UPDATE ON solicitudes_vacaciones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_actividades_updated_at BEFORE UPDATE ON actividades_fin_semana
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Función para calcular días acumulados desde ingreso
CREATE OR REPLACE FUNCTION calcular_dias_acumulados(fecha_ingreso DATE, dias_por_mes DECIMAL DEFAULT 2.5)
RETURNS DECIMAL AS $$
DECLARE
    meses_transcurridos INTEGER;
    dias_acumulados DECIMAL;
BEGIN
    -- Calcular meses completos desde ingreso hasta ahora
    meses_transcurridos := EXTRACT(YEAR FROM age(CURRENT_DATE, fecha_ingreso)) * 12 + 
                          EXTRACT(MONTH FROM age(CURRENT_DATE, fecha_ingreso));
    
    -- Calcular días acumulados
    dias_acumulados := meses_transcurridos * dias_por_mes;
    
    RETURN GREATEST(dias_acumulados, 0);
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar días acumulados automáticamente
CREATE OR REPLACE FUNCTION actualizar_dias_acumulados()
RETURNS void AS $$
DECLARE
    usuario_record RECORD;
    dias_usados DECIMAL;
    nuevo_saldo DECIMAL;
BEGIN
    FOR usuario_record IN SELECT id, fecha_ingreso FROM usuarios WHERE activo = TRUE LOOP
        -- Calcular días usados (solicitudes aprobadas)
        SELECT COALESCE(SUM(dias_solicitados), 0) INTO dias_usados
        FROM solicitudes_vacaciones 
        WHERE usuario_id = usuario_record.id 
        AND estado = 'aprobada';
        
        -- Calcular nuevo saldo
        nuevo_saldo := calcular_dias_acumulados(usuario_record.fecha_ingreso) - dias_usados;
        
        -- Actualizar saldo del usuario
        UPDATE usuarios 
        SET dias_acumulados = nuevo_saldo 
        WHERE id = usuario_record.id;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Función para validar reglas de negocio antes de crear solicitud
CREATE OR REPLACE FUNCTION validar_solicitud_vacaciones()
RETURNS TRIGGER AS $$
DECLARE
    dia_semana INTEGER;
    usuario_espejo_id INTEGER;
    conflicto_espejo BOOLEAN := FALSE;
    conflicto_departamento BOOLEAN := FALSE;
    dias_disponibles DECIMAL;
    tiene_actividad_fin_semana BOOLEAN := FALSE;
BEGIN
    -- Validar que no termine en viernes (5 = viernes)
    dia_semana := EXTRACT(DOW FROM NEW.fecha_fin);
    IF dia_semana = 5 THEN
        RAISE EXCEPTION 'Las vacaciones no pueden terminar en viernes';
    END IF;
    
    -- Obtener usuario espejo
    SELECT usuario_espejo_id INTO usuario_espejo_id 
    FROM usuarios WHERE id = NEW.usuario_id;
    
    -- Validar conflicto con usuario espejo
    IF usuario_espejo_id IS NOT NULL THEN
        SELECT EXISTS(
            SELECT 1 FROM solicitudes_vacaciones 
            WHERE usuario_id = usuario_espejo_id 
            AND estado IN ('pendiente', 'aprobada')
            AND (fecha_inicio <= NEW.fecha_fin AND fecha_fin >= NEW.fecha_inicio)
        ) INTO conflicto_espejo;
        
        IF conflicto_espejo THEN
            RAISE EXCEPTION 'Conflicto: el usuario espejo tiene vacaciones en el mismo período';
        END IF;
    END IF;
    
    -- Validar conflicto con otros usuarios del mismo departamento
    SELECT EXISTS(
        SELECT 1 FROM solicitudes_vacaciones sv
        JOIN usuarios u ON sv.usuario_id = u.id
        WHERE u.departamento_id = (SELECT departamento_id FROM usuarios WHERE id = NEW.usuario_id)
        AND sv.usuario_id != NEW.usuario_id
        AND sv.estado IN ('pendiente', 'aprobada')
        AND (sv.fecha_inicio <= NEW.fecha_fin AND sv.fecha_fin >= NEW.fecha_inicio)
    ) INTO conflicto_departamento;
    
    IF conflicto_departamento THEN
        RAISE EXCEPTION 'Conflicto: otro usuario del departamento tiene vacaciones en el mismo período';
    END IF;
    
    -- Validar días disponibles
    SELECT dias_acumulados INTO dias_disponibles 
    FROM usuarios WHERE id = NEW.usuario_id;
    
    IF NEW.dias_solicitados > dias_disponibles THEN
        RAISE EXCEPTION 'Días solicitados (%) exceden días disponibles (%)', 
                       NEW.dias_solicitados, dias_disponibles;
    END IF;
    
    -- Validar conflicto con actividades de fin de semana
    SELECT EXISTS(
        SELECT 1 FROM actividades_fin_semana 
        WHERE activo = TRUE
        AND (fecha_inicio <= NEW.fecha_fin AND fecha_fin >= NEW.fecha_inicio)
        AND NEW.usuario_id = ANY(usuarios_asignados)
    ) INTO tiene_actividad_fin_semana;
    
    IF tiene_actividad_fin_semana THEN
        RAISE EXCEPTION 'Conflicto: tienes actividades asignadas de fin de semana en este período';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para validaciones antes de insertar/actualizar solicitudes
CREATE TRIGGER trigger_validar_solicitud 
    BEFORE INSERT OR UPDATE ON solicitudes_vacaciones
    FOR EACH ROW EXECUTE FUNCTION validar_solicitud_vacaciones();

-- Función para actualizar días acumulados después de aprobar/rechazar solicitud
CREATE OR REPLACE FUNCTION actualizar_saldo_tras_aprobacion()
RETURNS TRIGGER AS $$
BEGIN
    -- Solo actualizar si cambió el estado a aprobada o de aprobada a otra cosa
    IF (OLD.estado != 'aprobada' AND NEW.estado = 'aprobada') OR 
       (OLD.estado = 'aprobada' AND NEW.estado != 'aprobada') THEN
        
        -- Recalcular días acumulados para este usuario
        UPDATE usuarios 
        SET dias_acumulados = calcular_dias_acumulados(fecha_ingreso) - (
            SELECT COALESCE(SUM(dias_solicitados), 0) 
            FROM solicitudes_vacaciones 
            WHERE usuario_id = NEW.usuario_id AND estado = 'aprobada'
        )
        WHERE id = NEW.usuario_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_actualizar_saldo 
    AFTER UPDATE ON solicitudes_vacaciones
    FOR EACH ROW EXECUTE FUNCTION actualizar_saldo_tras_aprobacion();