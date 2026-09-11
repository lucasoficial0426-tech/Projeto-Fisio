-- ============================================
-- SISTEMA "SESSÃO" - CLÍNICAS DE FISIOTERAPIA
-- DDL SQL (PostgreSQL) - Modelagem em 3FN
-- Regras de Negócio: RN-01 a RN-08
-- ============================================

-- ============================================
-- SEÇÃO 1: TABELAS DE DOMÍNIO (ENUMS E AUXILIARES)
-- ============================================

-- Tipo de pagamento do pacote
CREATE TYPE tipo_pagamento AS ENUM ('CONVENIO', 'PARTICULAR');

-- Status do pacote
CREATE TYPE status_pacote AS ENUM ('ATIVO', 'EXPIRADO', 'UTILIZADO');

-- Status da sessão
CREATE TYPE status_sessao AS ENUM (
    'AGENDADO',    -- Agendado, aguardando confirmação
    'CONFIRMADO',  -- Confirmado pelo paciente
    'REALIZADO',   -- Sessão realizada
    'CANCELADO',   -- Cancelado com antecedência
    'FALTA',       -- Paciente não compareceu
    'ATRASADO'     -- Atraso superior a 15 min (RN-08)
);

-- Tipo de atendimento (para RN-08)
CREATE TYPE tipo_atendimento AS ENUM ('NORMAL', 'REDUZIDO');

-- Status da fatura
CREATE TYPE status_fatura AS ENUM (
    'PENDENTE',   -- Aguardando processamento
    'FATURADO',    -- Faturado com sucesso
    'BLOQUEADO'    -- Bloqueado por falta de evolução (RN-06) ou atendimento reduzido (RN-08)
);

-- Status do lote
CREATE TYPE status_lote AS ENUM ('ABERTO', 'FECHADO', 'FATURADO');


-- ============================================
-- SEÇÃO 2: TABELAS PRINCIPAIS (ENTIDADES)
-- ============================================

-- Tabela: Convenio
-- Descrição: Convênios médicos parceiros da clínica
CREATE TABLE Convenio (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    endereco TEXT NOT NULL,
    taxa_desconto DECIMAL(5, 2) NOT NULL DEFAULT 0.00 CHECK (taxa_desconto >= 0 AND taxa_desconto <= 100),
    data_contrato DATE NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabela: Paciente
-- Descrição: Pacientes da clínica (particulares ou de convênio)
CREATE TABLE Paciente (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    data_nascimento DATE NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    endereco TEXT NOT NULL,
    convenio_id INT REFERENCES Convenio(id) ON DELETE SET NULL,
    data_cadastro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabela: Profissional
-- Descrição: Fisioterapeutas e outros profissionais da clínica
CREATE TABLE Profissional (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL UNIQUE,
    crf VARCHAR(20) NOT NULL UNIQUE,  -- Conselho Regional de Fisioterapia
    especialidade VARCHAR(50) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    data_cadastro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabela: Sala
-- Descrição: Salas de atendimento com capacidade limitada (RN-04)
CREATE TABLE Sala (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    descricao TEXT,
    capacidade INT NOT NULL DEFAULT 1 CHECK (capacidade > 0),
    localizacao VARCHAR(50),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabela: Pacote
-- Descrição: Pacotes de sessões comprados por pacientes (RN-01, RN-07)
-- RN-01: Pacote de 10 sessões expira 90 dias após a data de compra
CREATE TABLE Pacote (
    id SERIAL PRIMARY KEY,
    paciente_id INT NOT NULL REFERENCES Paciente(id) ON DELETE CASCADE,
    data_compra DATE NOT NULL,
    data_expiracao DATE NOT NULL,
    sessao_total INT NOT NULL DEFAULT 10 CHECK (sessao_total > 0),
    sessao_restante INT NOT NULL DEFAULT 10 CHECK (sessao_restante >= 0),
    tipo_pagamento tipo_pagamento NOT NULL,
    valor DECIMAL(10, 2) NOT NULL CHECK (valor > 0),
    status status_pacote NOT NULL DEFAULT 'ATIVO',
    convenio_id INT REFERENCES Convenio(id) ON DELETE SET NULL,
    -- RN-01: Garante que a data de expiração é 90 dias após a compra
    CONSTRAINT chk_expiracao_90_dias 
        CHECK (data_expiracao = data_compra + INTERVAL '90 days'),
    -- Garante que sessao_restante nunca excede sessao_total
    CONSTRAINT chk_sessao_restante_valida 
        CHECK (sessao_restante <= sessao_total)
);

-- Tabela: Sessao
-- Descrição: Agendamentos de sessões de fisioterapia (RN-02 a RN-08)
CREATE TABLE Sessao (
    id SERIAL PRIMARY KEY,
    paciente_id INT NOT NULL REFERENCES Paciente(id) ON DELETE CASCADE,
    profissional_id INT NOT NULL REFERENCES Profissional(id) ON DELETE CASCADE,
    sala_id INT NOT NULL REFERENCES Sala(id) ON DELETE CASCADE,
    pacote_id INT REFERENCES Pacote(id) ON DELETE SET NULL,
    convenio_id INT REFERENCES Convenio(id) ON DELETE SET NULL,
    data_hora_inicio TIMESTAMP NOT NULL,
    data_hora_fim TIMESTAMP NOT NULL,
    status status_sessao NOT NULL DEFAULT 'AGENDADO',
    tipo_atendimento tipo_atendimento NOT NULL DEFAULT 'NORMAL',
    observacoes TEXT,
    data_agendamento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- RN-08: Atraso superior a 15 min registra atendimento reduzido
    atraso_minutos INT DEFAULT 0 CHECK (atraso_minutos >= 0),
    -- Garante que data_hora_fim > data_hora_inicio
    CONSTRAINT chk_horario_valido 
        CHECK (data_hora_fim > data_hora_inicio),
    -- Garante que tipo_atendimento = REDUZIDO se atraso > 15 min (RN-08)
    CONSTRAINT chk_atendimento_reduzido 
        CHECK (atraso_minutos <= 15 OR tipo_atendimento = 'REDUZIDO')
);

-- Tabela: EvolucaoClinica
-- Descrição: Registros de evolução clínica para faturamento (RN-06)
-- RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica registrada
CREATE TABLE EvolucaoClinica (
    id SERIAL PRIMARY KEY,
    sessao_id INT NOT NULL REFERENCES Sessao(id) ON DELETE CASCADE,
    profissional_id INT NOT NULL REFERENCES Profissional(id) ON DELETE CASCADE,
    data_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descricao TEXT NOT NULL,
    objetivos TEXT,
    conduta TEXT,
    -- Garante que cada sessão de convênio tem no máximo uma evolução
    CONSTRAINT chk_evolucao_unica_por_sessao 
        UNIQUE (sessao_id)
);

-- Tabela: Falta
-- Descrição: Registro de faltas (RN-02, RN-03)
-- RN-02: Falta sem aviso com antecedência de 24h consome uma sessão do pacote
-- RN-03: Falta avisada com 24h ou mais de antecedência não consome sessão
CREATE TABLE Falta (
    id SERIAL PRIMARY KEY,
    sessao_id INT NOT NULL REFERENCES Sessao(id) ON DELETE CASCADE,
    data_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    avisado BOOLEAN NOT NULL DEFAULT FALSE,  -- Se foi avisado com antecedência
    antecedencia_horas DECIMAL(5, 2) NOT NULL DEFAULT 0 CHECK (antecedencia_horas >= 0),
    justificativa TEXT,
    -- RN-02 e RN-03: Apenas uma falta por sessão
    CONSTRAINT chk_falta_unica_por_sessao 
        UNIQUE (sessao_id)
);

-- Tabela: Lote
-- Descrição: Lotes de faturamento para convênios
CREATE TABLE Lote (
    id SERIAL PRIMARY KEY,
    convenio_id INT NOT NULL REFERENCES Convenio(id) ON DELETE CASCADE,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_fechamento TIMESTAMP,
    data_faturamento TIMESTAMP,
    status status_lote NOT NULL DEFAULT 'ABERTO',
    valor_total DECIMAL(12, 2) NOT NULL DEFAULT 0.00 CHECK (valor_total >= 0),
    observacoes TEXT
);

-- Tabela: Fatura
-- Descrição: Faturamento individual por sessão (RN-06, RN-08)
-- RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica
-- RN-08: Atraso superior a 15 min bloqueia faturamento no convênio
CREATE TABLE Fatura (
    id SERIAL PRIMARY KEY,
    sessao_id INT NOT NULL REFERENCES Sessao(id) ON DELETE CASCADE,
    lote_id INT NOT NULL REFERENCES Lote(id) ON DELETE CASCADE,
    convenio_id INT NOT NULL REFERENCES Convenio(id) ON DELETE CASCADE,
    valor DECIMAL(10, 2) NOT NULL CHECK (valor > 0),
    data_faturamento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status status_fatura NOT NULL DEFAULT 'PENDENTE',
    observacoes TEXT,
    -- RN-06: Garante que sessões de convênio sem evolução não podem ser faturadas
    CONSTRAINT chk_evolucao_obrigatoria 
        FOREIGN KEY (sessao_id) REFERENCES EvolucaoClinica(sessao_id),
    -- RN-08: Bloqueia faturamento se atendimento for reduzido
    CONSTRAINT chk_atendimento_reduzido_bloqueia_faturamento 
        CHECK (
            status != 'FATURADO' OR 
            (SELECT tipo_atendimento FROM Sessao WHERE id = sessao_id) != 'REDUZIDO'
        )
);


-- ============================================
-- SEÇÃO 3: ÍNDICES PARA PERFORMANCE
-- ============================================

-- Índices para consultas freqüentes
CREATE INDEX idx_paciente_cpf ON Paciente(cpf);
CREATE INDEX idx_paciente_convenio ON Paciente(convenio_id);
CREATE INDEX idx_profissional_cpf ON Profissional(cpf);
CREATE INDEX idx_profissional_crf ON Profissional(crf);
CREATE INDEX idx_pacote_paciente ON Pacote(paciente_id);
CREATE INDEX idx_pacote_data_expiracao ON Pacote(data_expiracao);
CREATE INDEX idx_pacote_status ON Pacote(status);

-- Índices para agendamento (consultas por data/hora)
CREATE INDEX idx_sessao_data_hora ON Sessao(data_hora_inicio, data_hora_fim);
CREATE INDEX idx_sessao_profissional ON Sessao(profissional_id, data_hora_inicio);
CREATE INDEX idx_sessao_sala ON Sessao(sala_id, data_hora_inicio);
CREATE INDEX idx_sessao_paciente ON Sessao(paciente_id, data_hora_inicio);
CREATE INDEX idx_sessao_status ON Sessao(status);

-- Índices para faturamento
CREATE INDEX idx_fatura_lote ON Fatura(lote_id);
CREATE INDEX idx_fatura_sessao ON Fatura(sessao_id);
CREATE INDEX idx_fatura_status ON Fatura(status);
CREATE INDEX idx_lote_convenio ON Lote(convenio_id);
CREATE INDEX idx_lote_status ON Lote(status);


-- ============================================
-- SEÇÃO 4: TRIGGERS PARA REGRAS DE NEGÓCIO
-- ============================================

-- Função para atualizar status do pacote (RN-01)
CREATE OR REPLACE FUNCTION atualizar_status_pacote()
RETURNS TRIGGER AS $$
BEGIN
    -- RN-01: Pacote expira 90 dias após a compra
    IF NEW.data_expiracao < CURRENT_DATE THEN
        NEW.status := 'EXPIRADO';
    ELSIF NEW.sessao_restante = 0 THEN
        NEW.status := 'UTILIZADO';
    ELSE
        NEW.status := 'ATIVO';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar status do pacote antes de inserir ou atualizar
CREATE TRIGGER trg_pacote_status_before_insert
    BEFORE INSERT OR UPDATE ON Pacote
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_status_pacote();


-- Função para validar agendamento (RN-04, RN-05, RN-07)
CREATE OR REPLACE FUNCTION validar_agendamento()
RETURNS TRIGGER AS $$
DECLARE
    conflito_sala INT;
    conflito_profissional INT;
    pacote_valido BOOLEAN;
BEGIN
    -- RN-07: Paciente particular com pacote expirado ou saldo zerado não pode ser agendado
    IF NEW.tipo_atendimento = 'NORMAL' AND NEW.pacote_id IS NOT NULL THEN
        SELECT 
            (p.data_expiracao >= CURRENT_DATE AND p.sessao_restante > 0) 
        INTO pacote_valido
        FROM Pacote p 
        WHERE p.id = NEW.pacote_id AND p.tipo_pagamento = 'PARTICULAR';
        
        IF NOT pacote_valido THEN
            RAISE EXCEPTION 'RN-07: Paciente particular com pacote expirado ou saldo zerado não pode ser agendado';
        END IF;
    END IF;
    
    -- RN-04: Uma sala não pode receber mais sessões simultâneas do que sua capacidade
    SELECT COUNT(*) 
    INTO conflito_sala
    FROM Sessao s
    WHERE s.sala_id = NEW.sala_id 
      AND s.id != NEW.id 
      AND (
          (NEW.data_hora_inicio BETWEEN s.data_hora_inicio AND s.data_hora_fim) OR
          (NEW.data_hora_fim BETWEEN s.data_hora_inicio AND s.data_hora_fim) OR
          (s.data_hora_inicio BETWEEN NEW.data_hora_inicio AND NEW.data_hora_fim)
      );
    
    IF conflito_sala >= (SELECT capacidade FROM Sala WHERE id = NEW.sala_id) THEN
        RAISE EXCEPTION 'RN-04: Sala não pode receber mais sessões simultâneas do que sua capacidade';
    END IF;
    
    -- RN-05: Um profissional não pode ter duas sessões no mesmo horário
    SELECT COUNT(*) 
    INTO conflito_profissional
    FROM Sessao s
    WHERE s.profissional_id = NEW.profissional_id 
      AND s.id != NEW.id 
      AND (
          (NEW.data_hora_inicio BETWEEN s.data_hora_inicio AND s.data_hora_fim) OR
          (NEW.data_hora_fim BETWEEN s.data_hora_inicio AND s.data_hora_fim) OR
          (s.data_hora_inicio BETWEEN NEW.data_hora_inicio AND NEW.data_hora_fim)
      );
    
    IF conflito_profissional > 0 THEN
        RAISE EXCEPTION 'RN-05: Profissional não pode ter duas sessões no mesmo horário';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para validar agendamento antes de inserir ou atualizar
CREATE TRIGGER trg_sessao_validar_agendamento
    BEFORE INSERT OR UPDATE ON Sessao
    FOR EACH ROW
    EXECUTE FUNCTION validar_agendamento();


-- Função para registrar falta e atualizar pacote (RN-02, RN-03)
CREATE OR REPLACE FUNCTION registrar_falta_e_atualizar_pacote()
RETURNS TRIGGER AS $$
BEGIN
    -- RN-02: Falta sem aviso com antecedência de 24h consome uma sessão do pacote
    -- RN-03: Falta avisada com 24h ou mais de antecedência não consome sessão
    IF NEW.avisado = FALSE AND NEW.antecedencia_horas < 24 THEN
        -- Consome uma sessão do pacote
        UPDATE Pacote 
        SET sessao_restante = sessao_restante - 1
        WHERE id = (SELECT pacote_id FROM Sessao WHERE id = NEW.sessao_id);
        
        -- Atualiza status da sessão para FALTA
        UPDATE Sessao 
        SET status = 'FALTA'
        WHERE id = NEW.sessao_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para registrar falta e atualizar pacote
CREATE TRIGGER trg_falta_registrar
    AFTER INSERT ON Falta
    FOR EACH ROW
    EXECUTE FUNCTION registrar_falta_e_atualizar_pacote();


-- Função para bloquear faturamento sem evolução (RN-06)
CREATE OR REPLACE FUNCTION validar_faturamento()
RETURNS TRIGGER AS $$
DECLARE
    tem_evolucao BOOLEAN;
    atendimento_reduzido BOOLEAN;
BEGIN
    -- RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica
    SELECT EXISTS(
        SELECT 1 FROM EvolucaoClinica WHERE sessao_id = NEW.sessao_id
    ) INTO tem_evolucao;
    
    -- RN-08: Atraso superior a 15 min bloqueia faturamento no convênio
    SELECT (atraso_minutos > 15) INTO atendimento_reduzido
    FROM Sessao WHERE id = NEW.sessao_id;
    
    IF NOT tem_evolucao OR atendimento_reduzido THEN
        NEW.status := 'BLOQUEADO';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para validar faturamento antes de inserir
CREATE TRIGGER trg_fatura_validar
    BEFORE INSERT OR UPDATE ON Fatura
    FOR EACH ROW
    EXECUTE FUNCTION validar_faturamento();


-- ============================================
-- SEÇÃO 5: VIEWS PARA RELATÓRIOS
-- ============================================

-- View para relatório de ocupação (Tela: Relatório de Ocupação)
CREATE VIEW vw_ocupacao_salas AS
SELECT 
    s.id AS sala_id,
    s.nome AS sala_nome,
    s.capacidade,
    DATE(sessao.data_hora_inicio) AS data,
    EXTRACT(HOUR FROM sessao.data_hora_inicio) AS hora,
    COUNT(sessao.id) AS qtd_sessoes,
    (COUNT(sessao.id) * 100.0 / s.capacidade) AS percentual_ocupacao
FROM Sala s
LEFT JOIN Sessao sessao ON s.id = sessao.sala_id 
    AND sessao.status IN ('AGENDADO', 'CONFIRMADO', 'REALIZADO')
GROUP BY s.id, s.nome, s.capacidade, DATE(sessao.data_hora_inicio), EXTRACT(HOUR FROM sessao.data_hora_inicio)
ORDER BY data, hora, s.id;


-- View para pacotes próximos de expirar (RN-01)
CREATE VIEW vw_pacotes_proximos_expirar AS
SELECT 
    p.id AS pacote_id,
    paciente.id AS paciente_id,
    paciente.nome AS paciente_nome,
    p.data_compra,
    p.data_expiracao,
    p.sessao_total,
    p.sessao_restante,
    p.status,
    (p.data_expiracao - CURRENT_DATE) AS dias_restantes
FROM Pacote p
JOIN Paciente paciente ON p.paciente_id = paciente.id
WHERE p.status = 'ATIVO' 
  AND p.data_expiracao BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '30 days')
ORDER BY p.data_expiracao;


-- View para sessões sem evolução clínica (RN-06)
CREATE VIEW vw_sessoes_sem_evolucao AS
SELECT 
    s.id AS sessao_id,
    paciente.nome AS paciente_nome,
    profissional.nome AS profissional_nome,
    s.data_hora_inicio,
    s.status,
    s.tipo_atendimento,
    s.atraso_minutos
FROM Sessao s
JOIN Paciente paciente ON s.paciente_id = paciente.id
JOIN Profissional profissional ON s.profissional_id = profissional.id
LEFT JOIN EvolucaoClinica ec ON s.id = ec.sessao_id
WHERE ec.sessao_id IS NULL 
  AND s.convenio_id IS NOT NULL 
  AND s.status = 'REALIZADO'
ORDER BY s.data_hora_inicio;


-- ============================================
-- SEÇÃO 6: DADOS INICIAIS (OPCIONAL)
-- ============================================

-- Inserir dados iniciais para testes (opcional)
-- DESCOMENTAR PARA USAR

/*
-- Convênios
INSERT INTO Convenio (nome, cnpj, telefone, email, endereco, data_contrato) VALUES
('Unimed', '00.000.000/0001-00', '(11) 1234-5678', 'unimed@email.com', 'Rua A, 123', '2023-01-01'),
('Amil', '00.000.000/0002-00', '(11) 8765-4321', 'amil@email.com', 'Rua B, 456', '2023-01-01');

-- Profissionais
INSERT INTO Profissional (nome, cpf, crf, especialidade, telefone, email) VALUES
('Dr. João Silva', '123.456.789-00', 'CRF-12345', 'Fisioterapia Ortopédica', '(11) 1111-1111', 'joao@email.com'),
('Dra. Maria Santos', '987.654.321-00', 'CRF-67890', 'Fisioterapia Neurológica', '(11) 2222-2222', 'maria@email.com');

-- Salas
INSERT INTO Sala (nome, descricao, capacidade, localizacao) VALUES
('Sala 1', 'Sala de atendimento individual', 1, 'Andar 1'),
('Sala 2', 'Sala de atendimento em grupo', 3, 'Andar 1'),
('Sala 3', 'Sala de avaliação', 1, 'Andar 2');

-- Pacientes
INSERT INTO Paciente (nome, cpf, data_nascimento, telefone, email, endereco, convenio_id) VALUES
('Carlos Souza', '111.111.111-11', '1980-01-01', '(11) 3333-3333', 'carlos@email.com', 'Rua C, 789', 1),
('Ana Oliveira', '222.222.222-22', '1990-05-15', '(11) 4444-4444', 'ana@email.com', 'Rua D, 101', NULL);

-- Pacotes
INSERT INTO Pacote (paciente_id, data_compra, data_expiracao, sessao_total, sessao_restante, tipo_pagamento, valor, convenio_id) VALUES
(1, '2023-09-01', '2023-11-30', 10, 10, 'CONVENIO', 500.00, 1),
(2, '2023-09-01', '2023-11-30', 10, 8, 'PARTICULAR', 600.00, NULL);
*/

-- ============================================
-- FIM DO DDL
-- ============================================
