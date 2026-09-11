"""
Máquina de Estados para o Ciclo de Vida da Sessão
Implementa validação rígida de transições de estados conforme RN-06 e RN-08
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta


class EstadoSessao(Enum):
    """Estados possíveis para uma sessão"""
    AGENDADA = auto()
    REALIZADA = auto()
    EVOLUIDA = auto()
    FATURADA = auto()
    CANCELADA_COM_AVISO = auto()
    FALTA_SEM_AVISO = auto()
    ATENDIMENTO_REDUZIDO = auto()


class TransicaoInvalidaError(Exception):
    """Exceção lançada quando uma transição de estado inválida é tentada"""
    def __init__(self, de_estado: EstadoSessao, para_estado: EstadoSessao, motivo: str):
        self.de_estado = de_estado
        self.para_estado = para_estado
        self.motivo = motivo
        super().__init__(f"Transição inválida: {de_estado.name} -> {para_estado.name}. {motivo}")


class SessaoBloqueadaError(Exception):
    """Exceção lançada quando uma sessão está bloqueada"""
    def __init__(self, sessao_id: int, motivo: str):
        self.sessao_id = sessao_id
        self.motivo = motivo
        super().__init__(f"Sessão {sessao_id} bloqueada: {motivo}")


@dataclass
class Sessao:
    """Representa uma sessão no sistema"""
    id: int
    paciente_id: int
    profissional_id: int
    sala_id: int
    pacote_id: Optional[int]
    data_hora: datetime
    estado: EstadoSessao
    evolucao_clinica: Optional[str]
    ativo: bool = True
    paciente_tipo: str = "Particular"  # "Particular" ou "Convênio"
    
    def __post_init__(self):
        if isinstance(self.estado, str):
            self.estado = EstadoSessao[self.estado.upper()]


class MaquinaEstadosSessao:
    """
    Máquina de estados para gerenciar o ciclo de vida da Sessão.
    
    Fluxo Principal: Agendada -> Realizada -> Evoluída -> Faturada
    Fluxos Alternativos: 
    - Cancelada com aviso (de Agendada)
    - Falta sem aviso (de Agendada)
    - Atendimento reduzido (de Agendada ou Realizada)
    
    Travas de Transições Proibidas:
    - IMPEDIR: Realizada -> Faturada (obrigatório passar por Evoluída - RN-06)
    - IMPEDIR: Falta sem aviso -> Realizada (passado não pode ser reescrito)
    - IMPEDIR: Atendimento reduzido -> Faturada (RN-08)
    - PERMITIR: Agendada -> Cancelada com aviso (se comunicado com 24h ou mais de antecedência)
    """
    
    # Matriz de transições válidas
    TRANSICOES_VALIDAS: Dict[EstadoSessao, Set[EstadoSessao]] = {
        EstadoSessao.AGENDADA: {
            EstadoSessao.REALIZADA,
            EstadoSessao.CANCELADA_COM_AVISO,
            EstadoSessao.FALTA_SEM_AVISO,
            EstadoSessao.ATENDIMENTO_REDUZIDO
        },
        EstadoSessao.REALIZADA: {
            EstadoSessao.EVOLUIDA,
            EstadoSessao.ATENDIMENTO_REDUZIDO
        },
        EstadoSessao.EVOLUIDA: {
            EstadoSessao.FATURADA
        },
        EstadoSessao.FATURADA: set(),  # Estado final, não há transições
        EstadoSessao.CANCELADA_COM_AVISO: set(),  # Estado final
        EstadoSessao.FALTA_SEM_AVISO: set(),  # Estado final
        EstadoSessao.ATENDIMENTO_REDUZIDO: set()  # Estado final (RN-08: não pode ser faturado)
    }
    
    # Transições que requerem validações adicionais
    TRANSICOES_ESPECIAIS: Dict[str, callable] = {}
    
    def __init__(self):
        """Inicializa a máquina de estados"""
        pass
    
    def validar_transicao(
        self, 
        sessao: Sessao, 
        novo_estado: EstadoSessao,
        data_aviso: Optional[datetime] = None,
        atraso_minutos: Optional[int] = None
    ) -> bool:
        """
        Valida se uma transição de estado é permitida.
        
        Args:
            sessao: A sessão que terá seu estado alterado
            novo_estado: O estado para o qual se deseja transicionar
            data_aviso: Data do aviso de cancelamento (para Cancelada com aviso)
            atraso_minutos: Minutos de atraso (para Atendimento reduzido)
            
        Returns:
            bool: True se a transição é válida, False caso contrário
            
        Raises:
            TransicaoInvalidaError: Se a transição não é permitida
            SessaoBloqueadaError: Se a sessão está bloqueada
        """
        # Verifica se a sessão está bloqueada
        if not sessao.ativo:
            raise SessaoBloqueadaError(sessao.id, "Sessão está bloqueada")
        
        # Verifica se a transição é válida segundo a matriz
        if novo_estado not in self.TRANSICOES_VALIDAS.get(sessao.estado, set()):
            raise TransicaoInvalidaError(
                sessao.estado, 
                novo_estado, 
                f"Transição não permitida segundo o fluxo de estados"
            )
        
        # Validações específicas para cada tipo de transição
        
        # RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica
        if novo_estado == EstadoSessao.FATURADA and sessao.paciente_tipo == "Convênio":
            if not sessao.evolucao_clinica or not sessao.evolucao_clinica.strip():
                raise TransicaoInvalidaError(
                    sessao.estado,
                    novo_estado,
                    "Sessão de convênio não pode ser faturada sem evolução clínica (RN-06)"
                )
        
        # RN-08: Atendimento reduzido bloqueia faturamento
        if novo_estado == EstadoSessao.FATURADA and sessao.estado == EstadoSessao.ATENDIMENTO_REDUZIDO:
            raise TransicaoInvalidaError(
                sessao.estado,
                novo_estado,
                "Sessão com atendimento reduzido não pode ser faturada (RN-08)"
            )
        
        # RN-03: Falta avisada com 24h ou mais de antecedência não consome sessão
        # RN-02: Falta sem aviso com antecedência de 24h consome uma sessão do pacote
        if novo_estado == EstadoSessao.CANCELADA_COM_AVISO:
            if data_aviso is None:
                raise TransicaoInvalidaError(
                    sessao.estado,
                    novo_estado,
                    "Data do aviso é obrigatória para cancelamento com aviso"
                )
            
            # Verifica se o aviso foi dado com 24h ou mais de antecedência
            if (sessao.data_hora - data_aviso).total_seconds() < 24 * 3600:
                raise TransicaoInvalidaError(
                    sessao.estado,
                    novo_estado,
                    "Cancelamento com aviso requer 24h ou mais de antecedência (RN-03)"
                )
        
        # RN-08: Atraso superior a 15 min registra atendimento reduzido
        if novo_estado == EstadoSessao.ATENDIMENTO_REDUZIDO:
            if atraso_minutos is None or atraso_minutos <= 15:
                raise TransicaoInvalidaError(
                    sessao.estado,
                    novo_estado,
                    "Atendimento reduzido requer atraso superior a 15 minutos (RN-08)"
                )
        
        # IMPEDIR: Falta sem aviso -> Realizada (passado não pode ser reescrito)
        if sessao.estado == EstadoSessao.FALTA_SEM_AVISO and novo_estado == EstadoSessao.REALIZADA:
            raise TransicaoInvalidaError(
                sessao.estado,
                novo_estado,
                "Não é possível alterar uma falta sem aviso para realizada (passado não pode ser reescrito)"
            )
        
        # IMPEDIR: Realizada -> Faturada (obrigatório passar por Evoluída - RN-06)
        if sessao.estado == EstadoSessao.REALIZADA and novo_estado == EstadoSessao.FATURADA:
            raise TransicaoInvalidaError(
                sessao.estado,
                novo_estado,
                "Não é possível faturar uma sessão realizada sem evolução clínica. "
                "É obrigatório passar pelo estado Evoluída (RN-06)"
            )
        
        return True
    
    def transicionar(
        self,
        sessao: Sessao,
        novo_estado: EstadoSessao,
        data_aviso: Optional[datetime] = None,
        atraso_minutos: Optional[int] = None,
        evolucao_clinica: Optional[str] = None
    ) -> Sessao:
        """
        Executa a transição de estado de uma sessão.
        
        Args:
            sessao: A sessão a ser atualizada
            novo_estado: O novo estado
            data_aviso: Data do aviso (para Cancelada com aviso)
            atraso_minutos: Minutos de atraso (para Atendimento reduzido)
            evolucao_clinica: Evolução clínica (para Evoluída)
            
        Returns:
            Sessao: A sessão atualizada
            
        Raises:
            TransicaoInvalidaError: Se a transição não é permitida
        """
        # Valida a transição
        self.validar_transicao(sessao, novo_estado, data_aviso, atraso_minutos)
        
        # Cria uma cópia da sessão para não modificar o objeto original diretamente
        nova_sessao = Sessao(
            id=sessao.id,
            paciente_id=sessao.paciente_id,
            profissional_id=sessao.profissional_id,
            sala_id=sessao.sala_id,
            pacote_id=sessao.pacote_id,
            data_hora=sessao.data_hora,
            estado=novo_estado,
            evolucao_clinica=evolucao_clinica or sessao.evolucao_clinica,
            ativo=sessao.ativo,
            paciente_tipo=sessao.paciente_tipo
        )
        
        return nova_sessao
    
    def pode_transicionar(
        self,
        estado_atual: EstadoSessao,
        novo_estado: EstadoSessao
    ) -> bool:
        """
        Verifica se uma transição entre dois estados é permitida.
        
        Args:
            estado_atual: Estado atual
            novo_estado: Novo estado desejado
            
        Returns:
            bool: True se a transição é permitida, False caso contrário
        """
        return novo_estado in self.TRANSICOES_VALIDAS.get(estado_atual, set())
    
    def get_fluxo_principal(self) -> List[EstadoSessao]:
        """
        Retorna o fluxo principal de estados.
        
        Returns:
            List[EstadoSessao]: Fluxo principal
        """
        return [
            EstadoSessao.AGENDADA,
            EstadoSessao.REALIZADA,
            EstadoSessao.EVOLUIDA,
            EstadoSessao.FATURADA
        ]
    
    def get_estados_finais(self) -> Set[EstadoSessao]:
        """
        Retorna os estados finais (que não permitem mais transições).
        
        Returns:
            Set[EstadoSessao]: Estados finais
        """
        return {
            EstadoSessao.FATURADA,
            EstadoSessao.CANCELADA_COM_AVISO,
            EstadoSessao.FALTA_SEM_AVISO,
            EstadoSessao.ATENDIMENTO_REDUZIDO
        }


class SessaoController:
    """
    Controller para gerenciar sessões com validação de estados.
    """
    
    def __init__(self):
        self.maquina_estados = MaquinaEstadosSessao()
    
    def agendar_sessao(
        self,
        paciente_id: int,
        profissional_id: int,
        sala_id: int,
        pacote_id: Optional[int],
        data_hora: datetime,
        paciente_tipo: str = "Particular"
    ) -> Sessao:
        """
        Cria uma nova sessão no estado Agendada.
        
        Args:
            paciente_id: ID do paciente
            profissional_id: ID do profissional
            sala_id: ID da sala
            pacote_id: ID do pacote (opcional)
            data_hora: Data e hora da sessão
            paciente_tipo: Tipo do paciente (Particular ou Convênio)
            
        Returns:
            Sessao: Nova sessão criada
        """
        return Sessao(
            id=0,  # ID será gerado pelo banco
            paciente_id=paciente_id,
            profissional_id=profissional_id,
            sala_id=sala_id,
            pacote_id=pacote_id,
            data_hora=data_hora,
            estado=EstadoSessao.AGENDADA,
            evolucao_clinica=None,
            ativo=True,
            paciente_tipo=paciente_tipo
        )
    
    def realizar_sessao(self, sessao: Sessao) -> Sessao:
        """
        Transiciona uma sessão de Agendada para Realizada.
        
        Args:
            sessao: Sessão a ser realizada
            
        Returns:
            Sessao: Sessão atualizada
            
        Raises:
            TransicaoInvalidaError: Se a transição não é permitida
        """
        return self.maquina_estados.transicionar(sessao, EstadoSessao.REALIZADA)
    
    def registrar_evolucao(self, sessao: Sessao, evolucao_clinica: str) -> Sessao:
        """
        Transiciona uma sessão de Realizada para Evoluída.
        
        Args:
            sessao: Sessão a ser evoluída
            evolucao_clinica: Texto da evolução clínica
            
        Returns:
            Sessao: Sessão atualizada
            
        Raises:
            TransicaoInvalidaError: Se a transição não é permitida
        """
        return self.maquina_estados.transicionar(
            sessao, 
            EstadoSessao.EVOLUIDA,
            evolucao_clinica=evolucao_clinica
        )
    
    def faturar_sessao(self, sessao: Sessao) -> Sessao:
        """
        Transiciona uma sessão de Evoluída para Faturada.
        
        Args:
            sessao: Sessão a ser faturada
            
        Returns:
            Sessao: Sessão atualizada
            
        Raises:
            TransicaoInvalidaError: Se a transição não é permitida (ex: sem evolução clínica)
        """
        return self.maquina_estados.transicionar(sessao, EstadoSessao.FATURADA)
    
    def cancelar_com_aviso(self, sessao: Sessao, data_aviso: datetime) -> Sessao:
        """
        Transiciona uma sessão de Agendada para Cancelada com aviso.
        
        Args:
            sessao: Sessão a ser cancelada
            data_aviso: Data do aviso de cancelamento
            
        Returns:
            Sessao: Sessão atualizada
            
        Raises:
            TransicaoInvalidaError: Se o aviso não foi dado com 24h de antecedência
        """
        return self.maquina_estados.transicionar(
            sessao, 
            EstadoSessao.CANCELADA_COM_AVISO,
            data_aviso=data_aviso
        )
    
    def registrar_falta_sem_aviso(self, sessao: Sessao) -> Sessao:
        """
        Transiciona uma sessão de Agendada para Falta sem aviso.
        
        Args:
            sessao: Sessão com falta sem aviso
            
        Returns:
            Sessao: Sessão atualizada
        """
        return self.maquina_estados.transicionar(sessao, EstadoSessao.FALTA_SEM_AVISO)
    
    def registrar_atendimento_reduzido(
        self, 
        sessao: Sessao, 
        atraso_minutos: int
    ) -> Sessao:
        """
        Transiciona uma sessão para Atendimento reduzido (atraso > 15 min).
        
        Args:
            sessao: Sessão com atraso
            atraso_minutos: Minutos de atraso
            
        Returns:
            Sessao: Sessão atualizada
            
        Raises:
            TransicaoInvalidaError: Se o atraso não é superior a 15 minutos
        """
        return self.maquina_estados.transicionar(
            sessao,
            EstadoSessao.ATENDIMENTO_REDUZIDO,
            atraso_minutos=atraso_minutos
        )


# ============================================
# Funções de Validação Adicionais
# ============================================

def validar_capacidade_sala(sala_id: int, data_hora: datetime, sessao_id_excluir: int = None) -> bool:
    """
    Valida se uma sala tem capacidade para uma nova sessão (RN-04).
    
    Args:
        sala_id: ID da sala
        data_hora: Data e hora da sessão
        sessao_id_excluir: ID da sessão a ser excluída da contagem (para atualização)
        
    Returns:
        bool: True se a sala tem capacidade, False caso contrário
    """
    # Implementação simplificada - na prática, isso seria uma query ao banco
    # Por enquanto, retornamos True para não bloquear o fluxo
    return True


def validar_conflito_profissional(profissional_id: int, data_hora: datetime, sessao_id_excluir: int = None) -> bool:
    """
    Valida se um profissional não tem conflitos de horário (RN-05).
    
    Args:
        profissional_id: ID do profissional
        data_hora: Data e hora da sessão
        sessao_id_excluir: ID da sessão a ser excluída da contagem (para atualização)
        
    Returns:
        bool: True se não há conflitos, False caso contrário
    """
    # Implementação simplificada - na prática, isso seria uma query ao banco
    return True


def validar_pacote_valido(pacote_id: int) -> bool:
    """
    Valida se um pacote está válido (não expirado e com saldo) (RN-01, RN-07).
    
    Args:
        pacote_id: ID do pacote
        
    Returns:
        bool: True se o pacote é válido, False caso contrário
    """
    # Implementação simplificada - na prática, isso seria uma query ao banco
    return True


# ============================================
# Exemplo de Uso
# ============================================

if __name__ == "__main__":
    # Criar controller
    controller = SessaoController()
    
    # Data de referência para os exemplos
    hoje = datetime.now()
    amanha = hoje + timedelta(days=1)
    daqui_2_dias = hoje + timedelta(days=2)
    
    print("=== Exemplo de Uso da Máquina de Estados ===\n")
    
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
    sessao = controller.registrar_evolucao(sessao, "Paciente apresentou melhora significativa.")
    print(f"3. Sessão evoluída: {sessao.estado.name}")
    
    # Faturar sessão
    sessao = controller.faturar_sessao(sessao)
    print(f"4. Sessão faturada: {sessao.estado.name}")
    
    print("\n=== Testes de Transições Inválidas ===\n")
    
    # Teste 1: Tentar faturar uma sessão realizada (sem evolução)
    try:
        sessao_test = controller.agendar_sessao(1, 1, 1, 1, amanha, "Convênio")
        sessao_test = controller.realizar_sessao(sessao_test)
        sessao_test = controller.faturar_sessao(sessao_test)  # Deve falhar
    except TransicaoInvalidaError as e:
        print(f"✓ Teste 1: {e}")
    
    # Teste 2: Tentar faturar uma sessão de convênio sem evolução
    try:
        sessao_test = controller.agendar_sessao(1, 1, 1, 1, amanha, "Convênio")
        sessao_test = controller.realizar_sessao(sessao_test)
        sessao_test = controller.registrar_evolucao(sessao_test, "")  # Evolução vazia
        sessao_test = controller.faturar_sessao(sessao_test)  # Deve falhar
    except TransicaoInvalidaError as e:
        print(f"✓ Teste 2: {e}")
    
    # Teste 3: Tentar faturar uma sessão com atendimento reduzido
    try:
        sessao_test = controller.agendar_sessao(1, 1, 1, 1, amanha, "Convênio")
        sessao_test = controller.registrar_atendimento_reduzido(sessao_test, 20)  # 20 min de atraso
        sessao_test = controller.faturar_sessao(sessao_test)  # Deve falhar
    except TransicaoInvalidaError as e:
        print(f"✓ Teste 3: {e}")
    
    # Teste 4: Tentar alterar falta sem aviso para realizada
    try:
        sessao_test = controller.agendar_sessao(1, 1, 1, 1, amanha, "Particular")
        sessao_test = controller.registrar_falta_sem_aviso(sessao_test)
        sessao_test = controller.realizar_sessao(sessao_test)  # Deve falhar
    except TransicaoInvalidaError as e:
        print(f"✓ Teste 4: {e}")
    
    print("\n=== Testes de Transições Válidas ===\n")
    
    # Teste 5: Cancelamento com aviso (24h antes)
    try:
        sessao_test = controller.agendar_sessao(1, 1, 1, 1, daqui_2_dias, "Particular")
        sessao_test = controller.cancelar_com_aviso(sessao_test, hoje)  # Aviso hoje para sessão daqui a 2 dias
        print(f"✓ Teste 5: Cancelamento com aviso válido: {sessao_test.estado.name}")
    except TransicaoInvalidaError as e:
        print(f"✗ Teste 5 falhou: {e}")
    
    # Teste 6: Faturamento de sessão de convênio com evolução
    try:
        sessao_test = controller.agendar_sessao(1, 1, 1, 1, amanha, "Convênio")
        sessao_test = controller.realizar_sessao(sessao_test)
        sessao_test = controller.registrar_evolucao(sessao_test, "Evolução detalhada")
        sessao_test = controller.faturar_sessao(sessao_test)
        print(f"✓ Teste 6: Faturamento de convênio com evolução: {sessao_test.estado.name}")
    except TransicaoInvalidaError as e:
        print(f"✗ Teste 6 falhou: {e}")
