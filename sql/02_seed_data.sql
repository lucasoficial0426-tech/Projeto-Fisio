-- ============================================
-- Script de Carga Inicial de Dados (Seed)
-- Inclui lógica de sanitização de inconsistências
-- ============================================

-- Ativa o schema
SET search_path TO fisio;

-- ============================================
-- Função para registrar inconsistências
-- ============================================
CREATE OR REPLACE FUNCTION registrar_inconsistencia(
    p_tabela VARCHAR(50),
    p_registro_id INTEGER,
    p_tipo VARCHAR(100),
    p_descricao TEXT
) RETURNS VOID AS $$
BEGIN
    INSERT INTO auditoria_inconsistencia (tabela_origem, registro_id, tipo_inconsistencia, descricao)
    VALUES (p_tabela, p_registro_id, p_tipo, p_descricao);
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Inserção de Convênios
-- ============================================
INSERT INTO convenio (nome, cnpj, ativo) VALUES
('SaúdeMais', '12.345.678/0001-01', TRUE),
('UniPlano', '98.765.432/0001-02', TRUE)
ON CONFLICT (nome) DO NOTHING;

-- ============================================
-- Inserção de Salas
-- ============================================
INSERT INTO sala (nome, capacidade, descricao, ativo) VALUES
('Sala 1', 1, 'Sala individual', TRUE),
('Sala 2', 1, 'Sala individual', TRUE),
('Sala 3 - Pilates', 3, 'Sala para aulas de pilates', TRUE)
ON CONFLICT (nome) DO NOTHING;

-- ============================================
-- Inserção de Profissionais
-- ============================================
-- Helena Kobayashi (sócia)
INSERT INTO profissional (nome, cpf, tipo, ativo) VALUES
('Helena Kobayashi', '123.456.789-09', 'Sócio', TRUE)
ON CONFLICT (cpf) DO NOTHING;

-- Diego Martins (contratado)
INSERT INTO profissional (nome, cpf, tipo, ativo) VALUES
('Diego Martins', '987.654.321-00', 'Contratado', TRUE)
ON CONFLICT (cpf) DO NOTHING;

-- Sabrina Luz (contratada)
INSERT INTO profissional (nome, cpf, tipo, ativo) VALUES
('Sabrina Luz', '456.789.123-01', 'Contratado', TRUE)
ON CONFLICT (cpf) DO NOTHING;

-- ============================================
-- Inserção de Pacientes
-- ============================================
-- Marta Siqueira (Particular)
INSERT INTO paciente (nome, cpf, tipo, convenio_id, ativo) VALUES
('Marta Siqueira', '111.111.111-11', 'Particular', NULL, TRUE)
ON CONFLICT (cpf) DO NOTHING;

-- Ricardo Tavares (Particular)
INSERT INTO paciente (nome, cpf, tipo, convenio_id, ativo) VALUES
('Ricardo Tavares', '222.222.222-22', 'Particular', NULL, TRUE)
ON CONFLICT (cpf) DO NOTHING;

-- José Anselmo Reis (Convênio SaúdeMais)
INSERT INTO paciente (nome, cpf, tipo, convenio_id, ativo) VALUES
('José Anselmo Reis', '333.333.333-33', 'Convênio', (SELECT id FROM convenio WHERE nome = 'SaúdeMais'), TRUE)
ON CONFLICT (cpf) DO NOTHING;

-- Carla Bonatto (Convênio UniPlano)
INSERT INTO paciente (nome, cpf, tipo, convenio_id, ativo) VALUES
('Carla Bonatto', '444.444.444-44', 'Convênio', (SELECT id FROM convenio WHERE nome = 'UniPlano'), TRUE)
ON CONFLICT (cpf) DO NOTHING;

-- ============================================
-- Função para verificar e bloquear inconsistências em Pacientes
-- ============================================
DO $$
DECLARE
    v_paciente_record RECORD;
    v_cpf_duplicado_count INTEGER;
BEGIN
    -- Verifica CPFs duplicados
    FOR v_paciente_record IN SELECT cpf, COUNT(*) as count FROM paciente GROUP BY cpf HAVING COUNT(*) > 1 LOOP
        -- Bloqueia todos os pacientes com CPF duplicado
        UPDATE paciente
        SET ativo = FALSE
        WHERE cpf = v_paciente_record.cpf;
        
        -- Registra inconsistência para cada paciente com CPF duplicado
        FOR v_paciente_record IN SELECT id FROM paciente WHERE cpf = v_paciente_record.cpf LOOP
            PERFORM registrar_inconsistencia('paciente', v_paciente_record.id, 'CPF duplicado', 'Paciente com CPF duplicado: ' || v_paciente_record.cpf);
        END LOOP;
    END LOOP;
END $$;

-- ============================================
-- Inserção de Pacotes
-- ============================================

-- P-01: Marta Siqueira, comprado em 12/08/2026 (7 de 10 sessões usadas)
INSERT INTO pacote (paciente_id, data_compra, quantidade_sessoes, sessoes_utilizadas, validade_dias, ativo)
SELECT 
    p.id,
    '2026-08-12'::DATE,
    10,
    7,
    90,
    TRUE
FROM paciente p WHERE p.nome = 'Marta Siqueira' AND p.cpf = '111.111.111-11'
ON CONFLICT DO NOTHING;

-- P-02: Marta Siqueira, comprado em 20/05/2026 (10 de 10 sessões usadas)
-- Este pacote está EXPIRADO (90 dias a partir de 20/05/2026 = 18/08/2026)
-- e com saldo zerado, então deve ser BLOQUEADO
INSERT INTO pacote (paciente_id, data_compra, quantidade_sessoes, sessoes_utilizadas, validade_dias, ativo)
SELECT 
    p.id,
    '2026-05-20'::DATE,
    10,
    10,
    90,
    FALSE  -- Bloqueado por estar expirado e com saldo zerado
FROM paciente p WHERE p.nome = 'Marta Siqueira' AND p.cpf = '111.111.111-11'
ON CONFLICT DO NOTHING;

-- Registra inconsistência para P-02 (expirado e saldo zerado)
DO $$
DECLARE
    v_pacote_id INTEGER;
BEGIN
    SELECT id INTO v_pacote_id
    FROM pacote
    WHERE paciente_id = (SELECT id FROM paciente WHERE cpf = '111.111.111-11')
      AND data_compra = '2026-05-20'::DATE;
    
    IF v_pacote_id IS NOT NULL THEN
        PERFORM registrar_inconsistencia('pacote', v_pacote_id, 'Pacote expirado e saldo zerado', 
            'Pacote comprado em 20/05/2026 com 90 dias de validade (expirou em 18/08/2026) e 10/10 sessões usadas.');
    END IF;
END $$;

-- P-03: Ricardo Tavares, comprado em 05/09/2026 (1 de 10 sessões usadas)
INSERT INTO pacote (paciente_id, data_compra, quantidade_sessoes, sessoes_utilizadas, validade_dias, ativo)
SELECT 
    p.id,
    '2026-09-05'::DATE,
    10,
    1,
    90,
    TRUE
FROM paciente p WHERE p.nome = 'Ricardo Tavares' AND p.cpf = '222.222.222-22'
ON CONFLICT DO NOTHING;

-- ============================================
-- Função para verificar e bloquear pacotes com sessões em datas anteriores à compra
-- ============================================
DO $$
DECLARE
    v_pacote_record RECORD;
    v_sessao_count INTEGER;
BEGIN
    -- Verifica se há sessões agendadas em datas anteriores à compra do pacote
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
            
            -- Registra inconsistência
            PERFORM registrar_inconsistencia('pacote', v_pacote_record.id, 'Sessão anterior à compra',
                'Pacote com sessões agendadas em data anterior à compra do pacote.');
        END IF;
    END LOOP;
END $$;

-- ============================================
-- Inserção de Sessões (para teste dos casos oficiais)
-- ============================================

-- Sessões para o Caso 1: Sala 3 com 3 sessões às 10h
-- (Para testar capacidade máxima da Sala 3)
INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    NULL,  -- Sessão sem pacote (para teste de capacidade)
    '2026-09-15 10:00:00'::TIMESTAMP,
    'Agendada',
    TRUE
FROM paciente p, profissional pr, sala s
WHERE p.nome = 'Marta Siqueira' 
  AND pr.nome = 'Helena Kobayashi'
  AND s.nome = 'Sala 3 - Pilates'
ON CONFLICT DO NOTHING;

INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    NULL,
    '2026-09-15 10:00:00'::TIMESTAMP,
    'Agendada',
    TRUE
FROM paciente p, profissional pr, sala s
WHERE p.nome = 'Ricardo Tavares' 
  AND pr.nome = 'Diego Martins'
  AND s.nome = 'Sala 3 - Pilates'
ON CONFLICT DO NOTHING;

INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    NULL,
    '2026-09-15 10:00:00'::TIMESTAMP,
    'Agendada',
    TRUE
FROM paciente p, profissional pr, sala s
WHERE p.nome = 'José Anselmo Reis' 
  AND pr.nome = 'Sabrina Luz'
  AND s.nome = 'Sala 3 - Pilates'
ON CONFLICT DO NOTHING;

-- Sessão para o Caso 2: Sabrina tem sessão às 10h na Sala 3
INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    NULL,
    '2026-09-16 10:00:00'::TIMESTAMP,
    'Agendada',
    TRUE
FROM paciente p, profissional pr, sala s
WHERE p.nome = 'Carla Bonatto' 
  AND pr.nome = 'Sabrina Luz'
  AND s.nome = 'Sala 3 - Pilates'
ON CONFLICT DO NOTHING;

-- Sessão para o Caso 4: Marta tem 3 sessões no P-01 (para testar falta sem aviso)
-- Usando o pacote P-01 (Marta Siqueira, 7/10 sessões usadas)
INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    pt.id,
    '2026-09-17 14:00:00'::TIMESTAMP,
    'Agendada',
    TRUE
FROM paciente p, profissional pr, sala s, pacote pt
WHERE p.nome = 'Marta Siqueira' 
  AND p.cpf = '111.111.111-11'
  AND pr.nome = 'Helena Kobayashi'
  AND s.nome = 'Sala 1'
  AND pt.paciente_id = p.id
  AND pt.data_compra = '2026-08-12'::DATE
ON CONFLICT DO NOTHING;

-- Sessão para o Caso 5: Marta tem 3 sessões no P-01 (para testar cancelamento com aviso)
INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    pt.id,
    '2026-09-18 15:00:00'::TIMESTAMP,
    'Agendada',
    TRUE
FROM paciente p, profissional pr, sala s, pacote pt
WHERE p.nome = 'Marta Siqueira' 
  AND p.cpf = '111.111.111-11'
  AND pr.nome = 'Helena Kobayashi'
  AND s.nome = 'Sala 1'
  AND pt.paciente_id = p.id
  AND pt.data_compra = '2026-08-12'::DATE
ON CONFLICT DO NOTHING;

-- Sessão para o Caso 6: Teste com pacote P-02 (expirado)
-- Esta sessão NÃO deve ser agendada (pacote expirado)
-- Vamos inserir como 'Agendada' para testar a validação
INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    pt.id,
    '2026-09-19 16:00:00'::TIMESTAMP,
    'Agendada',
    FALSE  -- Bloqueada por pacote expirado
FROM paciente p, profissional pr, sala s, pacote pt
WHERE p.nome = 'Marta Siqueira' 
  AND p.cpf = '111.111.111-11'
  AND pr.nome = 'Helena Kobayashi'
  AND s.nome = 'Sala 1'
  AND pt.paciente_id = p.id
  AND pt.data_compra = '2026-05-20'::DATE
ON CONFLICT DO NOTHING;

-- Registra inconsistência para a sessão com pacote expirado
DO $$
DECLARE
    v_sessao_id INTEGER;
BEGIN
    SELECT id INTO v_sessao_id
    FROM sessao
    WHERE paciente_id = (SELECT id FROM paciente WHERE cpf = '111.111.111-11')
      AND pacote_id = (SELECT id FROM pacote WHERE data_compra = '2026-05-20'::DATE);
    
    IF v_sessao_id IS NOT NULL THEN
        PERFORM registrar_inconsistencia('sessao', v_sessao_id, 'Pacote expirado', 
            'Sessão agendada com pacote P-02 (expirado em 18/08/2026).');
    END IF;
END $$;

-- Sessão para o Caso 7: José tem sessão realizada sem evolução (Convênio SaúdeMais)
INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, evolucao_clinica, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    NULL,
    '2026-09-20 10:00:00'::TIMESTAMP,
    'Realizada',
    NULL,  -- Sem evolução clínica
    TRUE
FROM paciente p, profissional pr, sala s
WHERE p.nome = 'José Anselmo Reis' 
  AND pr.nome = 'Diego Martins'
  AND s.nome = 'Sala 2'
ON CONFLICT DO NOTHING;

-- Sessão para o Caso 8: Mesma sessão do Caso 7, mas com evolução
INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, evolucao_clinica, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    NULL,
    '2026-09-21 10:00:00'::TIMESTAMP,
    'Evoluída',
    'Paciente apresentou melhora significativa na mobilidade.',
    TRUE
FROM paciente p, profissional pr, sala s
WHERE p.nome = 'José Anselmo Reis' 
  AND pr.nome = 'Diego Martins'
  AND s.nome = 'Sala 2'
ON CONFLICT DO NOTHING;

-- Sessão para o Caso 9: Carla chega 20 min atrasada (Convênio UniPlano)
INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, evolucao_clinica, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    NULL,
    '2026-09-22 11:00:00'::TIMESTAMP,
    'Atendimento reduzido',
    'Paciente chegou 20 minutos atrasado.',
    TRUE
FROM paciente p, profissional pr, sala s
WHERE p.nome = 'Carla Bonatto' 
  AND pr.nome = 'Sabrina Luz'
  AND s.nome = 'Sala 1'
ON CONFLICT DO NOTHING;

-- ============================================
-- Sessões para o Caso 10: Relatório de Ocupação de Setembro
-- ============================================

-- Sessões em setembro nas três salas
INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    NULL,
    '2026-09-01 09:00:00'::TIMESTAMP,
    'Realizada',
    TRUE
FROM paciente p, profissional pr, sala s
WHERE p.nome = 'Marta Siqueira' 
  AND pr.nome = 'Helena Kobayashi'
  AND s.nome = 'Sala 1'
ON CONFLICT DO NOTHING;

INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    NULL,
    '2026-09-01 10:00:00'::TIMESTAMP,
    'Realizada',
    TRUE
FROM paciente p, profissional pr, sala s
WHERE p.nome = 'Ricardo Tavares' 
  AND pr.nome = 'Diego Martins'
  AND s.nome = 'Sala 2'
ON CONFLICT DO NOTHING;

INSERT INTO sessao (paciente_id, profissional_id, sala_id, pacote_id, data_hora, estado, ativo)
SELECT 
    p.id,
    pr.id,
    s.id,
    NULL,
    '2026-09-01 11:00:00'::TIMESTAMP,
    'Realizada',
    TRUE
FROM paciente p, profissional pr, sala s
WHERE p.nome = 'José Anselmo Reis' 
  AND pr.nome = 'Sabrina Luz'
  AND s.nome = 'Sala 3 - Pilates'
ON CONFLICT DO NOTHING;

-- ============================================
-- Função para verificar e bloquear sessões com pacotes inconsistentes
-- ============================================
DO $$
DECLARE
    v_sessao_record RECORD;
    v_pacote_valido BOOLEAN;
BEGIN
    FOR v_sessao_record IN SELECT id, pacote_id FROM sessao WHERE pacote_id IS NOT NULL LOOP
        -- Verifica se o pacote está ativo e válido
        SELECT ativo INTO v_pacote_valido
        FROM pacote WHERE id = v_sessao_record.pacote_id;
        
        IF NOT v_pacote_valido THEN
            -- Bloqueia a sessão
            UPDATE sessao
            SET ativo = FALSE
            WHERE id = v_sessao_record.id;
            
            -- Registra inconsistência
            PERFORM registrar_inconsistencia('sessao', v_sessao_record.id, 'Pacote inconsistente',
                'Sessão com pacote bloqueado ou expirado.');
        END IF;
    END LOOP;
END $$;

-- ============================================
-- Resumo da Carga Inicial
-- ============================================

-- Exibe resumo das tabelas
SELECT 'Convênios' as tabela, COUNT(*) as quantidade FROM convenio;
SELECT 'Salas' as tabela, COUNT(*) as quantidade FROM sala;
SELECT 'Profissionais' as tabela, COUNT(*) as quantidade FROM profissional;
SELECT 'Pacientes' as tabela, COUNT(*) as quantidade FROM paciente;
SELECT 'Pacotes' as tabela, COUNT(*) as quantidade FROM pacote;
SELECT 'Sessões' as tabela, COUNT(*) as quantidade FROM sessao;

-- Exibe registros inconsistentes bloqueados
SELECT 
    tabela_origem,
    registro_id,
    tipo_inconsistencia,
    descricao,
    bloqueado_em
FROM auditoria_inconsistencia
ORDER BY bloqueado_em;

-- Exibe pacotes bloqueados
SELECT 
    p.id,
    pt.nome as paciente,
    p.data_compra,
    p.quantidade_sessoes,
    p.sessoes_utilizadas,
    p.validade_dias,
    (p.data_compra + p.validade_dias * INTERVAL '1 day') as data_vencimento,
    p.ativo
FROM pacote p
JOIN paciente pt ON p.paciente_id = pt.id
WHERE p.ativo = FALSE;

-- Exibe sessões bloqueadas
SELECT 
    s.id,
    pt.nome as paciente,
    pr.nome as profissional,
    sl.nome as sala,
    s.data_hora,
    s.estado,
    s.ativo
FROM sessao s
JOIN paciente pt ON s.paciente_id = pt.id
JOIN profissional pr ON s.profissional_id = pr.id
JOIN sala sl ON s.sala_id = sl.id
WHERE s.ativo = FALSE;
