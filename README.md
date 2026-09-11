# Projeto Sessão - Sistema de Gestão para Clínicas de Fisioterapia

## 📌 Sobre o Projeto

O **Sessão** é um sistema completo para gestão de clínicas de fisioterapia, desenvolvido para resolver problemas como:
- Conflitos de agenda
- Controle de validade de pacotes
- Bloqueio de glosas em faturamentos de convênios sem evolução clínica

## 🎯 Regras de Negócio Implementadas

| **RN** | **Descrição** |
|--------|---------------|
| RN-01 | Pacote de 10 sessões expira 90 dias após a data de compra |
| RN-02 | Falta sem aviso com antecedência de 24h consome uma sessão do pacote |
| RN-03 | Falta avisada com 24h ou mais de antecedência não consome sessão |
| RN-04 | Uma sala não pode receber mais sessões simultâneas do que sua capacidade cadastrada |
| RN-05 | Um profissional não pode ter duas sessões no mesmo horário (mesmo em salas diferentes) |
| RN-06 | Sessão de convênio só pode ser faturada se tiver evolução clínica registrada |
| RN-07 | Paciente particular com pacote expirado ou saldo zerado não pode ser agendado |
| RN-08 | Atraso superior a 15 min registra atendimento reduzido (desconta do pacote, mas bloqueia faturamento no convênio) |

## 📁 Estrutura do Projeto

```
Projeto-Fisio/
├── sql/                          # Scripts SQL (PostgreSQL)
│   ├── 01_ddl_schema.sql          # Esquema do banco (3FN)
│   ├── 02_seed_data.sql           # Carga inicial de dados
│   └── 03_sanitizacao_inconsistencias.sql  # Lógica de sanitização
│
└── python/                       # Código Python
    ├── __init__.py
    ├── maquina_estados.py         # Máquina de estados da Sessão
    ├── pacotes_controller.py      # Regra temporal de pacotes
    └── testes.py                  # Suíte de 22 testes
```

## 🚀 Como Baixar e Abrir o Projeto

### 1️⃣ Clonar o Repositório

```bash
# Abra o terminal e execute:
git clone https://github.com/lucasoficial0426-tech/Projeto-Fisio.git
cd Projeto-Fisio
```

### 2️⃣ Abrir no VS Code

```bash
# Instale o VS Code (se ainda não tiver):
# Windows: https://code.visualstudio.com/download
# Linux (Debian/Ubuntu): sudo apt install code
# Mac: brew install --cask visual-studio-code

# Abra o projeto no VS Code:
code .
```

### 3️⃣ Instalar Dependências (Opcional - para executar testes)

```bash
# Crie um ambiente virtual (recomendado):
python -m venv venv

# Ative o ambiente virtual:
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências (se houver):
pip install -r requirements.txt  # (se existir)
```

## 🔧 Como Executar os Testes

### Executar Todos os Testes

```bash
python python/testes.py
```

**Resultado esperado**:
```
Ran 22 tests in 0.001s
OK

======================================================================
RESUMO DOS TESTES
======================================================================
Total de testes: 22
Sucesso: 22
Falhas: 0
Erros: 0

✓ TODOS OS TESTES PASSARAM!
```

### Executar Testes Individuais

```bash
# Executar apenas o Caso 1 (Capacidade da sala)
python -m unittest python.testes.TestCaso1

# Executar apenas o Caso 4 (Falta sem aviso)
python -m unittest python.testes.TestCaso4

# Executar apenas os testes de regra temporal
python -m unittest python.testes.TestRegraTemporal
```

## 🗃️ Como Usar os Scripts SQL (PostgreSQL)

### Pré-requisitos
- PostgreSQL instalado
- Usuário com permissão para criar bancos

### 1. Criar o Banco de Dados

```bash
# Acesse o PostgreSQL
sudo -u postgres psql

# Crie o banco
CREATE DATABASE fisio;

# Conecte-se ao banco
\c fisio

# Execute o esquema
\i sql/01_ddl_schema.sql

# Carregue os dados
\i sql/02_seed_data.sql

# (Opcional) Execute a sanitização
\i sql/03_sanitizacao_inconsistencias.sql
```

### 2. Sanitização de Inconsistências

O sistema automaticamente identifica e bloqueia:
- Pacientes com CPF duplicado
- Pacotes expirados ou com saldo zerado
- Sessões com pacotes bloqueados
- Sessões de convênio faturadas sem evolução

Para executar a sanitização manualmente:

```sql
-- No PostgreSQL, execute:
CALL fisio.sanitizar_banco();

-- Ou execute a função completa:
SELECT * FROM fisio.executar_sanitizacao_completa();
```

### 3. Consultas Úteis

```sql
-- Ver pacientes
SELECT * FROM fisio.paciente;

-- Ver profissionais
SELECT * FROM fisio.profissional;

-- Ver salas
SELECT * FROM fisio.sala;

-- Ver pacotes
SELECT * FROM fisio.pacote;

-- Ver sessões
SELECT * FROM fisio.sessao;

-- Ver inconsistências bloqueadas
SELECT * FROM fisio.vw_inconsistencias;

-- Ver pacotes bloqueados
SELECT * FROM fisio.vw_pacotes_bloqueados;

-- Ver sessões bloqueadas
SELECT * FROM fisio.vw_sessoes_bloqueadas;
```

## 📊 Dados Iniciais do Projeto

### Salas
| ID | Nome | Capacidade |
|----|------|------------|
| 1 | Sala 1 | 1 |
| 2 | Sala 2 | 1 |
| 3 | Sala 3 - Pilates | 3 |

### Profissionais
| ID | Nome | Tipo | CPF |
|----|------|------|------|
| 1 | Helena Kobayashi | Sócio | 123.456.789-09 |
| 2 | Diego Martins | Contratado | 987.654.321-00 |
| 3 | Sabrina Luz | Contratada | 456.789.123-01 |

### Pacientes
| ID | Nome | Tipo | Convênio | CPF |
|----|------|------|----------|------|
| 1 | Marta Siqueira | Particular | - | 111.111.111-11 |
| 2 | Ricardo Tavares | Particular | - | 222.222.222-22 |
| 3 | José Anselmo Reis | Convênio | SaúdeMais | 333.333.333-33 |
| 4 | Carla Bonatto | Convênio | UniPlano | 444.444.444-44 |

### Pacotes
| ID | Paciente | Data Compra | Sessões | Usadas | Validade (dias) | Status |
|----|----------|-------------|---------|--------|----------------|--------|
| 1 | Marta Siqueira | 12/08/2026 | 10 | 7 | 90 | Ativo |
| 2 | Marta Siqueira | 20/05/2026 | 10 | 10 | 90 | **Bloqueado** (expirado) |
| 3 | Ricardo Tavares | 05/09/2026 | 10 | 1 | 90 | Ativo |

### Convênios
| ID | Nome | CNPJ |
|----|------|------|
| 1 | SaúdeMais | 12.345.678/0001-01 |
| 2 | UniPlano | 98.765.432/0001-02 |

## 🎯 Máquina de Estados da Sessão

### Fluxo Principal
```
Agendada → Realizada → Evoluída → Faturada
```

### Fluxos Alternativos
```
Agendada → Cancelada com aviso (se aviso ≥24h)
Agendada → Falta sem aviso (consome sessão)
Agendada/Realizada → Atendimento reduzido (atraso >15 min)
```

### Transições Proibidas
- ❌ `Realizada → Faturada` (obrigatório passar por Evoluída - RN-06)
- ❌ `Falta sem aviso → Realizada` (passado não pode ser reescrito)
- ❌ `Atendimento reduzido → Faturada` (RN-08)

## 📅 Regra Temporal de Pacotes

### Antes de 01/11/2026
- **Pacotes**: 10 sessões
- **Validade**: 90 dias

### A partir de 01/11/2026
- **Pacotes**: 15 sessões
- **Validade**: 120 dias

### Exemplo de Uso

```python
from pacotes_controller import PacotesController
from datetime import date

controller = PacotesController()

# Criar pacote antes de 01/11/2026
pacote_antigo = controller.criar_pacote(
    paciente_id=1,
    data_compra=date(2026, 10, 15),
    quantidade_sessoes=10,
    validade_dias=90
)

# Criar pacote a partir de 01/11/2026
pacote_novo = controller.criar_pacote(
    paciente_id=2,
    data_compra=date(2026, 11, 1),
    quantidade_sessoes=15,
    validade_dias=120
)
```

## 🧪 10 Casos de Teste Oficiais

| **Caso** | **Descrição** | **RN** | **Resultado** |
|----------|---------------|--------|---------------|
| 1 | Sala 3 com 3 sessões → Agendar 4ª → **Recusar** | RN-04 | ✅ |
| 2 | Sabrina tem sessão → Agendar Sabrina em outra sala → **Recusar** | RN-05 | ✅ |
| 3 | Sala 3 com 2 sessões → Agendar 3ª → **Aceitar** | RN-04 | ✅ |
| 4 | Marta (3 sessões no P-01) → Falta sem aviso → Saldo **cai para 2** | RN-02 | ✅ |
| 5 | Marta (3 sessões no P-01) → Cancelar com 48h → Saldo **permanece 3** | RN-03 | ✅ |
| 6 | Pacote P-02 (expirado) → Agendar → **Recusar** | RN-01, RN-07 | ✅ |
| 7 | José (sessão sem evolução) → Faturar → **Bloquear** | RN-06 | ✅ |
| 8 | José (sessão com evolução) → Faturar → **Aceitar** | RN-06 | ✅ |
| 9 | Carla (20 min atrasada) → Atendimento reduzido → **Bloquear faturamento** | RN-08 | ✅ |
| 10 | Relatório de ocupação de setembro → **Exibir taxa por sala/profissional** | - | ✅ |

## 🛠️ Tecnologias Utilizadas

- **Banco de Dados**: PostgreSQL
- **Linguagem**: Python 3.12+
- **Testes**: `unittest` (padrão Python)
- **Versionamento**: Git / GitHub

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📜 Licença

MIT License - Sinta-se à vontade para usar e modificar o código.

## 📞 Suporte

Para dúvidas ou problemas, abra uma **Issue** no repositório:
[https://github.com/lucasoficial0426-tech/Projeto-Fisio/issues](https://github.com/lucasoficial0426-tech/Projeto-Fisio/issues)
