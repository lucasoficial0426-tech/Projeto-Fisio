-- ============================================
-- Script de Sanitização de Inconsistências
-- Funções para identificar, isolar e bloquear registros inconsistentes
-- ============================================

SET search_path TO fisio;

-- ============================================
-- Função para verificar CPFs duplicados em Pacientes
-- ============================================
CREATE OR REPLACE FUNCTION verificar_cpfs_duplicados_pacientes()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_cpf_record RECORD;
BEGIN
    FOR v_cpf_record IN 
        SELECT cpf, COUNT(*) as qtd 
        FROM paciente 
        GROUP BY cpf 
        HAVING COUNT(*) > 1
    LOOP
        -- Bloqueia todos os pacientes com CPF duplicado
        UPDATE paciente
        SET ativo = FALSE
        WHERE cpf = v_cpf_record.cpf;
        
        -- Registra inconsistência para cada paciente
        FOR v_cpf_record IN SELECT id FROM paciente WHERE cpf = v_cpf_record.cpf LOOP
            INSERT INTO auditoria_inconsistencia (tabela_origem, registro_id, tipo_inconsistencia, descricao)
            VALUES ('paciente', v_cpf_record.id, 'CPF duplicado', 
                    'Paciente com CPF duplicado: ' || v_cpf_record.cpf || ' (bloqueado)');
            v_count := v_count + 1;
        END LOOP;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Função para verificar pacotes com sessões em datas anteriores à compra
-- ============================================
CREATE OR REPLACE FUNCTION verificar_sessoes_anteriores_compra()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_pacote_record RECORD;
    v_sessao_count INTEGER;
BEGIN
    FOR v_pacote_record IN SELECT id, paciente_id, data_compra FROM pacote LOOP
        SELECT COUNT(*) INTO v_sessao_count
        FROM sessao
        WHERE pacote_id = v_pacote_record.id
          AND data_hora < v_pacote_record.data_compra;
        
        IF v_sessao_count > 0 THEN
            -- Bloqueia o pacote
            UPDATE pacote
            SET ativo = FALSE
            WHERE id = v_pacote_record.id;
            
            -- Bloqueia todas as sessões com este pacote
            UPDATE sessao
            SET ativo = FALSE
            WHERE pacote_id = v_pacote_record.id;
            
            -- Registra inconsistência
            INSERT INTO auditoria_inconsistencia (tabela_origem, registro_id, tipo_inconsistencia, descricao)
            VALUES ('pacote', v_pacote_record.id, 'Sessão anterior à compra', 
                    'Pacote com sessões agendadas em data anterior à compra (ID: ' || v_pacote_record.id || ')');
            v_count := v_count + 1;
        END IF;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Função para verificar pacotes expirados ou com saldo zerado
-- ============================================
CREATE OR REPLACE FUNCTION verificar_pacotes_expirados_ou_zerados()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_pacote_record RECORD;
BEGIN
    FOR v_pacote_record IN SELECT id, paciente_id, data_compra, validade_dias, sessoes_utilizadas, quantidade_sessoes FROM pacote LOOP
        -- Verifica se está expirado
        IF (v_pacote_record.data_compra + v_pacote_record.validade_dias * INTERVAL '1 day') < CURRENT_DATE THEN
            -- Bloqueia o pacote
            UPDATE pacote
            SET ativo = FALSE
            WHERE id = v_pacote_record.id;
            
            -- Bloqueia todas as sessões com este pacote
            UPDATE sessao
            SET ativo = FALSE
            WHERE pacote_id = v_pacote_record.id;
            
            -- Registra inconsistência
            INSERT INTO auditoria_inconsistencia (tabela_origem, registro_id, tipo_inconsistencia, descricao)
            VALUES ('pacote', v_pacote_record.id, 'Pacote expirado', 
                    'Pacote expirado: comprado em ' || v_pacote_record.data_compra || 
                    ', validade ' || v_pacote_record.validade_dias || ' dias (expirou em ' || 
                    (v_pacote_record.data_compra + v_pacote_record.validade_dias * INTERVAL '1 day')::DATE || ')');
            v_count := v_count + 1;
        END IF;
        
        -- Verifica se o saldo está zerado
        IF v_pacote_record.sessoes_utilizadas >= v_pacote_record.quantidade_sessoes THEN
            -- Bloqueia o pacote
            UPDATE pacote
            SET ativo = FALSE
            WHERE id = v_pacote_record.id;
            
            -- Registra inconsistência
            INSERT INTO auditoria_inconsistencia (tabela_origem, registro_id, tipo_inconsistencia, descricao)
            VALUES ('pacote', v_pacote_record.id, 'Saldo zerado', 
                    'Pacote com saldo zerado: ' || v_pacote_record.sessoes_utilizadas || '/' || 
                    v_pacote_record.quantidade_sessoes || ' sessões usadas');
            v_count := v_count + 1;
        END IF;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Função para verificar sessões com pacotes bloqueados
-- ============================================
CREATE OR REPLACE FUNCTION verificar_sessoes_com_pacotes_bloqueados()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_sessao_record RECORD;
    v_pacote_ativo BOOLEAN;
BEGIN
    FOR v_sessao_record IN SELECT id, pacote_id FROM sessao WHERE pacote_id IS NOT NULL LOOP
        SELECT ativo INTO v_pacote_ativo FROM pacote WHERE id = v_sessao_record.pacote_id;
        
        IF NOT v_pacote_ativo THEN
            -- Bloqueia a sessão
            UPDATE sessao
            SET ativo = FALSE
            WHERE id = v_sessao_record.id;
            
            -- Registra inconsistência
            INSERT INTO auditoria_inconsistencia (tabela_origem, registro_id, tipo_inconsistencia, descricao)
            VALUES ('sessao', v_sessao_record.id, 'Pacote bloqueado', 
                    'Sessão com pacote bloqueado (pacote_id: ' || v_sessao_record.pacote_id || ')');
            v_count := v_count + 1;
        END IF;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Função para verificar sessões de convênio sem evolução clínica (RN-06)
-- ============================================
CREATE OR REPLACE FUNCTION verificar_sessoes_convenio_sem_evolucao()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_sessao_record RECORD;
BEGIN
    FOR v_sessao_record IN 
        SELECT s.id, s.estado, s.evolucao_clinica, p.tipo as paciente_tipo
        FROM sessao s
        JOIN paciente p ON s.paciente_id = p.id
        WHERE p.tipo = 'Convênio' 
          AND s.estado = 'Faturada'
          AND (s.evolucao_clinica IS NULL OR LENGTH(TRIM(s.evolucao_clinica)) = 0)
    LOOP
        -- Bloqueia a sessão (não pode ser faturada sem evolução)
        UPDATE sessao
        SET ativo = FALSE
        WHERE id = v_sessao_record.id;
        
        -- Registra inconsistência
        INSERT INTO auditoria_inconsistencia (tabela_origem, registro_id, tipo_inconsistencia, descricao)
        VALUES ('sessao', v_sessao_record.id, 'Faturamento sem evolução', 
                'Sessão de convênio faturada sem evolução clínica (RN-06)');
        v_count := v_count + 1;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Função para verificar sessões com estado inválido (RN-08: Atendimento reduzido não pode ser faturado)
-- ============================================
CREATE OR REPLACE FUNCTION verificar_sessoes_atendimento_reduzido_faturadas()
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER := 0;
    v_sessao_record RECORD;
BEGIN
    FOR v_sessao_record IN 
        SELECT s.id, s.estado
        FROM sessao s
        JOIN sessao_lote sl ON s.id = sl.sessao_id
        WHERE s.estado = 'Atendimento reduzido' 
          AND sl.faturado = TRUE
    LOOP
        -- Desfaz o faturamento
        UPDATE sessao_lote
        SET faturado = FALSE
        WHERE sessao_id = v_sessao_record.id;
        
        -- Bloqueia a sessão
        UPDATE sessao
        SET ativo = FALSE
        WHERE id = v_sessao_record.id;
        
        -- Registra inconsistência
        INSERT INTO auditoria_inconsistencia (tabela_origem, registro_id, tipo_inconsistencia, descricao)
        VALUES ('sessao', v_sessao_record.id, 'Atendimento reduzido faturado', 
                'Sessão em estado "Atendimento reduzido" foi faturada (RN-08)');
        v_count := v_count + 1;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Função Principal: Executar Sanitização Completa
-- ============================================
CREATE OR REPLACE FUNCTION executar_sanitizacao_completa()
RETURNS TABLE (tabela VARCHAR, inconsistencias_encontradas INTEGER, descricao TEXT) AS $$
BEGIN
    -- 1. CPFs duplicados em pacientes
    RETURN QUERY SELECT 'paciente', verificar_cpfs_duplicados_pacientes(), 'CPFs duplicados';
    
    -- 2. Sessões anteriores à compra do pacote
    RETURN QUERY SELECT 'pacote', verificar_sessoes_anteriores_compra(), 'Sessões anteriores à compra';
    
    -- 3. Pacotes expirados ou com saldo zerado
    RETURN QUERY SELECT 'pacote', verificar_pacotes_expirados_ou_zerados(), 'Pacotes expirados ou saldo zerado';
    
    -- 4. Sessões com pacotes bloqueados
    RETURN QUERY SELECT 'sessao', verificar_sessoes_com_pacotes_bloqueados(), 'Sessões com pacotes bloqueados';
    
    -- 5. Sessões de convênio faturadas sem evolução
    RETURN QUERY SELECT 'sessao', verificar_sessoes_convenio_sem_evolucao(), 'Sessões de convênio sem evolução';
    
    -- 6. Sessões de atendimento reduzido faturadas
    RETURN QUERY SELECT 'sessao', verificar_sessoes_atendimento_reduzido_faturadas(), 'Sessões de atendimento reduzido faturadas';
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Procedimento para executar sanitização e gerar relatório
-- ============================================
CREATE OR REPLACE PROCEDURE sanitizar_banco()
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_inconsistencias INTEGER := 0;
    v_result RECORD;
BEGIN
    RAISE NOTICE 'Iniciando sanitização do banco de dados...';
    
    -- Executa sanitização completa
    FOR v_result IN SELECT * FROM executar_sanitizacao_completa() LOOP
        v_total_inconsistencias := v_total_inconsistencias + v_result.inconsistencias_encontradas;
        RAISE NOTICE 'Tabela %: % inconsistências encontradas (%))', 
            v_result.tabela, v_result.inconsistencias_encontradas, v_result.descricao;
    END LOOP;
    
    RAISE NOTICE 'Sanitização concluída. Total de inconsistências encontradas: %', v_total_inconsistencias;
    
    -- Exibe relatório final
    RAISE NOTICE '--- RELATÓRIO DE INCONSISTÊNCIAS ---';
    RAISE NOTICE 'Pacientes bloqueados: %', 
        (SELECT COUNT(*) FROM paciente WHERE ativo = FALSE);
    RAISE NOTICE 'Pacotes bloqueados: %', 
        (SELECT COUNT(*) FROM pacote WHERE ativo = FALSE);
    RAISE NOTICE 'Sessões bloqueadas: %', 
        (SELECT COUNT(*) FROM sessao WHERE ativo = FALSE);
    RAISE NOTICE 'Registros em auditoria: %', 
        (SELECT COUNT(*) FROM auditoria_inconsistencia);
END;
$$;

-- ============================================
-- Função para reativar registros (após correção manual)
-- ============================================
CREATE OR REPLACE FUNCTION reativar_registro(
    p_tabela VARCHAR(50),
    p_registro_id INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    IF p_tabela = 'paciente' THEN
        UPDATE paciente SET ativo = TRUE WHERE id = p_registro_id;
        RETURN TRUE;
    ELSIF p_tabela = 'pacote' THEN
        UPDATE pacote SET ativo = TRUE WHERE id = p_registro_id;
        RETURN TRUE;
    ELSIF p_tabela = 'sessao' THEN
        UPDATE sessao SET ativo = TRUE WHERE id = p_registro_id;
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Função para remover registro de auditoria (após correção)
-- ============================================
CREATE OR REPLACE FUNCTION remover_auditoria(
    p_id INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE auditoria_inconsistencia SET ativo = FALSE WHERE id = p_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Views para Monitoramento
-- ============================================

-- View para visualizar todas as inconsistências
CREATE OR REPLACE VIEW vw_inconsistencias AS
SELECT 
    ai.id,
    ai.tabela_origem,
    ai.registro_id,
    ai.tipo_inconsistencia,
    ai.descricao,
    ai.bloqueado_em,
    CASE 
        WHEN ai.tabela_origem = 'paciente' THEN (SELECT nome FROM paciente WHERE id = ai.registro_id)
        WHEN ai.tabela_origem = 'pacote' THEN (SELECT 'Pacote ' || id FROM pacote WHERE id = ai.registro_id)
        WHEN ai.tabela_origem = 'sessao' THEN (SELECT 'Sessão ' || id FROM sessao WHERE id = ai.registro_id)
        ELSE NULL
    END as registro_descricao
FROM auditoria_inconsistencia ai
WHERE ai.ativo = TRUE
ORDER BY ai.bloqueado_em DESC;

-- View para visualizar pacotes bloqueados
CREATE OR REPLACE VIEW vw_pacotes_bloqueados AS
SELECT 
    p.id,
    pt.nome as paciente,
    pt.cpf as paciente_cpf,
    p.data_compra,
    p.quantidade_sessoes,
    p.sessoes_utilizadas,
    p.validade_dias,
    (p.data_compra + p.validade_dias * INTERVAL '1 day')::DATE as data_vencimento,
    CASE 
        WHEN (p.data_compra + p.validade_dias * INTERVAL '1 day') < CURRENT_DATE THEN 'Expirado'
        WHEN p.sessoes_utilizadas >= p.quantidade_sessoes THEN 'Saldo zerado'
        ELSE 'Outro motivo'
    END as motivo_bloqueio,
    p.ativo,
    p.criado_em,
    p.atualizado_em
FROM pacote p
JOIN paciente pt ON p.paciente_id = pt.id
WHERE p.ativo = FALSE
ORDER BY p.data_compra;

-- View para visualizar sessões bloqueadas
CREATE OR REPLACE VIEW vw_sessoes_bloqueadas AS
SELECT 
    s.id,
    pt.nome as paciente,
    pr.nome as profissional,
    sl.nome as sala,
    s.data_hora,
    s.estado,
    s.pacote_id,
    CASE 
        WHEN s.pacote_id IS NOT NULL AND NOT (SELECT ativo FROM pacote WHERE id = s.pacote_id) THEN 'Pacote bloqueado'
        WHEN EXISTS (SELECT 1 FROM auditoria_inconsistencia WHERE registro_id = s.id) THEN 
            (SELECT tipo_inconsistencia FROM auditoria_inconsistencia WHERE registro_id = s.id LIMIT 1)
        ELSE 'Motivo desconhecido'
    END as motivo_bloqueio,
    s.ativo,
    s.criado_em,
    s.atualizado_em
FROM sessao s
JOIN paciente pt ON s.paciente_id = pt.id
JOIN profissional pr ON s.profissional_id = pr.id
JOIN sala sl ON s.sala_id = sl.id
WHERE s.ativo = FALSE
ORDER BY s.data_hora;
