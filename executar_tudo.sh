#!/bin/bash

# ============================================
# Script para Executar TUDO automaticamente
# ============================================

echo "=========================================="
echo "  PROJETO SESSÃO - EXECUÇÃO AUTOMÁTICA"
echo "=========================================="
echo ""

# Cores para o terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para mostrar mensagens coloridas
mensagem() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

sucesso() {
    echo -e "${GREEN}[OK]${NC} $1"
}

erro() {
    echo -e "${RED}[ERRO]${NC} $1"
}

aviso() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# Verificar se o Python está instalado
mensagem "Verificando se o Python está instalado..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    erro "Python não encontrado! Instale o Python 3.8+ antes de continuar."
    aviso "Baixe em: https://www.python.org/downloads/"
    exit 1
fi
sucesso "Python encontrado: $PYTHON"

# Criar ambiente virtual (se não existir)
mensagem "Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
    sucesso "Ambiente virtual criado"
else
    sucesso "Ambiente virtual já existe"
fi

# Ativar ambiente virtual
mensagem "Ativando ambiente virtual..."
if [ "$OS" = "Windows_NT" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
sucesso "Ambiente virtual ativado"

# Instalar dependências (se houver)
mensagem "Instalando dependências..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    sucesso "Dependências instaladas"
else
    sucesso "Nenhum arquivo requirements.txt encontrado"
fi

echo ""
echo "=========================================="
echo "  MENU PRINCIPAL"
echo "=========================================="
echo ""
echo "Escolha uma opção:"
echo ""
echo "  1) Executar TODOS os 22 testes"
echo "  2) Executar apenas os 10 casos oficiais"
echo "  3) Executar testes individuais (escolher caso)"
echo "  4) Testar código manualmente (exemplos práticos)"
echo "  5) Configurar banco de dados PostgreSQL"
echo "  6) Ver estrutura do projeto"
echo "  7) Sair"
echo ""
echo "Digite o número da opção: "

read opcao

case $opcao in
    1)
        echo ""
        aviso "Executando TODOS os 22 testes..."
        echo "=========================================="
        $PYTHON python/testes.py
        ;;
    2)
        echo ""
        aviso "Executando os 10 casos oficiais..."
        echo "=========================================="
        $PYTHON -m unittest python.testes.TestCaso1 python.testes.TestCaso2 python.testes.TestCaso3 python.testes.TestCaso4 python.testes.TestCaso5 python.testes.TestCaso6 python.testes.TestCaso7 python.testes.TestCaso8 python.testes.TestCaso9 python.testes.TestCaso10 -v
        ;;
    3)
        echo ""
        echo "Escolha o caso para testar:"
        echo ""
        echo "  1) Caso 1 - Capacidade da sala"
        echo "  2) Caso 2 - Conflito de profissional"
        echo "  3) Caso 3 - Capacidade da sala (aceitar)"
        echo "  4) Caso 4 - Falta sem aviso"
        echo "  5) Caso 5 - Cancelamento com aviso"
        echo "  6) Caso 6 - Pacote expirado"
        echo "  7) Caso 7 - Sessão sem evolução"
        echo "  8) Caso 8 - Sessão com evolução"
        echo "  9) Caso 9 - Atendimento reduzido"
        echo " 10) Caso 10 - Relatório de ocupação"
        echo "  0) Voltar"
        echo ""
        echo "Digite o número do caso: "
        read caso
        
        case $caso in
            1) $PYTHON -m unittest python.testes.TestCaso1 -v ;;
            2) $PYTHON -m unittest python.testes.TestCaso2 -v ;;
            3) $PYTHON -m unittest python.testes.TestCaso3 -v ;;
            4) $PYTHON -m unittest python.testes.TestCaso4 -v ;;
            5) $PYTHON -m unittest python.testes.TestCaso5 -v ;;
            6) $PYTHON -m unittest python.testes.TestCaso6 -v ;;
            7) $PYTHON -m unittest python.testes.TestCaso7 -v ;;
            8) $PYTHON -m unittest python.testes.TestCaso8 -v ;;
            9) $PYTHON -m unittest python.testes.TestCaso9 -v ;;
           10) $PYTHON -m unittest python.testes.TestCaso10 -v ;;
            0) /bin/bash $0 ;;
            *) erro "Opção inválida!" ;;
        esac
        ;;
    4)
        echo ""
        aviso "Criando arquivos de teste manual..."
        
        # Criar teste_manual.py
        cat > teste_manual.py << 'EOF'
from python.maquina_estados import SessaoController
from python.pacotes_controller import PacotesController
from datetime import datetime, timedelta, date

print("=" * 60)
print("TESTE MANUAL - MÁQUINA DE ESTADOS")
print("=" * 60)

# Testar máquina de estados
controller = SessaoController()
hoje = datetime.now()
amanha = hoje + timedelta(days=1)

print("\n1. Criando sessão agendada...")
sessao = controller.agendar_sessao(
    paciente_id=1,
    profissional_id=1,
    sala_id=1,
    pacote_id=1,
    data_hora=amanha,
    paciente_tipo="Particular"
)
print(f"   Estado: {sessao.estado.name}")

print("\n2. Realizando sessão...")
sessao = controller.realizar_sessao(sessao)
print(f"   Estado: {sessao.estado.name}")

print("\n3. Registrando evolução...")
sessao = controller.registrar_evolucao(sessao, "Paciente apresentou melhora.")
print(f"   Estado: {sessao.estado.name}")

print("\n4. Faturando sessão...")
sessao = controller.faturar_sessao(sessao)
print(f"   Estado: {sessao.estado.name}")

print("\n" + "=" * 60)
print("TESTE MANUAL - CONTROLADOR DE PACOTES")
print("=" * 60)

# Testar controlador de pacotes
pacotes_controller = PacotesController()

print("\n1. Criando pacote antes de 01/11/2026...")
pacote_antigo = pacotes_controller.criar_pacote(
    paciente_id=1,
    data_compra=date(2026, 10, 15),
    quantidade_sessoes=10,
    validade_dias=90
)
print(f"   Sessões: {pacote_antigo.quantidade_sessoes}, Validade: {pacote_antigo.validade_dias} dias")

print("\n2. Criando pacote a partir de 01/11/2026...")
pacote_novo = pacotes_controller.criar_pacote(
    paciente_id=2,
    data_compra=date(2026, 11, 1),
    quantidade_sessoes=15,
    validade_dias=120
)
print(f"   Sessões: {pacote_novo.quantidade_sessoes}, Validade: {pacote_novo.validade_dias} dias")

print("\n3. Validando pacotes...")
print(f"   Pacote antigo válido: {pacotes_controller.validar_pacote(pacote_antigo)}")
print(f"   Pacote novo válido: {pacotes_controller.validar_pacote(pacote_novo)}")

print("\n4. Usando uma sessão do pacote...")
pacote_usado = pacotes_controller.usar_sessao(pacote_antigo)
print(f"   Sessões usadas: {pacote_usado.sessoes_utilizadas}")
print(f"   Saldo: {pacote_usado.saldo}")

print("\n" + "=" * 60)
print("✓ TESTES MANUAIS CONCLUÍDOS!")
print("=" * 60)
EOF

        sucesso "Arquivo teste_manual.py criado!"
        aviso "Executando teste manual..."
        echo ""
        $PYTHON teste_manual.py
        ;;
    5)
        echo ""
        aviso "Configurando banco de dados PostgreSQL..."
        echo ""
        
        # Verificar se o PostgreSQL está instalado
        if command -v psql &> /dev/null; then
            sucesso "PostgreSQL encontrado"
            
            echo ""
            echo "Para configurar o banco de dados manualmente:"
            echo ""
            echo "1. Acesse o PostgreSQL:"
            echo "   sudo -u postgres psql"
            echo ""
            echo "2. Execute os comandos:"
            echo "   CREATE DATABASE fisio;"
            echo "   \\c fisio"
            echo "   \\i sql/01_ddl_schema.sql"
            echo "   \\i sql/02_seed_data.sql"
            echo "   \\i sql/03_sanitizacao_inconsistencias.sql"
            echo ""
            
            # Tentar executar automaticamente
            read -p "Deseja executar automaticamente? (s/n): " resp
            if [ "$resp" = "s" ] || [ "$resp" = "S" ]; then
                echo ""
                aviso "Criando banco de dados..."
                sudo -u postgres psql -c "CREATE DATABASE fisio;" 2>/dev/null || aviso "Banco já existe ou erro ao criar"
                
                aviso "Executando esquema..."
                sudo -u postgres psql fisio < sql/01_ddl_schema.sql 2>/dev/null || erro "Erro ao executar esquema"
                
                aviso "Carregando dados..."
                sudo -u postgres psql fisio < sql/02_seed_data.sql 2>/dev/null || erro "Erro ao carregar dados"
                
                aviso "Executando sanitização..."
                sudo -u postgres psql fisio < sql/03_sanitizacao_inconsistencias.sql 2>/dev/null || erro "Erro ao executar sanitização"
                
                sucesso "Banco de dados configurado com sucesso!"
            fi
        else
            erro "PostgreSQL não encontrado!"
            aviso "Instale o PostgreSQL antes de continuar."
            echo ""
            echo "Para instalar:"
            echo "  Linux (Debian/Ubuntu): sudo apt install postgresql postgresql-contrib"
            echo "  Linux (Fedora): sudo dnf install postgresql-server postgresql-contrib"
            echo "  Mac: brew install postgresql"
            echo "  Windows: https://www.postgresql.org/download/windows/"
        fi
        ;;
    6)
        echo ""
        aviso "Estrutura do projeto:"
        echo ""
        tree -L 3 --noreport 2>/dev/null || find . -maxdepth 3 -type f -name "*.py" -o -name "*.sql" -o -name "*.md" | grep -v ".git" | sort
        ;;
    7)
        echo ""
        sucesso "Saindo..."
        exit 0
        ;;
    *)
        erro "Opção inválida!"
        ;;
esac

echo ""
echo "Pressione Enter para voltar ao menu..."
read
/bin/bash $0
