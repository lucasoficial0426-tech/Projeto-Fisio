# Tutorial Completo: Como Baixar, Abrir e Testar o Projeto Sessão

## 📥 Passo 1: Baixar o Projeto

### Opção A: Clonar via Git (Recomendado)

1. **Abra o terminal** (Prompt de Comando no Windows, Terminal no Linux/Mac)
2. **Navegue até a pasta onde deseja salvar o projeto**:
   ```bash
   cd /caminho/para/sua/pasta
   ```
   Exemplo:
   ```bash
   cd ~/Documentos/Projetos
   ```

3. **Clone o repositório**:
   ```bash
   git clone https://github.com/lucasoficial0426-tech/Projeto-Fisio.git
   ```

4. **Entre na pasta do projeto**:
   ```bash
   cd Projeto-Fisio
   ```

### Opção B: Baixar ZIP

1. Acesse o repositório no GitHub:
   👉 [https://github.com/lucasoficial0426-tech/Projeto-Fisio](https://github.com/lucasoficial0426-tech/Projeto-Fisio)

2. Clique no botão **"Code"** (verde)
3. Selecione **"Download ZIP"**
4. Extraia o arquivo ZIP em uma pasta de sua preferência

---

## 🖥️ Passo 2: Abrir o Projeto no VS Code

### Instalar o VS Code (se não tiver)

| Sistema Operacional | Comando/Link |
|---------------------|--------------|
| **Windows** | Baixe em: [https://code.visualstudio.com/download](https://code.visualstudio.com/download) |
| **Linux (Debian/Ubuntu)** | `sudo apt update && sudo apt install code` |
| **Linux (Fedora)** | `sudo dnf install code` |
| **Mac** | `brew install --cask visual-studio-code` |

### Abrir o Projeto

1. **Pelo terminal** (recomendado):
   ```bash
   code .
   ```
   (O ponto `.` significa "pasta atual")

2. **Pelo VS Code**:
   - Abra o VS Code
   - Clique em **File → Open Folder...**
   - Selecione a pasta `Projeto-Fisio`
   - Clique em **Select Folder**

### Verificar a Estrutura do Projeto

No **Explorer** (painel esquerdo do VS Code), você verá:

```
PROJETO-SESSAO/
├── .git/                    # Arquivos do Git (ocultos)
├── README.md               # Documentação principal
├── TUTORIAL.md             # Este tutorial
├── sql/                    # Scripts SQL
│   ├── 01_ddl_schema.sql
│   ├── 02_seed_data.sql
│   └── 03_sanitizacao_inconsistencias.sql
└── python/                 # Código Python
    ├── __init__.py
    ├── maquina_estados.py
    ├── pacotes_controller.py
    └── testes.py
```

---

## 🐍 Passo 3: Configurar o Ambiente Python

### Verificar se o Python está instalado

Abra o terminal no VS Code (**Ctrl+`** ou **Terminal → New Terminal**) e execute:

```bash
python --version
```

**Resultado esperado**:
```
Python 3.12.x  # ou qualquer versão 3.8+
```

Se não tiver o Python instalado:

| Sistema Operacional | Comando/Link |
|---------------------|--------------|
| **Windows** | Baixe em: [https://www.python.org/downloads/](https://www.python.org/downloads/) |
| **Linux (Debian/Ubuntu)** | `sudo apt install python3 python3-pip` |
| **Linux (Fedora)** | `sudo dnf install python3` |
| **Mac** | `brew install python` |

### Criar um Ambiente Virtual (Recomendado)

1. **No terminal do VS Code**, execute:
   ```bash
   python -m venv venv
   ```
   (Isso cria uma pasta `venv` com o ambiente isolado)

2. **Ativar o ambiente virtual**:
   - **Windows**:
     ```bash
     .\venv\Scripts\activate
     ```
   - **Linux/Mac**:
     ```bash
     source venv/bin/activate
     ```

   **Resultado esperado**:
   ```
   (venv) C:\caminho\para\Projeto-Fisio>
   ```
   (Aparecerá `(venv)` no início da linha do terminal)

### Instalar Dependências (se necessário)

O projeto não requer dependências externas, mas se precisar instalar algo:

```bash
pip install -r requirements.txt
```

---

## 🧪 Passo 4: Executar os Testes

### Executar Todos os Testes

1. **No terminal do VS Code**, execute:
   ```bash
   python python/testes.py
   ```

2. **Resultado esperado**:
   ```
   test_sala_3_capacidade_maxima (__main__.TestCaso1.test_sala_3_capacidade_maxima) ... ok
   test_sala_3_aceita_3_sessoes (__main__.TestCaso1.test_sala_3_aceita_3_sessoes) ... ok
   test_conflito_profissional_mesmo_horario (__main__.TestCaso2.test_conflito_profissional_mesmo_horario) ... ok
   ...
   
   ----------------------------------------------------------------------
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

Se quiser testar apenas um caso específico:

```bash
# Caso 1: Capacidade da sala
python -m unittest python.testes.TestCaso1 -v

# Caso 4: Falta sem aviso
python -m unittest python.testes.TestCaso4 -v

# Caso 7: Sessão de convênio sem evolução
python -m unittest python.testes.TestCaso7 -v

# Todos os casos de 1 a 10
python -m unittest python.testes.TestCaso1 python.testes.TestCaso2 python.testes.TestCaso3 python.testes.TestCaso4 python.testes.TestCaso5 python.testes.TestCaso6 python.testes.TestCaso7 python.testes.TestCaso8 python.testes.TestCaso9 python.testes.TestCaso10 -v

# Testes de regra temporal
python -m unittest python.testes.TestRegraTemporal -v
```

---

## 🗃️ Passo 5: Testar o Banco de Dados (Opcional)

### Instalar o PostgreSQL

| Sistema Operacional | Comando/Link |
|---------------------|--------------|
| **Windows** | Baixe em: [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/) |
| **Linux (Debian/Ubuntu)** | `sudo apt install postgresql postgresql-contrib` |
| **Linux (Fedora)** | `sudo dnf install postgresql-server postgresql-contrib` |
| **Mac** | `brew install postgresql` |

### Criar o Banco de Dados

1. **Acesse o PostgreSQL**:
   ```bash
   sudo -u postgres psql
   ```

2. **Crie o banco `fisio`**:
   ```sql
   CREATE DATABASE fisio;
   ```

3. **Conecte-se ao banco**:
   ```sql
   \\c fisio
   ```

4. **Execute o esquema do banco**:
   ```sql
   \\i sql/01_ddl_schema.sql
   ```

5. **Carregue os dados**:
   ```sql
   \\i sql/02_seed_data.sql
   ```

6. **Execute a sanitização**:
   ```sql
   \\i sql/03_sanitizacao_inconsistencias.sql
   ```

### Verificar os Dados

1. **Listar todas as tabelas**:
   ```sql
   \\dt fisio.*
   ```

2. **Ver pacientes**:
   ```sql
   SELECT * FROM fisio.paciente;
   ```

3. **Ver profissionais**:
   ```sql
   SELECT * FROM fisio.profissional;
   ```

4. **Ver salas**:
   ```sql
   SELECT * FROM fisio.sala;
   ```

5. **Ver pacotes**:
   ```sql
   SELECT * FROM fisio.pacote;
   ```

6. **Ver sessões**:
   ```sql
   SELECT * FROM fisio.sessao;
   ```

7. **Ver inconsistências**:
   ```sql
   SELECT * FROM fisio.vw_inconsistencias;
   ```

8. **Ver pacotes bloqueados**:
   ```sql
   SELECT * FROM fisio.vw_pacotes_bloqueados;
   ```

9. **Ver sessões bloqueadas**:
   ```sql
   SELECT * FROM fisio.vw_sessoes_bloqueadas;
   ```

### Executar a Sanitização Manualmente

```sql
-- Executar a sanitização completa
CALL fisio.sanitizar_banco();

-- Ou executar a função
SELECT * FROM fisio.executar_sanitizacao_completa();
```

---

## 📝 Passo 6: Testar o Código Python Manualmente

### Testar a Máquina de Estados

1. **Crie um arquivo de teste** (ex: `teste_manual.py`):
   ```python
   from python.maquina_estados import SessaoController, EstadoSessao
   from datetime import datetime, timedelta

   # Criar controller
   controller = SessaoController()

   # Data de referência
   hoje = datetime.now()
   amanha = hoje + timedelta(days=1)
   daqui_2_dias = hoje + timedelta(days=2)

   # Criar uma sessão
   sessao = controller.agendar_sessao(
       paciente_id=1,
       profissional_id=1,
       sala_id=1,
       pacote_id=1,
       data_hora=amanha,
       paciente_tipo="Particular"
   )
   print(f"1. Sessão agendada: {sessao.estado.name}")

   # Realizar sessão
   sessao = controller.realizar_sessao(sessao)
   print(f"2. Sessão realizada: {sessao.estado.name}")

   # Registrar evolução
   sessao = controller.registrar_evolucao(sessao, "Paciente apresentou melhora.")
   print(f"3. Sessão evoluída: {sessao.estado.name}")

   # Faturar sessão
   sessao = controller.faturar_sessao(sessao)
   print(f"4. Sessão faturada: {sessao.estado.name}")
   ```

2. **Execute o arquivo**:
   ```bash
   python teste_manual.py
   ```

### Testar o Controller de Pacotes

1. **Crie um arquivo de teste** (ex: `teste_pacotes.py`):
   ```python
   from python.pacotes_controller import PacotesController
   from datetime import date

   controller = PacotesController()

   # Criar pacote antes de 01/11/2026
   pacote_antigo = controller.criar_pacote(
       paciente_id=1,
       data_compra=date(2026, 10, 15),
       quantidade_sessoes=10,
       validade_dias=90
   )
   print(f"Pacote antigo: {pacote_antigo.quantidade_sessoes} sessões, {pacote_antigo.validade_dias} dias")

   # Criar pacote a partir de 01/11/2026
   pacote_novo = controller.criar_pacote(
       paciente_id=2,
       data_compra=date(2026, 11, 1),
       quantidade_sessoes=15,
       validade_dias=120
   )
   print(f"Pacote novo: {pacote_novo.quantidade_sessoes} sessões, {pacote_novo.validade_dias} dias")

   # Validar pacotes
   print(f"Pacote antigo válido: {controller.validar_pacote(pacote_antigo)}")
   print(f"Pacote novo válido: {controller.validar_pacote(pacote_novo)}")
   ```

2. **Execute o arquivo**:
   ```bash
   python teste_pacotes.py
   ```

---

## 🎯 Passo 7: Entender os 10 Casos de Teste

### Caso 1: Capacidade da Sala
**Objetivo**: Verificar que a Sala 3 (capacidade 3) não aceita uma 4ª sessão.
**RN**: RN-04
**Como testar**:
```bash
python -m unittest python.testes.TestCaso1 -v
```

### Caso 2: Conflito de Profissional
**Objetivo**: Verificar que um profissional não pode ter duas sessões no mesmo horário.
**RN**: RN-05
**Como testar**:
```bash
python -m unittest python.testes.TestCaso2 -v
```

### Caso 3: Capacidade da Sala (Aceitar)
**Objetivo**: Verificar que a Sala 3 aceita até 3 sessões.
**RN**: RN-04
**Como testar**:
```bash
python -m unittest python.testes.TestCaso3 -v
```

### Caso 4: Falta Sem Aviso
**Objetivo**: Verificar que uma falta sem aviso consome uma sessão do pacote.
**RN**: RN-02
**Como testar**:
```bash
python -m unittest python.testes.TestCaso4 -v
```

### Caso 5: Cancelamento Com Aviso
**Objetivo**: Verificar que um cancelamento com 48h de antecedência não consome sessão.
**RN**: RN-03
**Como testar**:
```bash
python -m unittest python.testes.TestCaso5 -v
```

### Caso 6: Pacote Expirado
**Objetivo**: Verificar que um pacote expirado não pode ser usado.
**RN**: RN-01, RN-07
**Como testar**:
```bash
python -m unittest python.testes.TestCaso6 -v
```

### Caso 7: Sessão de Convênio Sem Evolução
**Objetivo**: Verificar que uma sessão de convênio sem evolução não pode ser faturada.
**RN**: RN-06
**Como testar**:
```bash
python -m unittest python.testes.TestCaso7 -v
```

### Caso 8: Sessão de Convênio Com Evolução
**Objetivo**: Verificar que uma sessão de convênio com evolução pode ser faturada.
**RN**: RN-06
**Como testar**:
```bash
python -m unittest python.testes.TestCaso8 -v
```

### Caso 9: Atendimento Reduzido
**Objetivo**: Verificar que um atraso de 20 minutos registra atendimento reduzido e bloqueia faturamento.
**RN**: RN-08
**Como testar**:
```bash
python -m unittest python.testes.TestCaso9 -v
```

### Caso 10: Relatório de Ocupação
**Objetivo**: Verificar a geração do relatório de ocupação por sala e profissional.
**Como testar**:
```bash
python -m unittest python.testes.TestCaso10 -v
```

---

## 🔍 Dicas para Depuração

### Verificar Erros nos Testes

Se um teste falhar, o VS Code mostrará o erro no terminal. Exemplo:

```
FAIL: test_sessao_convenio_sem_evolucao_nao_pode_ser_faturada (__main__.TestCaso7.test_sessao_convenio_sem_evolucao_nao_pode_ser_faturada)
```

Para ver mais detalhes:

```bash
python -m unittest python.testes.TestCaso7.test_sessao_convenio_sem_evolucao_nao_pode_ser_faturada -v
```

### Usar o Debugger do VS Code

1. Abra o arquivo `python/testes.py`
2. Clique no ícone de **Run and Debug** (ícone de play com besouro)
3. Clique em **"Run and Debug"** ou pressione **F5**
4. Selecione **"Python File"**
5. O debugger será iniciado e você poderá:
   - Ver variáveis
   - Passar por cada linha
   - Inspecionar o estado do programa

### Adicionar Print Statements

Se precisar depurar manualmente, adicione `print()` no código:

```python
# Em python/maquina_estados.py
print(f"Estado atual: {sessao.estado.name}")
print(f"Novo estado: {novo_estado.name}")
```

---

## 📌 Resumo dos Comandos Úteis

| **Ação** | **Comando** |
|----------|-------------|
| Clonar o projeto | `git clone https://github.com/lucasoficial0426-tech/Projeto-Fisio.git` |
| Abrir no VS Code | `code .` |
| Criar ambiente virtual | `python -m venv venv` |
| Ativar ambiente (Windows) | `.\venv\Scripts\activate` |
| Ativar ambiente (Linux/Mac) | `source venv/bin/activate` |
| Executar todos os testes | `python python/testes.py` |
| Executar teste específico | `python -m unittest python.testes.TestCaso1 -v` |
| Criar banco PostgreSQL | `sudo -u postgres psql -c "CREATE DATABASE fisio;"` |
| Executar esquema SQL | `sudo -u postgres psql fisio < sql/01_ddl_schema.sql` |
| Carregar dados | `sudo -u postgres psql fisio < sql/02_seed_data.sql` |

---

## 🎉 Parabéns!

Agora você sabe:
✅ Como baixar o projeto
✅ Como abrir no VS Code
✅ Como executar os testes
✅ Como testar o banco de dados
✅ Como depurar o código

O projeto **Sessão** está pronto para ser usado e testado! 🚀

---

## 📞 Suporte

Se encontrar algum problema, verifique:

1. **O Python está instalado?** → `python --version`
2. **O ambiente virtual está ativado?** → Verifique se aparece `(venv)` no terminal
3. **Os arquivos estão no lugar certo?** → Verifique a estrutura no Explorer
4. **O PostgreSQL está rodando?** → `sudo service postgresql status`

Se ainda assim não funcionar, abra uma **Issue** no GitHub:
👉 [https://github.com/lucasoficial0426-tech/Projeto-Fisio/issues](https://github.com/lucasoficial0426-tech/Projeto-Fisio/issues)
