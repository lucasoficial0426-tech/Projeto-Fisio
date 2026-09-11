"""
Aplicação Flask para o Projeto Sessão
Sistema de Gestão para Clínicas de Fisioterapia
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, date, timedelta
import sys
import os

# Adicionar o diretório python ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importar os controllers do backend
from maquina_estados import SessaoController, EstadoSessao, TransicaoInvalidaError, Sessao
from pacotes_controller import PacotesController, Pacote, PacoteInvalidoError

# Inicializar a aplicação Flask
app = Flask(__name__)
app.secret_key = 'sessao_fisioterapia_2026_secret_key'

# Configurações
app.config['DATABASE_URI'] = 'sqlite:///fisio.db'  # Para futura integração com banco

# Inicializar controllers
sessao_controller = SessaoController()
pacotes_controller = PacotesController()

# Dados de exemplo (simulando banco de dados)
pacientes = [
    {"id": 1, "nome": "Marta Siqueira", "cpf": "111.111.111-11", "tipo": "Particular", "ativo": True},
    {"id": 2, "nome": "Ricardo Tavares", "cpf": "222.222.222-22", "tipo": "Particular", "ativo": True},
    {"id": 3, "nome": "José Anselmo Reis", "cpf": "333.333.333-33", "tipo": "Convênio", "convenio": "SaúdeMais", "ativo": True},
    {"id": 4, "nome": "Carla Bonatto", "cpf": "444.444.444-44", "tipo": "Convênio", "convenio": "UniPlano", "ativo": True}
]

profissionais = [
    {"id": 1, "nome": "Helena Kobayashi", "cpf": "123.456.789-09", "tipo": "Sócio", "ativo": True},
    {"id": 2, "nome": "Diego Martins", "cpf": "987.654.321-00", "tipo": "Contratado", "ativo": True},
    {"id": 3, "nome": "Sabrina Luz", "cpf": "456.789.123-01", "tipo": "Contratada", "ativo": True}
]

salas = [
    {"id": 1, "nome": "Sala 1", "capacidade": 1, "descricao": "Sala individual", "ativo": True},
    {"id": 2, "nome": "Sala 2", "capacidade": 1, "descricao": "Sala individual", "ativo": True},
    {"id": 3, "nome": "Sala 3 - Pilates", "capacidade": 3, "descricao": "Sala para aulas de pilates", "ativo": True}
]

pacotes = [
    {"id": 1, "paciente_id": 1, "data_compra": "2026-08-12", "quantidade_sessoes": 10, "sessoes_utilizadas": 7, "validade_dias": 90, "ativo": True, "tipo": "10_sessoes_90_dias"},
    {"id": 2, "paciente_id": 1, "data_compra": "2026-05-20", "quantidade_sessoes": 10, "sessoes_utilizadas": 10, "validade_dias": 90, "ativo": False, "tipo": "10_sessoes_90_dias"},
    {"id": 3, "paciente_id": 2, "data_compra": "2026-09-05", "quantidade_sessoes": 10, "sessoes_utilizadas": 1, "validade_dias": 90, "ativo": True, "tipo": "10_sessoes_90_dias"}
]

sessoes = []

# ============================================
# Funções Auxiliares
# ============================================

def get_paciente_by_id(paciente_id):
    """Retorna um paciente pelo ID"""
    for p in pacientes:
        if p["id"] == paciente_id:
            return p
    return None

def get_profissional_by_id(profissional_id):
    """Retorna um profissional pelo ID"""
    for p in profissionais:
        if p["id"] == profissional_id:
            return p
    return None

def get_sala_by_id(sala_id):
    """Retorna uma sala pelo ID"""
    for s in salas:
        if s["id"] == sala_id:
            return s
    return None

def get_pacote_by_id(pacote_id):
    """Retorna um pacote pelo ID"""
    for p in pacotes:
        if p["id"] == pacote_id:
            return p
    return None

def get_sessao_by_id(sessao_id):
    """Retorna uma sessão pelo ID"""
    for s in sessoes:
        if s["id"] == sessao_id:
            return s
    return None

def formatar_data(data_str):
    """Formata data do formato YYYY-MM-DD para DD/MM/YYYY"""
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d").date()
        return data.strftime("%d/%m/%Y")
    except:
        return data_str

def formatar_data_hora(data_hora_str):
    """Formata data e hora"""
    try:
        dt = datetime.strptime(data_hora_str, "%Y-%m-%dT%H:%M")
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return data_hora_str

# ============================================
# Rotas
# ============================================

@app.route('/')
def index():
    """Página inicial - Dashboard"""
    # Contar estatísticas
    total_pacientes = len([p for p in pacientes if p["ativo"]])
    total_profissionais = len([p for p in profissionais if p["ativo"]])
    total_salas = len([s for s in salas if s["ativo"]])
    total_pacotes = len([p for p in pacotes if p["ativo"]])
    total_sessoes = len([s for s in sessoes if s.get("ativo", True)])
    
    # Pacotes ativos vs bloqueados
    pacotes_ativos = len([p for p in pacotes if p["ativo"]])
    pacotes_bloqueados = len([p for p in pacotes if not p["ativo"]])
    
    # Sessões por estado
    sessoes_agendadas = len([s for s in sessoes if s.get("estado") == "Agendada"])
    sessoes_realizadas = len([s for s in sessoes if s.get("estado") == "Realizada"])
    sessoes_faturadas = len([s for s in sessoes if s.get("estado") == "Faturada"])
    
    return render_template('index.html',
                         total_pacientes=total_pacientes,
                         total_profissionais=total_profissionais,
                         total_salas=total_salas,
                         total_pacotes=total_pacotes,
                         total_sessoes=total_sessoes,
                         pacotes_ativos=pacotes_ativos,
                         pacotes_bloqueados=pacotes_bloqueados,
                         sessoes_agendadas=sessoes_agendadas,
                         sessoes_realizadas=sessoes_realizadas,
                         sessoes_faturadas=sessoes_faturadas)


@app.route('/pacientes')
def listar_pacientes():
    """Lista todos os pacientes"""
    return render_template('pacientes.html', pacientes=pacientes)


@app.route('/pacientes/cadastro', methods=['GET', 'POST'])
def cadastro_paciente():
    """Cadastro de pacientes"""
    if request.method == 'POST':
        # Criar novo paciente
        novo_id = max([p["id"] for p in pacientes]) + 1 if pacientes else 1
        novo_paciente = {
            "id": novo_id,
            "nome": request.form['nome'],
            "cpf": request.form['cpf'],
            "tipo": request.form['tipo'],
            "convenio": request.form.get('convenio', ''),
            "ativo": True
        }
        pacientes.append(novo_paciente)
        flash('Paciente cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_pacientes'))
    
    # Convênios disponíveis
    convenios = ["SaúdeMais", "UniPlano"]
    return render_template('pacientes_cadastro.html', convenios=convenios)


@app.route('/pacientes/editar/<int:paciente_id>', methods=['GET', 'POST'])
def editar_paciente(paciente_id):
    """Editar paciente"""
    paciente = get_paciente_by_id(paciente_id)
    if not paciente:
        flash('Paciente não encontrado!', 'danger')
        return redirect(url_for('listar_pacientes'))
    
    if request.method == 'POST':
        # Atualizar paciente
        paciente["nome"] = request.form['nome']
        paciente["cpf"] = request.form['cpf']
        paciente["tipo"] = request.form['tipo']
        paciente["convenio"] = request.form.get('convenio', '')
        flash('Paciente atualizado com sucesso!', 'success')
        return redirect(url_for('listar_pacientes'))
    
    convenios = ["SaúdeMais", "UniPlano"]
    return render_template('pacientes_editar.html', paciente=paciente, convenios=convenios)


@app.route('/pacientes/desativar/<int:paciente_id>')
def desativar_paciente(paciente_id):
    """Desativar paciente"""
    paciente = get_paciente_by_id(paciente_id)
    if paciente:
        paciente["ativo"] = False
        flash('Paciente desativado!', 'warning')
    return redirect(url_for('listar_pacientes'))


@app.route('/pacientes/ativar/<int:paciente_id>')
def ativar_paciente(paciente_id):
    """Ativar paciente"""
    paciente = get_paciente_by_id(paciente_id)
    if paciente:
        paciente["ativo"] = True
        flash('Paciente ativado!', 'success')
    return redirect(url_for('listar_pacientes'))


@app.route('/profissionais')
def listar_profissionais():
    """Lista todos os profissionais"""
    return render_template('profissionais.html', profissionais=profissionais, salas=salas)


@app.route('/profissionais/cadastro', methods=['GET', 'POST'])
def cadastro_profissional():
    """Cadastro de profissionais"""
    if request.method == 'POST':
        # Criar novo profissional
        novo_id = max([p["id"] for p in profissionais]) + 1 if profissionais else 1
        novo_profissional = {
            "id": novo_id,
            "nome": request.form['nome'],
            "cpf": request.form['cpf'],
            "tipo": request.form['tipo'],
            "ativo": True
        }
        profissionais.append(novo_profissional)
        flash('Profissional cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_profissionais'))
    
    return render_template('profissionais_cadastro.html')


@app.route('/profissionais/editar/<int:profissional_id>', methods=['GET', 'POST'])
def editar_profissional(profissional_id):
    """Editar profissional"""
    profissional = get_profissional_by_id(profissional_id)
    if not profissional:
        flash('Profissional não encontrado!', 'danger')
        return redirect(url_for('listar_profissionais'))
    
    if request.method == 'POST':
        # Atualizar profissional
        profissional["nome"] = request.form['nome']
        profissional["cpf"] = request.form['cpf']
        profissional["tipo"] = request.form['tipo']
        flash('Profissional atualizado com sucesso!', 'success')
        return redirect(url_for('listar_profissionais'))
    
    return render_template('profissionais_editar.html', profissional=profissional)


@app.route('/profissionais/desativar/<int:profissional_id>')
def desativar_profissional(profissional_id):
    """Desativar profissional"""
    profissional = get_profissional_by_id(profissional_id)
    if profissional:
        profissional["ativo"] = False
        flash('Profissional desativado!', 'warning')
    return redirect(url_for('listar_profissionais'))


@app.route('/profissionais/ativar/<int:profissional_id>')
def ativar_profissional(profissional_id):
    """Ativar profissional"""
    profissional = get_profissional_by_id(profissional_id)
    if profissional:
        profissional["ativo"] = True
        flash('Profissional ativado!', 'success')
    return redirect(url_for('listar_profissionais'))


@app.route('/pacotes')
def listar_pacotes():
    """Lista todos os pacotes"""
    # Adicionar informações dos pacientes
    pacotes_com_nome = []
    for p in pacotes:
        paciente = get_paciente_by_id(p["paciente_id"])
        pacote_data = p.copy()
        pacote_data["paciente_nome"] = paciente["nome"] if paciente else "Desconhecido"
        pacote_data["paciente_cpf"] = paciente["cpf"] if paciente else ""
        
        # Calcular data de vencimento
        try:
            data_compra = datetime.strptime(p["data_compra"], "%Y-%m-%d").date()
            data_vencimento = data_compra + timedelta(days=p["validade_dias"])
            pacote_data["data_vencimento"] = data_vencimento.strftime("%d/%m/%Y")
            pacote_data["expirado"] = data_vencimento < date.today()
        except:
            pacote_data["data_vencimento"] = "N/A"
            pacote_data["expirado"] = False
        
        pacote_data["saldo"] = p["quantidade_sessoes"] - p["sessoes_utilizadas"]
        pacotes_com_nome.append(pacote_data)
    
    return render_template('pacotes.html', pacotes=pacotes_com_nome, pacientes=pacientes)


@app.route('/pacotes/venda', methods=['GET', 'POST'])
def venda_pacotes():
    """Venda de pacotes"""
    if request.method == 'POST':
        paciente_id = int(request.form['paciente_id'])
        data_compra = request.form['data_compra']
        
        # Determinar tipo de pacote com base na data
        try:
            data_compra_date = datetime.strptime(data_compra, "%Y-%m-%d").date()
        except:
            data_compra_date = date.today()
        
        # Usar o controller de pacotes
        try:
            pacote = pacotes_controller.criar_pacote(
                paciente_id=paciente_id,
                data_compra=data_compra_date,
                quantidade_sessoes=None,  # Usa padrão
                validade_dias=None  # Usa padrão
            )
            
            # Adicionar ao banco de dados simulado
            novo_pacote = {
                "id": max([p["id"] for p in pacotes]) + 1 if pacotes else 1,
                "paciente_id": paciente_id,
                "data_compra": data_compra,
                "quantidade_sessoes": pacote.quantidade_sessoes,
                "sessoes_utilizadas": 0,
                "validade_dias": pacote.validade_dias,
                "ativo": True,
                "tipo": pacote.tipo
            }
            pacotes.append(novo_pacote)
            flash('Pacote vendido com sucesso!', 'success')
            return redirect(url_for('listar_pacotes'))
        except PacoteInvalidoError as e:
            flash(str(e), 'danger')
    
    return render_template('pacotes_venda.html', pacientes=pacientes)


@app.route('/pacotes/desativar/<int:pacote_id>')
def desativar_pacote(pacote_id):
    """Desativar pacote"""
    pacote = get_pacote_by_id(pacote_id)
    if pacote:
        pacote["ativo"] = False
        flash('Pacote desativado!', 'warning')
    return redirect(url_for('listar_pacotes'))


@app.route('/agenda')
def agenda():
    """Agenda de sessões"""
    # Agrupar sessões por data
    agenda_por_data = {}
    for sessao in sessoes:
        data = sessao.get('data_hora', '')[:10]  # Extrair apenas a data
        if data not in agenda_por_data:
            agenda_por_data[data] = []
        agenda_por_data[data].append(sessao)
    
    # Ordenar por data
    datas_ordenadas = sorted(agenda_por_data.keys(), reverse=True)
    
    # Formatar datas
    datas_formatadas = {}
    for data in datas_ordenadas:
        data_formatada = formatar_data(data)
        datas_formatadas[data_formatada] = agenda_por_data[data]
    
    return render_template('agenda.html', 
                         agenda=datas_formatadas,
                         pacientes=pacientes,
                         profissionais=profissionais,
                         salas=salas,
                         pacotes=pacotes)


@app.route('/agenda/nova', methods=['GET', 'POST'])
def nova_sessao():
    """Agendar nova sessão"""
    if request.method == 'POST':
        paciente_id = int(request.form['paciente_id'])
        profissional_id = int(request.form['profissional_id'])
        sala_id = int(request.form['sala_id'])
        pacote_id = int(request.form['pacote_id']) if request.form.get('pacote_id') else None
        data_hora = request.form['data_hora']
        
        # Validar capacidade da sala
        sala = get_sala_by_id(sala_id)
        if sala:
            # Contar sessões na mesma data/hora
            data_hora_obj = datetime.strptime(data_hora, "%Y-%m-%dT%H:%M")
            sessoes_na_sala = [s for s in sessoes 
                             if s.get('sala_id') == sala_id 
                             and s.get('data_hora') == data_hora
                             and s.get('ativo', True)]
            
            if len(sessoes_na_sala) >= sala["capacidade"]:
                flash(f'Capacidade da sala excedida! Máximo: {sala["capacidade"]} sessões', 'danger')
                return redirect(url_for('nova_sessao'))
        
        # Validar conflito de profissional
        profissional = get_profissional_by_id(profissional_id)
        if profissional:
            sessoes_profissional = [s for s in sessoes 
                                   if s.get('profissional_id') == profissional_id 
                                   and s.get('data_hora') == data_hora
                                   and s.get('ativo', True)]
            
            if sessoes_profissional:
                flash('Profissional já tem sessão nesse horário!', 'danger')
                return redirect(url_for('nova_sessao'))
        
        # Validar pacote (se fornecido)
        if pacote_id:
            pacote = get_pacote_by_id(pacote_id)
            if pacote and not pacote["ativo"]:
                flash('Pacote está bloqueado!', 'danger')
                return redirect(url_for('nova_sessao'))
            
            if pacote:
                saldo = pacote["quantidade_sessoes"] - pacote["sessoes_utilizadas"]
                if saldo <= 0:
                    flash('Pacote não tem saldo!', 'danger')
                    return redirect(url_for('nova_sessao'))
        
        # Criar nova sessão
        novo_id = max([s["id"] for s in sessoes]) + 1 if sessoes else 1
        paciente = get_paciente_by_id(paciente_id)
        
        nova_sessao = {
            "id": novo_id,
            "paciente_id": paciente_id,
            "profissional_id": profissional_id,
            "sala_id": sala_id,
            "pacote_id": pacote_id,
            "data_hora": data_hora,
            "estado": "Agendada",
            "evolucao_clinica": "",
            "ativo": True,
            "paciente_nome": paciente["nome"] if paciente else "Desconhecido",
            "profissional_nome": profissional["nome"] if profissional else "Desconhecido",
            "sala_nome": sala["nome"] if sala else "Desconhecida"
        }
        sessoes.append(nova_sessao)
        
        # Atualizar sessões utilizadas do pacote
        if pacote_id:
            pacote = get_pacote_by_id(pacote_id)
            if pacote:
                pacote["sessoes_utilizadas"] += 1
        
        flash('Sessão agendada com sucesso!', 'success')
        return redirect(url_for('agenda'))
    
    return render_template('agenda_nova.html', 
                         pacientes=pacientes,
                         profissionais=profissionais,
                         salas=salas,
                         pacotes=pacotes)


@app.route('/agenda/cancelar/<int:sessao_id>')
def cancelar_sessao(sessao_id):
    """Cancelar sessão"""
    sessao = get_sessao_by_id(sessao_id)
    if sessao:
        sessao["estado"] = "Cancelada com aviso"
        flash('Sessão cancelada!', 'warning')
    return redirect(url_for('agenda'))


@app.route('/agenda/falta/<int:sessao_id>')
def registrar_falta(sessao_id):
    """Registrar falta sem aviso"""
    sessao = get_sessao_by_id(sessao_id)
    if sessao:
        sessao["estado"] = "Falta sem aviso"
        # Consumir sessão do pacote (RN-02)
        if sessao.get('pacote_id'):
            pacote = get_pacote_by_id(sessao['pacote_id'])
            if pacote:
                pacote["sessoes_utilizadas"] += 1
        flash('Falta registrada! Sessão consumida do pacote.', 'warning')
    return redirect(url_for('agenda'))


@app.route('/atendimento')
def atendimento():
    """Atendimento - Sessões em andamento"""
    # Sessões que podem ser atendidas (Agendada ou Realizada)
    sessoes_atendimento = [s for s in sessoes 
                         if s.get('estado') in ['Agendada', 'Realizada'] 
                         and s.get('ativo', True)]
    
    return render_template('atendimento.html', sessoes=sessoes_atendimento)


@app.route('/atendimento/realizar/<int:sessao_id>')
def realizar_atendimento(sessao_id):
    """Realizar sessão"""
    sessao = get_sessao_by_id(sessao_id)
    if sessao:
        # Usar a máquina de estados
        try:
            # Criar objeto Sessao para a máquina de estados
            paciente = get_paciente_by_id(sessao['paciente_id'])
            paciente_tipo = paciente.get('tipo', 'Particular') if paciente else 'Particular'
            
            sessao_obj = Sessao(
                id=sessao['id'],
                paciente_id=sessao['paciente_id'],
                profissional_id=sessao['profissional_id'],
                sala_id=sessao['sala_id'],
                pacote_id=sessao.get('pacote_id'),
                data_hora=datetime.strptime(sessao['data_hora'], "%Y-%m-%dT%H:%M"),
                estado=EstadoSessao[sessao['estado'].upper()],
                evolucao_clinica=sessao.get('evolucao_clinica'),
                ativo=sessao.get('ativo', True),
                paciente_tipo=paciente_tipo
            )
            
            # Transicionar para Realizada
            sessao_obj = sessao_controller.realizar_sessao(sessao_obj)
            sessao['estado'] = sessao_obj.estado.name
            flash('Sessão realizada!', 'success')
        except TransicaoInvalidaError as e:
            flash(str(e), 'danger')
    
    return redirect(url_for('atendimento'))


@app.route('/atendimento/evolucao/<int:sessao_id>', methods=['GET', 'POST'])
def registrar_evolucao(sessao_id):
    """Registrar evolução clínica"""
    sessao = get_sessao_by_id(sessao_id)
    if not sessao:
        flash('Sessão não encontrada!', 'danger')
        return redirect(url_for('atendimento'))
    
    if request.method == 'POST':
        evolucao = request.form['evolucao']
        
        # Usar a máquina de estados
        try:
            paciente = get_paciente_by_id(sessao['paciente_id'])
            paciente_tipo = paciente.get('tipo', 'Particular') if paciente else 'Particular'
            
            sessao_obj = Sessao(
                id=sessao['id'],
                paciente_id=sessao['paciente_id'],
                profissional_id=sessao['profissional_id'],
                sala_id=sessao['sala_id'],
                pacote_id=sessao.get('pacote_id'),
                data_hora=datetime.strptime(sessao['data_hora'], "%Y-%m-%dT%H:%M"),
                estado=EstadoSessao[sessao['estado'].upper()],
                evolucao_clinica=sessao.get('evolucao_clinica'),
                ativo=sessao.get('ativo', True),
                paciente_tipo=paciente_tipo
            )
            
            # Registrar evolução
            sessao_obj = sessao_controller.registrar_evolucao(sessao_obj, evolucao)
            sessao['estado'] = sessao_obj.estado.name
            sessao['evolucao_clinica'] = evolucao
            flash('Evolução registrada!', 'success')
            return redirect(url_for('atendimento'))
        except TransicaoInvalidaError as e:
            flash(str(e), 'danger')
    
    return render_template('atendimento_evolucao.html', sessao=sessao)


@app.route('/atendimento/faturar/<int:sessao_id>')
def faturar_sessao(sessao_id):
    """Faturar sessão"""
    sessao = get_sessao_by_id(sessao_id)
    if sessao:
        # Usar a máquina de estados
        try:
            paciente = get_paciente_by_id(sessao['paciente_id'])
            paciente_tipo = paciente.get('tipo', 'Particular') if paciente else 'Particular'
            
            sessao_obj = Sessao(
                id=sessao['id'],
                paciente_id=sessao['paciente_id'],
                profissional_id=sessao['profissional_id'],
                sala_id=sessao['sala_id'],
                pacote_id=sessao.get('pacote_id'),
                data_hora=datetime.strptime(sessao['data_hora'], "%Y-%m-%dT%H:%M"),
                estado=EstadoSessao[sessao['estado'].upper()],
                evolucao_clinica=sessao.get('evolucao_clinica'),
                ativo=sessao.get('ativo', True),
                paciente_tipo=paciente_tipo
            )
            
            # Faturar
            sessao_obj = sessao_controller.faturar_sessao(sessao_obj)
            sessao['estado'] = sessao_obj.estado.name
            flash('Sessão faturada!', 'success')
        except TransicaoInvalidaError as e:
            flash(str(e), 'danger')
    
    return redirect(url_for('atendimento'))


@app.route('/atendimento/atraso/<int:sessao_id>')
def registrar_atraso(sessao_id):
    """Registrar atendimento reduzido (atraso > 15 min)"""
    sessao = get_sessao_by_id(sessao_id)
    if sessao:
        # Usar a máquina de estados
        try:
            paciente = get_paciente_by_id(sessao['paciente_id'])
            paciente_tipo = paciente.get('tipo', 'Particular') if paciente else 'Particular'
            
            sessao_obj = Sessao(
                id=sessao['id'],
                paciente_id=sessao['paciente_id'],
                profissional_id=sessao['profissional_id'],
                sala_id=sessao['sala_id'],
                pacote_id=sessao.get('pacote_id'),
                data_hora=datetime.strptime(sessao['data_hora'], "%Y-%m-%dT%H:%M"),
                estado=EstadoSessao[sessao['estado'].upper()],
                evolucao_clinica=sessao.get('evolucao_clinica'),
                ativo=sessao.get('ativo', True),
                paciente_tipo=paciente_tipo
            )
            
            # Registrar atendimento reduzido (20 min de atraso)
            sessao_obj = sessao_controller.registrar_atendimento_reduzido(sessao_obj, 20)
            sessao['estado'] = sessao_obj.estado.name
            flash('Atendimento reduzido registrado! (RN-08: bloqueia faturamento)', 'warning')
        except TransicaoInvalidaError as e:
            flash(str(e), 'danger')
    
    return redirect(url_for('atendimento'))


@app.route('/lote_convenio')
def lote_convenio():
    """Lote de faturamento de convênio"""
    # Sessões de convênio que podem ser faturadas (Evoluída)
    sessoes_faturaveis = [s for s in sessoes 
                         if s.get('estado') == 'Evoluída'
                         and s.get('ativo', True)]
    
    # Agrupar por convênio
    lotes = {}
    for sessao in sessoes_faturaveis:
        paciente = get_paciente_by_id(sessao['paciente_id'])
        convenio = paciente.get('convenio', 'Desconhecido') if paciente else 'Desconhecido'
        
        if convenio not in lotes:
            lotes[convenio] = []
        lotes[convenio].append(sessao)
    
    return render_template('lote_convenio.html', lotes=lotes)


@app.route('/relatorio')
def relatorio():
    """Relatório de ocupação"""
    # Calcular ocupação por sala
    ocupacao_por_sala = {}
    for sala in salas:
        sessao_count = len([s for s in sessoes 
                           if s.get('sala_id') == sala['id'] 
                           and s.get('ativo', True)])
        ocupacao_por_sala[sala['nome']] = {
            'total': sessao_count,
            'capacidade': sala['capacidade'],
            'taxa': (sessao_count / sala['capacidade']) * 100 if sala['capacidade'] > 0 else 0
        }
    
    # Calcular ocupação por profissional
    ocupacao_por_profissional = {}
    for prof in profissionais:
        sessao_count = len([s for s in sessoes 
                           if s.get('profissional_id') == prof['id'] 
                           and s.get('ativo', True)])
        ocupacao_por_profissional[prof['nome']] = sessao_count
    
    # Calcular ocupação por dia (últimos 30 dias)
    ocupacao_por_dia = {}
    for sessao in sessoes:
        if sessao.get('ativo', True):
            data = sessao.get('data_hora', '')[:10]
            if data not in ocupacao_por_dia:
                ocupacao_por_dia[data] = 0
            ocupacao_por_dia[data] += 1
    
    # Ordenar por data
    ocupacao_por_dia = dict(sorted(ocupacao_por_dia.items(), reverse=True))
    
    # Formatar datas
    ocupacao_por_dia_formatado = {}
    for data, count in ocupacao_por_dia.items():
        data_formatada = formatar_data(data)
        ocupacao_por_dia_formatado[data_formatada] = count
    
    return render_template('relatorio.html',
                         ocupacao_por_sala=ocupacao_por_sala,
                         ocupacao_por_profissional=ocupacao_por_profissional,
                         ocupacao_por_dia=ocupacao_por_dia_formatado)


# ============================================
# Inicialização
# ============================================

if __name__ == '__main__':
    # Criar uma sessão de exemplo (se não houver nenhuma)
    if not sessoes:
        hoje = date.today()
        amanha = hoje + timedelta(days=1)
        
        # Sessão de exemplo
        sessoes.append({
            "id": 1,
            "paciente_id": 1,
            "profissional_id": 1,
            "sala_id": 1,
            "pacote_id": 1,
            "data_hora": f"{amanha}T10:00",
            "estado": "Agendada",
            "evolucao_clinica": "",
            "ativo": True,
            "paciente_nome": "Marta Siqueira",
            "profissional_nome": "Helena Kobayashi",
            "sala_nome": "Sala 1"
        })
    
    # Executar a aplicação
    print("=" * 60)
    print("PROJETO SESSÃO - SISTEMA DE FISIOTERAPIA")
    print("=" * 60)
    print("\nAplicação rodando em: http://localhost:5000")
    print("\nPressione CTRL+C para parar o servidor")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
