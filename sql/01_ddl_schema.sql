-- ============================================
-- DDL - Esquema do Banco de Dados "Sessão"
-- Normalizado em 3FN com PKs, FKs, constraints e RNs
-- ============================================

-- Criação do schema
CREATE SCHEMA IF NOT EXISTS fisio;
SET search_path TO fisio;

-- ============================================
-- Tabelas de Domínio (Lookup Tables)
-- ============================================

-- Estados possíveis para uma Sessão
CREATE TYPE estado_sessao AS ENUM (
    'Agendada',
    'Realizada',
    'Evoluída',
    'Faturada',
    'Cancelada com aviso',
    'Falta sem aviso',
    'Atendimento reduzido'
);

-- Tipos de Paciente
CREATE TYPE tipo_paciente AS ENUM (
    'Particular',
    'Convênio'
);

-- Tipos de Profissional
CREATE TYPE tipo_profissional AS ENUM (
    'Sócio',
    'Contratado'
);

-- ============================================
-- Tabelas Principais
-- ============================================

-- Tabela: Sala
CREATE TABLE sala (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    capacidade INTEGER NOT NULL CHECK (capacidade > 0),
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Profissional
CREATE TABLE profissional (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    tipo tipo_profissional NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Paciente
CREATE TABLE paciente (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) UNIQUE NOT NULL,
    tipo tipo_paciente NOT NULL,
    convenio_id INTEGER,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_paciente_convenio FOREIGN KEY (convenio_id) REFERENCES convenio(id)
);

-- Tabela: Convênio
CREATE TABLE convenio (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    cnpj VARCHAR(18) UNIQUE,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Pacote
CREATE TABLE pacote (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL,
    data_compra DATE NOT NULL,
    quantidade_sessoes INTEGER NOT NULL CHECK (quantidade_sessoes > 0),
    sessoes_utilizadas INTEGER DEFAULT 0 CHECK (sessoes_utilizadas >= 0),
    validade_dias INTEGER NOT NULL CHECK (validade_dias > 0),
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pacote_paciente FOREIGN KEY (paciente_id) REFERENCES paciente(id),
    -- RN-01: Validade padrão de 90 dias (antes de 01/11/2026) ou 120 dias (após)
    CONSTRAINT chk_validade_pacote CHECK (
        (data_compra < '2026-11-01' AND validade_dias = 90 AND quantidade_sessoes = 10) OR
        (data_compra >= '2026-11-01' AND validade_dias = 120 AND quantidade_sessoes = 15) OR
        -- Permite pacotes personalizados (para migração ou casos especiais)
        (quantidade_sessoes IN (10, 15) AND validade_dias IN (90, 120))
    )
);

-- Tabela: Sessão
CREATE TABLE sessao (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL,
    profissional_id INTEGER NOT NULL,
    sala_id INTEGER NOT NULL,
    pacote_id INTEGER,
    data_hora TIMESTAMP NOT NULL,
    duracao_minutos INTEGER DEFAULT 60 CHECK (duracao_minutos > 0),
    estado estado_sessao NOT NULL DEFAULT 'Agendada',
    evolucao_clinica TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sessao_paciente FOREIGN KEY (paciente_id) REFERENCES paciente(id),
    CONSTRAINT fk_sessao_profissional FOREIGN KEY (profissional_id) REFERENCES profissional(id),
    CONSTRAINT fk_sessao_sala FOREIGN KEY (sala_id) REFERENCES sala(id),
    CONSTRAINT fk_sessao_pacote FOREIGN KEY (pacote_id) REFERENCES pacote(id),
    -- RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica
    CONSTRAINT chk_sessao_convenio_faturavel CHECK (
        (paciente_id IN (SELECT id FROM paciente WHERE tipo = 'Convênio') AND estado = 'Faturada') = FALSE OR
        (evolucao_clinica IS NOT NULL AND LENGTH(TRIM(evolucao_clinica)) > 0)
    )
);

-- Tabela: Lote de Convênio (para faturamento em lote)
CREATE TABLE lote_convenio (
    id SERIAL PRIMARY KEY,
    convenio_id INTEGER NOT NULL,
    data_geracao DATE NOT NULL DEFAULT CURRENT_DATE,
    data_faturamento DATE,
    valor_total NUMERIC(10, 2) DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'Pendente' CHECK (estado IN ('Pendente', 'Faturado', 'Bloqueado')),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_lote_convenio FOREIGN KEY (convenio_id) REFERENCES convenio(id)
);

-- Tabela: Sessão no Lote (relacionamento N:N entre Sessão e Lote de Convênio)
CREATE TABLE sessao_lote (
    id SERIAL PRIMARY KEY,
    sessao_id INTEGER NOT NULL,
    lote_convenio_id INTEGER NOT NULL,
    valor NUMERIC(10, 2) NOT NULL,
    faturado BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sessao_lote_sessao FOREIGN KEY (sessao_id) REFERENCES sessao(id),
    CONSTRAINT fk_sessao_lote_lote FOREIGN KEY (lote_convenio_id) REFERENCES lote_convenio(id),
    UNIQUE (sessao_id, lote_convenio_id)
);

-- ============================================
-- Índices para Performance
-- ============================================

CREATE INDEX idx_sessao_data_hora ON sessao(data_hora);
CREATE INDEX idx_sessao_estado ON sessao(estado);
CREATE INDEX idx_sessao_paciente ON sessao(paciente_id);
CREATE INDEX idx_sessao_profissional ON sessao(profissional_id);
CREATE INDEX idx_sessao_sala ON sessao(sala_id);
CREATE INDEX idx_pacote_paciente ON pacote(paciente_id);
CREATE INDEX idx_pacote_data_compra ON pacote(data_compra);
CREATE INDEX idx_paciente_tipo ON paciente(tipo);

-- ============================================
-- Funções de Validação (RN-04 a RN-08)
-- ============================================

-- Função para verificar capacidade da sala (RN-04)
CREATE OR REPLACE FUNCTION verificar_capacidade_sala(
    p_sala_id INTEGER,
    p_data_hora TIMESTAMP
) RETURNS BOOLEAN AS $$
DECLARE
    v_capacidade INTEGER;
    v_sessoes_agendadas INTEGER;
BEGIN
    SELECT capacidade INTO v_capacidade FROM sala WHERE id = p_sala_id;
    
    SELECT COUNT(*) INTO v_sessoes_agendadas
    FROM sessao
    WHERE sala_id = p_sala_id
      AND data_hora = p_data_hora
      AND estado NOT IN ('Cancelada com aviso', 'Falta sem aviso')
      AND ativo = TRUE;
    
    RETURN v_sessoes_agendadas < v_capacidade;
END;
$$ LANGUAGE plpgsql;

-- Função para verificar conflitos de profissional (RN-05)
CREATE OR REPLACE FUNCTION verificar_conflito_profissional(
    p_profissional_id INTEGER,
    p_data_hora TIMESTAMP
) RETURNS BOOLEAN AS $$
DECLARE
    v_conflitos INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_conflitos
    FROM sessao
    WHERE profissional_id = p_profissional_id
      AND data_hora = p_data_hora
      AND estado NOT IN ('Cancelada com aviso', 'Falta sem aviso')
      AND ativo = TRUE;
    
    RETURN v_conflitos = 0;
END;
$$ LANGUAGE plpgsql;

-- Função para verificar validade do pacote (RN-01 e RN-07)
CREATE OR REPLACE FUNCTION verificar_validade_pacote(
    p_pacote_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_data_compra DATE;
    v_validade_dias INTEGER;
    v_sessoes_utilizadas INTEGER;
    v_quantidade_sessoes INTEGER;
BEGIN
    SELECT data_compra, validade_dias, sessoes_utilizadas, quantidade_sessoes
    INTO v_data_compra, v_validade_dias, v_sessoes_utilizadas, v_quantidade_sessoes
    FROM pacote WHERE id = p_pacote_id;
    
    -- Verifica se o pacote está expirado
    IF (v_data_compra + v_validade_dias * INTERVAL '1 day') < CURRENT_DATE THEN
        RETURN FALSE; -- Pacote expirado
    END IF;
    
    -- Verifica se o saldo está zerado
    IF v_sessoes_utilizadas >= v_quantidade_sessoes THEN
        RETURN FALSE; -- Saldo zerado
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Função para registrar falta sem aviso (RN-02)
CREATE OR REPLACE FUNCTION registrar_falta_sem_aviso(
    p_sessao_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_pacote_id INTEGER;
    v_paciente_id INTEGER;
BEGIN
    SELECT pacote_id, paciente_id INTO v_pacote_id, v_paciente_id
    FROM sessao WHERE id = p_sessao_id;
    
    -- Verifica se o paciente é particular (RN-07: particular com pacote expirado/zerado não pode ser agendado, mas falta consome sessão)
    IF v_pacote_id IS NOT NULL THEN
        -- RN-02: Falta sem aviso consome uma sessão do pacote
        UPDATE pacote
        SET sessoes_utilizadas = sessoes_utilizadas + 1,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = v_pacote_id
        AND (data_compra + validade_dias * INTERVAL '1 day') >= CURRENT_DATE; -- Só consome se não expirado
        
        -- Atualiza estado da sessão
        UPDATE sessao
        SET estado = 'Falta sem aviso',
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = p_sessao_id;
        
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Função para verificar se sessão pode ser faturada (RN-06 e RN-08)
CREATE OR REPLACE FUNCTION pode_faturar_sessao(
    p_sessao_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_paciente_tipo tipo_paciente;
    v_estado estado_sessao;
    v_evolucao TEXT;
    v_atraso BOOLEAN;
BEGIN
    SELECT p.tipo, s.estado, s.evolucao_clinica
    INTO v_paciente_tipo, v_estado, v_evolucao
    FROM sessao s
    JOIN paciente p ON s.paciente_id = p.id
    WHERE s.id = p_sessao_id;
    
    -- RN-08: Atendimento reduzido (atraso > 15 min) bloqueia faturamento
    IF v_estado = 'Atendimento reduzido' THEN
        RETURN FALSE;
    END IF;
    
    -- RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica
    IF v_paciente_tipo = 'Convênio' THEN
        IF v_evolucao IS NULL OR LENGTH(TRIM(v_evolucao)) = 0 THEN
            RETURN FALSE;
        END IF;
    END IF;
    
    -- Fluxo principal: deve estar em estado Evoluída
    IF v_estado != 'Evoluída' THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Triggers para Atualização de Timestamps
-- ============================================

CREATE OR REPLACE FUNCTION atualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sala_atualizado BEFORE UPDATE ON sala FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trg_profissional_atualizado BEFORE UPDATE ON profissional FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trg_paciente_atualizado BEFORE UPDATE ON paciente FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trg_convenio_atualizado BEFORE UPDATE ON convenio FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trg_pacote_atualizado BEFORE UPDATE ON pacote FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trg_sessao_atualizado BEFORE UPDATE ON sessao FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();
CREATE TRIGGER trg_lote_convenio_atualizado BEFORE UPDATE ON lote_convenio FOR EACH ROW EXECUTE FUNCTION atualizar_timestamp();

-- ============================================
-- Tabelas de Auditoria (para registros inconsistentes)
-- ============================================

-- Tabela para armazena registros inconsistentes (bloqueados)
CREATE TABLE auditoria_inconsistencia (
    id SERIAL PRIMARY KEY,
    tabela_origem VARCHAR(50) NOT NULL,
    registro_id INTEGER NOT NULL,
    tipo_inconsistencia VARCHAR(100) NOT NULL,
    descricao TEXT NOT NULL,
    bloqueado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE
);

-- ============================================
-- Comentários das Tabelas
-- ============================================

COMMENT ON TABLE sala IS 'Armazena informações sobre as salas de atendimento.';
COMMENT ON TABLE profissional IS 'Armazena informações sobre os profissionais (fisioterapeutas).';
COMMENT ON TABLE paciente IS 'Armazena informações sobre os pacientes.';
COMMENT ON TABLE convenio IS 'Armazena informações sobre os convênios.';
COMMENT ON TABLE pacote IS 'Armazena informações sobre os pacotes de sessões comprados pelos pacientes.';
COMMENT ON TABLE sessao IS 'Armazena informações sobre as sessões agendadas.';
COMMENT ON TABLE lote_convenio IS 'Armazena lotes de faturamento para convênios.';
COMMENT ON TABLE sessao_lote IS 'Relacionamento entre sessões e lotes de convênio.';
COMMENT ON TABLE auditoria_inconsistencia IS 'Armazena registros inconsistentes bloqueados.';

COMMENT ON COLUMN sessao.estado IS 'Estado da sessão (Agendada, Realizada, Evoluída, Faturada, etc.).';
COMMENT ON COLUMN pacote.validade_dias IS 'Quantidade de dias de validade do pacote (90 ou 120).';
COMMENT ON COLUMN pacote.quantidade_sessoes IS 'Quantidade de sessões do pacote (10 ou 15).';
