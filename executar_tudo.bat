@echo off
REM ============================================
REM Script para Executar TUDO automaticamente (Windows)
REM ============================================

:menu
cls
echo ==========================================
 echo   PROJETO SESSAO - EXECUCAO AUTOMATICA
 echo ==========================================
echo.

REM Verificar se o Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado! Instale o Python 3.8+ antes de continuar.
    echo [AVISO] Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado

REM Criar ambiente virtual (se nao existir)
if not exist "venv" (
    python -m venv venv
    echo [OK] Ambiente virtual criado
) else (
    echo [OK] Ambiente virtual ja existe
)

REM Ativar ambiente virtual
call venv\Scripts\activate
if errorlevel 1 (
    echo [ERRO] Falha ao ativar ambiente virtual
    pause
    exit /b 1
)
echo [OK] Ambiente virtual ativado

echo.
echo ==========================================
echo   MENU PRINCIPAL
echo ==========================================
echo.
echo Escolha uma opcao:
echo.
echo  1) Executar TODOS os 22 testes
echo  2) Executar apenas os 10 casos oficiais
echo  3) Executar testes individuais (escolher caso)
echo  4) Testar codigo manualmente (exemplos praticos)
echo  5) Ver estrutura do projeto
echo  6) Sair
echo.
echo Digite o numero da opcao: 

set /p opcao=

if "%opcao%" == "1" (
    echo.
    echo [AVISO] Executando TODOS os 22 testes...
    echo ==========================================
    python python\testes.py
    pause
    goto menu
)

if "%opcao%" == "2" (
    echo.
    echo [AVISO] Executando os 10 casos oficiais...
    echo ==========================================
    python -m unittest python.testes.TestCaso1 python.testes.TestCaso2 python.testes.TestCaso3 python.testes.TestCaso4 python.testes.TestCaso5 python.testes.TestCaso6 python.testes.TestCaso7 python.testes.TestCaso8 python.testes.TestCaso9 python.testes.TestCaso10 -v
    pause
    goto menu
)

if "%opcao%" == "3" (
    echo.
    echo Escolha o caso para testar:
    echo.
    echo  1) Caso 1 - Capacidade da sala
    echo  2) Caso 2 - Conflito de profissional
    echo  3) Caso 3 - Capacidade da sala (aceitar)
    echo  4) Caso 4 - Falta sem aviso
    echo  5) Caso 5 - Cancelamento com aviso
    echo  6) Caso 6 - Pacote expirado
    echo  7) Caso 7 - Sessao sem evolucao
    echo  8) Caso 8 - Sessao com evolucao
    echo  9) Caso 9 - Atendimento reduzido
    echo 10) Caso 10 - Relatorio de ocupacao
    echo  0) Voltar
    echo.
    echo Digite o numero do caso: 
    set /p caso=
    
    if "%caso%" == "1" (python -m unittest python.testes.TestCaso1 -v)
    if "%caso%" == "2" (python -m unittest python.testes.TestCaso2 -v)
    if "%caso%" == "3" (python -m unittest python.testes.TestCaso3 -v)
    if "%caso%" == "4" (python -m unittest python.testes.TestCaso4 -v)
    if "%caso%" == "5" (python -m unittest python.testes.TestCaso5 -v)
    if "%caso%" == "6" (python -m unittest python.testes.TestCaso6 -v)
    if "%caso%" == "7" (python -m unittest python.testes.TestCaso7 -v)
    if "%caso%" == "8" (python -m unittest python.testes.TestCaso8 -v)
    if "%caso%" == "9" (python -m unittest python.testes.TestCaso9 -v)
    if "%caso%" == "10" (python -m unittest python.testes.TestCaso10 -v)
    if "%caso%" == "0" (goto menu)
    
    pause
    goto menu
)

if "%opcao%" == "4" (
    echo.
    echo [AVISO] Criando arquivo de teste manual...
    
    REM Criar teste_manual.py
    (
    echo from python.maquina_estados import SessaoController
    echo from python.pacotes_controller import PacotesController
    echo from datetime import datetime, timedelta, date
    echo.
    echo print("=" * 60)
    echo print("TESTE MANUAL - MAQUINA DE ESTADOS")
    echo print("=" * 60)
    echo.
    echo # Testar maquina de estados
    echo controller = SessaoController()
    echo hoje = datetime.now()
    echo amanha = hoje + timedelta(days=1)
    echo.
    echo print("\n1. Criando sessao agendada...")
    echo sessao = controller.agendar_sessao(
    echo     paciente_id=1,
    echo     profissional_id=1,
    echo     sala_id=1,
    echo     pacote_id=1,
    echo     data_hora=amanha,
    echo     paciente_tipo="Particular"
    echo )
    echo print(f"   Estado: {sessao.estado.name}")
    echo.
    echo print("\n2. Realizando sessao...")
    echo sessao = controller.realizar_sessao(sessao)
    echo print(f"   Estado: {sessao.estado.name}")
    echo.
    echo print("\n3. Registrando evolucao...")
    echo sessao = controller.registrar_evolucao(sessao, "Paciente apresentou melhora.")
    echo print(f"   Estado: {sessao.estado.name}")
    echo.
    echo print("\n4. Faturando sessao...")
    echo sessao = controller.faturar_sessao(sessao)
    echo print(f"   Estado: {sessao.estado.name}")
    echo.
    echo print("\n" + "=" * 60)
    echo print("TESTE MANUAL - CONTROLADOR DE PACOTES")
    echo print("=" * 60)
    echo.
    echo # Testar controlador de pacotes
    echo pacotes_controller = PacotesController()
    echo.
    echo print("\n1. Criando pacote antes de 01/11/2026...")
    echo pacote_antigo = pacotes_controller.criar_pacote(
    echo     paciente_id=1,
    echo     data_compra=date(2026, 10, 15),
    echo     quantidade_sessoes=10,
    echo     validade_dias=90
    echo )
    echo print(f"   Sessoes: {pacote_antigo.quantidade_sessoes}, Validade: {pacote_antigo.validade_dias} dias")
    echo.
    echo print("\n2. Criando pacote a partir de 01/11/2026...")
    echo pacote_novo = pacotes_controller.criar_pacote(
    echo     paciente_id=2,
    echo     data_compra=date(2026, 11, 1),
    echo     quantidade_sessoes=15,
    echo     validade_dias=120
    echo )
    echo print(f"   Sessoes: {pacote_novo.quantidade_sessoes}, Validade: {pacote_novo.validade_dias} dias")
    echo.
    echo print("\n3. Validando pacotes...")
    echo print(f"   Pacote antigo valido: {pacotes_controller.validar_pacote(pacote_antigo)}")
    echo print(f"   Pacote novo valido: {pacotes_controller.validar_pacote(pacote_novo)}")
    echo.
    echo print("\n4. Usando uma sessao do pacote...")
    echo pacote_usado = pacotes_controller.usar_sessao(pacote_antigo)
    echo print(f"   Sessoes usadas: {pacote_usado.sessoes_utilizadas}")
    echo print(f"   Saldo: {pacote_usado.saldo}")
    echo.
    echo print("\n" + "=" * 60)
    echo print("SUCCESS TESTES MANUAIS CONCLUIDOS!")
    echo print("=" * 60)
    ) > teste_manual.py
    
    echo [OK] Arquivo teste_manual.py criado!
    echo [AVISO] Executando teste manual...
    echo.
    python teste_manual.py
    pause
    goto menu
)

if "%opcao%" == "5" (
    echo.
    echo [AVISO] Estrutura do projeto:
    echo.
    dir /s /b | findstr /v ".git" | findstr /E ".py .sql .md .sh .bat" | sort
    pause
    goto menu
)

if "%opcao%" == "6" (
    echo.
    echo [OK] Saindo...
    exit /b 0
)

echo.
echo [ERRO] Opcao invalida!
pause
goto menu
