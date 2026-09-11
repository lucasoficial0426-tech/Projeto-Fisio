"""
Módulo de Venda de Pacotes com Regra Temporal
Implementa a mudança contratual a partir de 01/11/2026 (RN-01)

Antes de 01/11/2026: Pacotes de 10 sessões com validade de 90 dias
A partir de 01/11/2026: Pacotes de 15 sessões com validade de 120 dias
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class TipoPacote(Enum):
    """Tipos de pacotes disponíveis"""
    PADRAO_10 = "10_sessoes_90_dias"  # Antes de 01/11/2026
    PADRAO_15 = "15_sessoes_120_dias"  # A partir de 01/11/2026


@dataclass
class Pacote:
    """Representa um pacote de sessões"""
    id: int
    paciente_id: int
    data_compra: date
    quantidade_sessoes: int
    sessoes_utilizadas: int = 0
    validade_dias: int = 90
    ativo: bool = True
    tipo: str = "10_sessoes_90_dias"
    
    def __post_init__(self):
        if isinstance(self.data_compra, str):
            self.data_compra = datetime.strptime(self.data_compra, "%Y-%m-%d").date()
    
    @property
    def data_vencimento(self) -> date:
        """Calcula a data de vencimento do pacote"""
        from datetime import timedelta
        return self.data_compra + timedelta(days=self.validade_dias)
    
    @property
    def expirado(self) -> bool:
        """Verifica se o pacote está expirado"""
        return date.today() > self.data_vencimento
    
    @property
    def saldo(self) -> int:
        """Retorna o saldo de sessões restantes"""
        return self.quantidade_sessoes - self.sessoes_utilizadas
    
    @property
    def pode_ser_usado(self) -> bool:
        """Verifica se o pacote pode ser usado para agendamento"""
        return self.ativo and not self.expirado and self.saldo > 0


class PacoteInvalidoError(Exception):
    """Exceção lançada quando um pacote é inválido"""
    def __init__(self, motivo: str, pacote_id: int = None):
        self.motivo = motivo
        self.pacote_id = pacote_id
        super().__init__(f"Pacote inválido: {motivo}" + (f" (ID: {pacote_id})" if pacote_id else ""))


class PacotesController:
    """
    Controller para gerenciar a venda e validação de pacotes.
    
    Implementa a regra temporal:
    - Antes de 01/11/2026: Pacotes de 10 sessões com 90 dias de validade
    - A partir de 01/11/2026: Pacotes de 15 sessões com 120 dias de validade
    """
    
    DATA_MUDANCA = date(2026, 11, 1)
    
    def __init__(self):
        """Inicializa o controller de pacotes"""
        pass
    
    def determinar_tipo_pacote(self, data_compra: date) -> TipoPacote:
        """
        Determina o tipo de pacote com base na data de compra.
        
        Args:
            data_compra: Data de compra do pacote
            
        Returns:
            TipoPacote: Tipo do pacote (10 ou 15 sessões)
        """
        if data_compra >= self.DATA_MUDANCA:
            return TipoPacote.PADRAO_15
        else:
            return TipoPacote.PADRAO_10
    
    def criar_pacote(
        self,
        paciente_id: int,
        data_compra: date,
        quantidade_sessoes: Optional[int] = None,
        validade_dias: Optional[int] = None
    ) -> Pacote:
        """
        Cria um novo pacote com base nas regras temporais.
        
        Args:
            paciente_id: ID do paciente
            data_compra: Data de compra do pacote
            quantidade_sessoes: Quantidade de sessões (opcional, usa padrão se None)
            validade_dias: Validade em dias (opcional, usa padrão se None)
            
        Returns:
            Pacote: Novo pacote criado
            
        Raises:
            PacoteInvalidoError: Se os parâmetros são inválidos
        """
        # Determina o tipo de pacote com base na data
        tipo_pacote = self.determinar_tipo_pacote(data_compra)
        
        # Define valores padrão com base no tipo
        if tipo_pacote == TipoPacote.PADRAO_10:
            qtd_padrao = 10
            validade_padrao = 90
        else:  # TipoPacote.PADRAO_15
            qtd_padrao = 15
            validade_padrao = 120
        
        # Usa valores padrão se não forem fornecidos
        qtd = quantidade_sessoes if quantidade_sessoes is not None else qtd_padrao
        validade = validade_dias if validade_dias is not None else validade_padrao
        
        # Valida os valores
        if qtd not in [10, 15]:
            raise PacoteInvalidoError(
                f"Quantidade de sessões deve ser 10 ou 15, não {qtd}",
                paciente_id
            )
        
        if validade not in [90, 120]:
            raise PacoteInvalidoError(
                f"Validade deve ser 90 ou 120 dias, não {validade}",
                paciente_id
            )
        
        # Verifica consistência entre quantidade e validade
        if (qtd == 10 and validade != 90) or (qtd == 15 and validade != 120):
            raise PacoteInvalidoError(
                f"Combinação inválida: {qtd} sessões com {validade} dias de validade",
                paciente_id
            )
        
        # Verifica se a combinação está de acordo com a data de compra
        if data_compra < self.DATA_MUDANCA:
            # Antes de 01/11/2026, só são permitidos pacotes de 10/90
            if qtd != 10 or validade != 90:
                raise PacoteInvalidoError(
                    f"Antes de {self.DATA_MUDANCA}, só são permitidos pacotes de 10 sessões/90 dias",
                    paciente_id
                )
        else:
            # A partir de 01/11/2026, só são permitidos pacotes de 15/120
            if qtd != 15 or validade != 120:
                raise PacoteInvalidoError(
                    f"A partir de {self.DATA_MUDANCA}, só são permitidos pacotes de 15 sessões/120 dias",
                    paciente_id
                )
        
        # Cria o pacote
        return Pacote(
            id=0,  # ID será gerado pelo banco
            paciente_id=paciente_id,
            data_compra=data_compra,
            quantidade_sessoes=qtd,
            sessoes_utilizadas=0,
            validade_dias=validade,
            ativo=True,
            tipo=f"{qtd}_sessoes_{validade}_dias"
        )
    
    def validar_pacote(self, pacote: Pacote) -> bool:
        """
        Valida se um pacote está válido para uso.
        
        Args:
            pacote: Pacote a ser validado
            
        Returns:
            bool: True se o pacote é válido, False caso contrário
        """
        # Verifica se está ativo
        if not pacote.ativo:
            return False
        
        # Verifica se está expirado
        if pacote.expirado:
            return False
        
        # Verifica se tem saldo
        if pacote.saldo <= 0:
            return False
        
        # Verifica consistência entre data de compra e tipo
        tipo_esperado = self.determinar_tipo_pacote(pacote.data_compra)
        
        if tipo_esperado == TipoPacote.PADRAO_10:
            if pacote.quantidade_sessoes != 10 or pacote.validade_dias != 90:
                return False
        else:  # TipoPacote.PADRAO_15
            if pacote.quantidade_sessoes != 15 or pacote.validade_dias != 120:
                return False
        
        return True
    
    def usar_sessao(self, pacote: Pacote) -> Pacote:
        """
        Registra o uso de uma sessão do pacote.
        
        Args:
            pacote: Pacote a ser atualizado
            
        Returns:
            Pacote: Pacote atualizado
            
        Raises:
            PacoteInvalidoError: Se o pacote não pode ser usado
        """
        if not self.validar_pacote(pacote):
            raise PacoteInvalidoError(
                f"Pacote não pode ser usado (expirado: {pacote.expirado}, saldo: {pacote.saldo})",
                pacote.id
            )
        
        # Atualiza o número de sessões utilizadas
        return Pacote(
            id=pacote.id,
            paciente_id=pacote.paciente_id,
            data_compra=pacote.data_compra,
            quantidade_sessoes=pacote.quantidade_sessoes,
            sessoes_utilizadas=pacote.sessoes_utilizadas + 1,
            validade_dias=pacote.validade_dias,
            ativo=pacote.ativo,
            tipo=pacote.tipo
        )
    
    def get_info_pacote(self, pacote: Pacote) -> dict:
        """
        Retorna informações detalhadas sobre um pacote.
        
        Args:
            pacote: Pacote a ser analisado
            
        Returns:
            dict: Informações do pacote
        """
        return {
            "id": pacote.id,
            "paciente_id": pacote.paciente_id,
            "data_compra": pacote.data_compra,
            "data_vencimento": pacote.data_vencimento,
            "quantidade_sessoes": pacote.quantidade_sessoes,
            "sessoes_utilizadas": pacote.sessoes_utilizadas,
            "saldo": pacote.saldo,
            "validade_dias": pacote.validade_dias,
            "ativo": pacote.ativo,
            "expirado": pacote.expirado,
            "pode_ser_usado": pacote.pode_ser_usado,
            "tipo": pacote.tipo
        }
    
    def listar_pacotes_paciente(self, paciente_id: int) -> List[Pacote]:
        """
        Lista todos os pacotes de um paciente.
        
        Args:
            paciente_id: ID do paciente
            
        Returns:
            List[Pacote]: Lista de pacotes do paciente
        """
        # Na implementação real, isso seria uma query ao banco
        # Por enquanto, retornamos uma lista vazia
        return []
    
    def get_pacote_ativo(self, paciente_id: int) -> Optional[Pacote]:
        """
        Retorna o pacote ativo de um paciente (se houver).
        
        Args:
            paciente_id: ID do paciente
            
        Returns:
            Optional[Pacote]: Pacote ativo ou None
        """
        pacotes = self.listar_pacotes_paciente(paciente_id)
        
        for pacote in pacotes:
            if self.validar_pacote(pacote):
                return pacote
        
        return None


# ============================================
# Funções Auxiliares
# ============================================

def formatar_data(data: date) -> str:
    """Formata uma data no formato dd/mm/yyyy"""
    return data.strftime("%d/%m/%Y")


def calcular_dias_restantes(pacote: Pacote) -> int:
    """Calcula os dias restantes até o vencimento do pacote"""
    from datetime import date
    hoje = date.today()
    vencimento = pacote.data_vencimento
    
    if hoje > vencimento:
        return 0
    
    return (vencimento - hoje).days


# ============================================
# Exemplo de Uso
# ============================================

if __name__ == "__main__":
    controller = PacotesController()
    
    print("=== Exemplo de Uso do Controller de Pacotes ===\n")
    
    # Criar pacote antes de 01/11/2026 (10 sessões, 90 dias)
    pacote_antigo = controller.criar_pacote(
        paciente_id=1,
        data_compra=date(2026, 10, 15),  # Antes de 01/11/2026
        quantidade_sessoes=10,
        validade_dias=90
    )
    print(f"Pacote criado (antes de 01/11/2026):")
    print(f"  - Quantidade: {pacote_antigo.quantidade_sessoes} sessões")
    print(f"  - Validade: {pacote_antigo.validade_dias} dias")
    print(f"  - Data de vencimento: {formatar_data(pacote_antigo.data_vencimento)}")
    print(f"  - Tipo: {pacote_antigo.tipo}")
    
    # Criar pacote a partir de 01/11/2026 (15 sessões, 120 dias)
    pacote_novo = controller.criar_pacote(
        paciente_id=2,
        data_compra=date(2026, 11, 1),  # A partir de 01/11/2026
        quantidade_sessoes=15,
        validade_dias=120
    )
    print(f"\nPacote criado (a partir de 01/11/2026):")
    print(f"  - Quantidade: {pacote_novo.quantidade_sessoes} sessões")
    print(f"  - Validade: {pacote_novo.validade_dias} dias")
    print(f"  - Data de vencimento: {formatar_data(pacote_novo.data_vencimento)}")
    print(f"  - Tipo: {pacote_novo.tipo}")
    
    # Tentar criar pacote com combinação inválida antes de 01/11/2026
    print("\n=== Testes de Validação ===\n")
    try:
        pacote_invalido = controller.criar_pacote(
            paciente_id=3,
            data_compra=date(2026, 10, 15),  # Antes de 01/11/2026
            quantidade_sessoes=15,  # Inválido para esta data
            validade_dias=120
        )
    except PacoteInvalidoError as e:
        print(f"✓ Teste 1: {e}")
    
    # Tentar criar pacote com combinação inválida a partir de 01/11/2026
    try:
        pacote_invalido = controller.criar_pacote(
            paciente_id=4,
            data_compra=date(2026, 11, 1),  # A partir de 01/11/2026
            quantidade_sessoes=10,  # Inválido para esta data
            validade_dias=90
        )
    except PacoteInvalidoError as e:
        print(f"✓ Teste 2: {e}")
    
    # Validar pacote
    print(f"\n✓ Teste 3: Pacote antigo válido: {controller.validar_pacote(pacote_antigo)}")
    print(f"✓ Teste 4: Pacote novo válido: {controller.validar_pacote(pacote_novo)}")
    
    # Usar sessão do pacote
    pacote_usado = controller.usar_sessao(pacote_antigo)
    print(f"\n✓ Teste 5: Pacote após usar 1 sessão:")
    print(f"  - Sessões utilizadas: {pacote_usado.sessoes_utilizadas}")
    print(f"  - Saldo: {pacote_usado.saldo}")
    
    # Tentar usar sessão de pacote expirado
    try:
        pacote_expirado = Pacote(
            id=100,
            paciente_id=5,
            data_compra=date(2025, 1, 1),  # Data muito antiga
            quantidade_sessoes=10,
            sessoes_utilizadas=5,
            validade_dias=90,
            ativo=True
        )
        controller.usar_sessao(pacote_expirado)
    except PacoteInvalidoError as e:
        print(f"\n✓ Teste 6: {e}")
    
    # Informações do pacote
    print(f"\n✓ Teste 7: Informações do pacote:")
    info = controller.get_info_pacote(pacote_antigo)
    for key, value in info.items():
        print(f"  - {key}: {value}")
