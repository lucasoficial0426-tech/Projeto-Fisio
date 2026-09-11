# 🏗️ **ARQUITETURA DE TELAS - SISTEMA SESSÃO**

## **Visão Geral**

O sistema **Sessão** para clínicas de fisioterapia possui **7 telas obrigatórias** que cobrem todo o fluxo de trabalho, desde o cadastro de pacientes até o faturamento de convênios. Cada tela é projetada para validar as **Regras de Negócio (RN-01 a RN-08)** e garantir a integridade dos dados.

---

## **📋 Estrutura de Arquivos**

```
frontend/src/
├── pages/                          # Telas principais
│   ├── CadastroPacientes/          # Tela 1: Cadastro de Pacientes
│   │   ├── index.jsx              # Componente principal
│   │   ├── PacienteForm.jsx       # Formulário de paciente
│   │   └── PacienteList.jsx       # Lista de pacientes
│   │
│   ├── CadastroProfissionais/     # Tela 2: Cadastro de Profissionais/Salas
│   │   ├── index.jsx
│   │   ├── ProfissionalForm.jsx
│   │   ├── ProfissionalList.jsx
│   │   ├── SalaForm.jsx
│   │   └── SalaList.jsx
│   │
│   ├── VendaPacotes/              # Tela 3: Venda de Pacotes
│   │   ├── index.jsx
│   │   ├── PacoteForm.jsx
│   │   └── PacoteList.jsx
│   │
│   ├── Agenda/                    # Tela 4: Agenda
│   │   ├── index.jsx
│   │   ├── Calendario.jsx         # Calendário interativo
│   │   ├── AgendamentoModal.jsx   # Modal de agendamento
│   │   └── ConflitoAlert.jsx     # Alertas de conflito (RN-04, RN-05)
│   │
│   ├── Atendimento/              # Tela 5: Atendimento
│   │   ├── index.jsx
│   │   ├── SessaoDetalhes.jsx     # Detalhes da sessão
│   │   ├── EvolucaoForm.jsx      # Formulário de evolução clínica (RN-06)
│   │   └── AtrasoAlert.jsx       # Alerta de atraso (RN-08)
│   │
│   ├── LoteConvenio/              # Tela 6: Lote de Convênio
│   │   ├── index.jsx
│   │   ├── LoteForm.jsx
│   │   ├── LoteList.jsx
│   │   └── FaturamentoModal.jsx   # Modal de faturamento
│   │
│   └── RelatorioOcupacao/         # Tela 7: Relatório de Ocupação
│       ├── index.jsx
│       ├── OcupacaoChart.jsx      # Gráfico de ocupação
│       └── Filtros.jsx           # Filtros por data/sala
│
├── components/                    # Componentes reutilizáveis
│   ├── Layout/                   # Layout base
│   │   ├── Header.jsx
│   │   ├── Sidebar.jsx
│   │   └── Footer.jsx
│   │
│   ├── Common/                   # Componentes comuns
│   │   ├── Table.jsx            # Tabela genérica
│   │   ├── Modal.jsx            # Modal genérico
│   │   ├── Button.jsx           # Botões padronizados
│   │   ├── Input.jsx            # Inputs padronizados
│   │   ├── Select.jsx           # Select padronizado
│   │   └── Alert.jsx            # Alertas
│   │
│   └── Validation/              # Validações
│       ├── PacoteValidator.jsx   # Valida RN-01, RN-07
│       ├── SessaoValidator.jsx   # Valida RN-04, RN-05, RN-08
│       └── FaturamentoValidator.jsx # Valida RN-06
│
├── services/                     # Serviços de API
│   ├── api.js                   # Configuração do axios
│   ├── paciente_service.js
│   ├── profissional_service.js
│   ├── sala_service.js
│   ├── convenio_service.js
│   ├── pacote_service.js
│   ├── sessao_service.js
│   ├── evolucao_clinica_service.js
│   ├── falta_service.js
│   └── fatura_service.js
│
├── utils/                        # Utilitários
│   ├── dateUtils.js             # Funções de data/hora
│   ├── validationUtils.js       # Funções de validação
│   └── constants.js             # Constantes do sistema
│
└── styles/                      # Estilos
    ├── global.css               # Estilos globais
    └── theme.js                 # Tema do sistema
```

---

## **🎯 Detalhamento das 7 Telas Obrigatórias**

---

### **📄 Tela 1: Cadastro de Pacientes**
**Caminho:** `/pages/CadastroPacientes/`

#### **Componentes:**
1. **`index.jsx`** - Componente principal
   - Gerencia o estado global da tela
   - Navegação entre lista e formulário

2. **`PacienteForm.jsx`** - Formulário de cadastro/edição
   - Campos: Nome, CPF, Data de Nascimento, Telefone, Email, Endereço, Convênio
   - Validações:
     - CPF único
     - Formato de telefone/email
     - Data de nascimento válida
   - Ações:
     - `POST /api/pacientes/` - Criar paciente
     - `PUT /api/pacientes/{id}` - Atualizar paciente

3. **`PacienteList.jsx`** - Lista de pacientes
   - Tabela com paginação
   - Filtros: Nome, CPF, Convênio, Status
   - Ações:
     - Editar paciente
     - Visualizar detalhes
     - Desativar paciente

#### **Fluxo de Dados:**
```
PacienteForm → (submit) → PacienteService.create() → API → Banco de Dados
PacienteList → (load) → PacienteService.getAll() → API → Exibe tabela
```

#### **Regras de Negócio Relacionadas:**
- **RN-07**: Filtro para pacientes com pacotes ativos (exibir alerta se pacote expirado)

---

### **📄 Tela 2: Cadastro de Profissionais/Salas**
**Caminho:** `/pages/CadastroProfissionais/`

#### **Componentes:**
1. **`index.jsx`** - Componente principal com abas
   - Abas: Profissionais | Salas

2. **`ProfissionalForm.jsx`** - Formulário de profissional
   - Campos: Nome, CPF, CRF, Especialidade, Telefone, Email
   - Validações:
     - CPF único
     - CRF único
     - Formato de contato

3. **`SalaForm.jsx`** - Formulário de sala
   - Campos: Nome, Descrição, Capacidade, Localização
   - Validações:
     - Capacidade > 0 (RN-04)

4. **`ProfissionalList.jsx`** e **`SalaList.jsx`** - Listas
   - Tabelas com paginação
   - Ações: Editar, Desativar

#### **Fluxo de Dados:**
```
ProfissionalForm → ProfissionalService.create() → API
SalaForm → SalaService.create() → API
```

#### **Regras de Negócio Relacionadas:**
- **RN-04**: Capacidade da sala deve ser > 0
- **RN-05**: CRF único para evitar duplicidade de profissionais

---

### **📄 Tela 3: Venda de Pacotes**
**Caminho:** `/pages/VendaPacotes/`

#### **Componentes:**
1. **`index.jsx`** - Componente principal

2. **`PacoteForm.jsx`** - Formulário de venda de pacote
   - Campos:
     - Paciente (select com busca)
     - Tipo de Pagamento (CONVÊNIO / PARTICULAR)
     - Convênio (se tipo = CONVÊNIO)
     - Data de Compra (default: hoje)
     - Quantidade de Sessões (default: 10)
     - Valor
   - Validações:
     - Paciente deve existir
     - Data de expiração automática (90 dias após compra - **RN-01**)
     - Valor > 0

3. **`PacoteList.jsx`** - Lista de pacotes
   - Tabela com filtros: Paciente, Tipo, Status, Data de Expiração
   - Ações: Visualizar, Editar

#### **Fluxo de Dados:**
```
PacoteForm → PacoteService.create() → API
  ↓
  Data Expiração = Data Compra + 90 dias (RN-01)
```

#### **Regras de Negócio Relacionadas:**
- **RN-01**: Pacote expira 90 dias após a compra
- **RN-07**: Pacientes particulares com pacote expirado não podem ser agendados

---

### **📄 Tela 4: Agenda**
**Caminho:** `/pages/Agenda/`

#### **Componentes:**
1. **`index.jsx`** - Componente principal
   - Gerencia estado do calendário e modais

2. **`Calendario.jsx`** - Calendário interativo
   - Exibe dias com sessões agendadas
   - Navegação por mês
   - Seleção de data

3. **`AgendamentoModal.jsx`** - Modal de agendamento
   - Campos:
     - Paciente (select com filtro de pacotes ativos - **RN-07**)
     - Profissional (select com validação de disponibilidade - **RN-05**)
     - Sala (select com validação de capacidade - **RN-04**)
     - Data/Hora Início e Fim
     - Observações
   - Validações em tempo real:
     - Verificar conflitos de sala (RN-04)
     - Verificar conflitos de profissional (RN-05)
     - Verificar pacote do paciente (RN-07)

4. **`ConflitoAlert.jsx`** - Alertas de conflito
   - Exibe mensagens de erro das RNs

#### **Fluxo de Dados:**
```
Calendario → (click dia) → AgendamentoModal
AgendamentoModal → (submit) → SessaoService.create() → API
  ↓
  Validações:
    - SalaService.verificar_capacidade_sala() (RN-04)
    - ProfissionalService.get_profissionais_disponiveis() (RN-05)
    - PacoteService.validar_pacote_para_agendamento() (RN-07)
```

#### **Regras de Negócio Relacionadas:**
- **RN-04**: Sala não pode ter mais sessões do que sua capacidade
- **RN-05**: Profissional não pode ter duas sessões no mesmo horário
- **RN-07**: Paciente particular com pacote expirado ou saldo zerado não pode ser agendado

---

### **📄 Tela 5: Atendimento**
**Caminho:** `/pages/Atendimento/`

#### **Componentes:**
1. **`index.jsx`** - Componente principal

2. **`SessaoDetalhes.jsx`** - Detalhes da sessão
   - Exibe: Paciente, Profissional, Sala, Horário, Status
   - Ações:
     - Confirmar sessão
     - Realizar sessão
     - Cancelar sessão
     - Registrar falta

3. **`EvolucaoForm.jsx`** - Formulário de evolução clínica
   - Campos: Descrição, Objetivos, Conduta
   - Validação: Obrigatório para sessões de convênio (**RN-06**)

4. **`AtrasoAlert.jsx`** - Alerta de atraso
   - Se atraso > 15 min, marca como atendimento reduzido (**RN-08**)

5. **`FaltaForm.jsx`** - Registro de falta
   - Campos: Avisado (sim/não), Antecedência (horas), Justificativa
   - Validações:
     - Se não avisado com 24h: consome sessão (**RN-02**)
     - Se avisado com 24h+: não consome sessão (**RN-03**)

#### **Fluxo de Dados:**
```
SessaoDetalhes → (realizar) → SessaoService.realizar_sessao() → API
EvolucaoForm → EvolucaoClinicaService.create() → API (RN-06)
FaltaForm → FaltaService.create() → API (RN-02, RN-03)
```

#### **Regras de Negócio Relacionadas:**
- **RN-02**: Falta sem aviso com 24h consome sessão
- **RN-03**: Falta avisada com 24h não consome sessão
- **RN-06**: Sessão de convênio só pode ser faturada com evolução clínica
- **RN-08**: Atraso > 15 min registra atendimento reduzido

---

### **📄 Tela 6: Lote de Convênio**
**Caminho:** `/pages/LoteConvenio/`

#### **Componentes:**
1. **`index.jsx`** - Componente principal

2. **`LoteForm.jsx`** - Formulário de lote
   - Campos: Convênio, Observações
   - Ações: Criar lote

3. **`LoteList.jsx`** - Lista de lotes
   - Tabela com status: ABERTO, FECHADO, FATURADO
   - Ações: Fechar lote, Faturar lote

4. **`FaturamentoModal.jsx`** - Modal de faturamento
   - Exibe sessões do lote que podem ser faturadas
   - Validações:
     - Somente sessões com evolução clínica (**RN-06**)
     - Somente sessões com atendimento normal (**RN-08**)
   - Ações:
     - Criar faturas para sessões selecionadas

#### **Fluxo de Dados:**
```
LoteList → (fechar) → LoteService.fechar_lote() → API
FaturamentoModal → FaturaService.create() → API (RN-06, RN-08)
```

#### **Regras de Negócio Relacionadas:**
- **RN-06**: Sessão de convênio só pode ser faturada com evolução clínica
- **RN-08**: Atraso > 15 min bloqueia faturamento

---

### **📄 Tela 7: Relatório de Ocupação**
**Caminho:** `/pages/RelatorioOcupacao/`

#### **Componentes:**
1. **`index.jsx`** - Componente principal

2. **`Filtros.jsx`** - Filtros do relatório
   - Período (data inicial/final)
   - Sala (opcional)
   - Profissional (opcional)

3. **`OcupacaoChart.jsx`** - Gráfico de ocupação
   - Tipo: Gráfico de barras ou calor
   - Eixo X: Dias/Horários
   - Eixo Y: Salas
   - Cor: Percentual de ocupação

4. **`OcupacaoTable.jsx`** - Tabela de ocupação
   - Colunas: Sala, Data, Hora, Sessões Agendadas, Capacidade, % Ocupação

#### **Fluxo de Dados:**
```
Filtros → (apply) → SessaoService.get_by_data() → API → Exibe gráfico/tabela
```

#### **Regras de Negócio Relacionadas:**
- **RN-04**: Exibe capacidade máxima de cada sala

---

## **🔄 Fluxos entre Telas**

### **Fluxo de Agendamento:**
```
Agenda (Calendario)
  ↓ (selecionar dia/horário)
AgendamentoModal
  ↓ (selecionar paciente)
  → PacienteService.getPacientesComPacotesAtivos() (RN-07)
  ↓ (selecionar profissional)
  → ProfissionalService.get_profissionais_disponiveis() (RN-05)
  ↓ (selecionar sala)
  → SalaService.verificar_capacidade_sala() (RN-04)
  ↓ (confirmar)
  → SessaoService.create() → API
```

### **Fluxo de Atendimento:**
```
Agenda (Sessão Agendada)
  ↓ (clicar na sessão)
Atendimento (SessaoDetalhes)
  ↓ (registrar evolução)
EvolucaoForm → EvolucaoClinicaService.create() (RN-06)
  ↓ (marcar como realizada)
SessaoService.realizar_sessao() → API
  ↓ (se convênio)
LoteConvenio → FaturamentoModal → FaturaService.create() (RN-06, RN-08)
```

### **Fluxo de Faturamento:**
```
LoteConvenio (LoteList)
  ↓ (selecionar lote ABERTO)
FaturamentoModal
  ↓ (carregar sessões)
  → SessaoService.get_sessoes_para_faturamento() (RN-06, RN-08)
  ↓ (selecionar sessões)
  → FaturaService.create() → API
  ↓ (faturar lote)
LoteService.faturar_lote() → API
```

---

## **🎨 Componentes Reutilizáveis**

### **1. `Layout/`**
- **`Header.jsx`**: Barra superior com logo, menu e usuário
- **`Sidebar.jsx`**: Menu lateral com navegação entre telas
- **`Footer.jsx`**: Rodapé com informações do sistema

### **2. `Common/`**
- **`Table.jsx`**: Tabela genérica com paginação, ordenação e filtros
- **`Modal.jsx`**: Modal genérico com header, body e footer
- **`Button.jsx`**: Botões padronizados (primary, secondary, danger, etc.)
- **`Input.jsx`**: Inputs com validação e máscaras (CPF, telefone, data)
- **`Select.jsx`**: Select com busca e paginação
- **`Alert.jsx`**: Alertas de sucesso, erro, aviso

### **3. `Validation/`**
- **`PacoteValidator.jsx`**:
  - Valida se pacote está ativo (RN-01, RN-07)
  - Exibe alerta se pacote expirado

- **`SessaoValidator.jsx`**:
  - Valida conflitos de sala (RN-04)
  - Valida conflitos de profissional (RN-05)
  - Valida atraso (RN-08)

- **`FaturamentoValidator.jsx`**:
  - Valida se sessão tem evolução clínica (RN-06)
  - Valida se atendimento não é reduzido (RN-08)

---

## **📊 Validações nas Telas**

| **Tela** | **Regra de Negócio** | **Validação** | **Mensagem de Erro** |
|---------|---------------------|---------------|----------------------|
| Agenda | RN-04 | SalaService.verificar_capacidade_sala() | "Sala lotada" |
| Agenda | RN-05 | ProfissionalService.get_profissionais_disponiveis() | "Profissional ocupado" |
| Agenda | RN-07 | PacoteService.validar_pacote_para_agendamento() | "Pacote expirado ou sem saldo" |
| Atendimento | RN-02 | FaltaService.create() (avisado=false, antecedência<24) | "Falta sem aviso: 1 sessão consumida" |
| Atendimento | RN-03 | FaltaService.create() (avisado=true, antecedência>=24) | "Falta avisada: sessão não consumida" |
| Atendimento | RN-06 | EvolucaoClinicaService.tem_evolucao() | "Sessão de convênio requer evolução clínica" |
| Atendimento | RN-08 | SessaoService.update() (atraso>15) | "Atraso > 15 min: atendimento reduzido" |
| Lote de Convênio | RN-06 | FaturaService.validar_faturamento() | "Não é possível faturar: falta evolução clínica" |
| Lote de Convênio | RN-08 | FaturaService.validar_faturamento() | "Não é possível faturar: atendimento reduzido" |

---

## **🎯 Resumo das Integrações com APIs**

| **Tela** | **APIs Utilizadas** |
|---------|---------------------|
| Cadastro de Pacientes | GET/POST/PUT/DELETE `/api/pacientes/` |
| Cadastro de Profissionais | GET/POST/PUT/DELETE `/api/profissionais/` |
| Cadastro de Salas | GET/POST/PUT/DELETE `/api/salas/` |
| Venda de Pacotes | GET/POST/PUT/DELETE `/api/pacotes/` |
| Agenda | GET/POST `/api/sessoes/`, GET `/api/sessoes/verificar-conflitos/` |
| Atendimento | GET/PUT `/api/sessoes/`, POST `/api/evolucoes/`, POST `/api/faltas/` |
| Lote de Convênio | GET/POST/PUT `/api/lotes/`, POST `/api/faturas/` |
| Relatório de Ocupação | GET `/api/sessoes/` |

---

## **🚀 Próximos Passos**

1. **Implementar os componentes React** para cada tela
2. **Configurar o roteamento** (React Router)
3. **Estilizar com CSS/Styled Components**
4. **Testar todas as validações das RNs**
5. **Integrar com o backend** (FastAPI)

---

## **✅ Checklist de Implementação**

- [ ] Tela 1: Cadastro de Pacientes
- [ ] Tela 2: Cadastro de Profissionais/Salas
- [ ] Tela 3: Venda de Pacotes
- [ ] Tela 4: Agenda
- [ ] Tela 5: Atendimento
- [ ] Tela 6: Lote de Convênio
- [ ] Tela 7: Relatório de Ocupação
- [ ] Componentes reutilizáveis
- [ ] Validações das RNs
- [ ] Integração com API
- [ ] Testes de usabilidade
