"""
Funções auxiliares para conexão com IBM Quantum e gerenciamento de backends.
"""

import os
from typing import Optional, List
from dotenv import load_dotenv
from qiskit_ibm_runtime import QiskitRuntimeService


def load_ibm_credentials() -> tuple[str, str]:
    """
    Carrega as credenciais IBM Quantum do arquivo .env
    
    Returns:
        tuple: (IBM_API_KEY, QISKIT_IBM_INSTANCE)
    
    Raises:
        ValueError: Se as credenciais não estiverem configuradas
    """
    load_dotenv()
    
    api_key = os.getenv('IBM_API_KEY')
    instance = os.getenv('QISKIT_IBM_INSTANCE')
    
    if not api_key:
        raise ValueError(
            "IBM_API_KEY não encontrada no .env\n"
            "Configure sua API key em: https://quantum.ibm.com/"
        )
    
    if not instance:
        raise ValueError(
            "QISKIT_IBM_INSTANCE não encontrada no .env\n"
            "Configure seu CRN da instância em: https://quantum.ibm.com/"
        )
    
    return api_key, instance


def get_qiskit_service() -> QiskitRuntimeService:
    """
    Inicializa e retorna o serviço Qiskit Runtime com as credenciais do .env
    
    Returns:
        QiskitRuntimeService: Serviço conectado ao IBM Quantum
    
    Raises:
        ValueError: Se as credenciais não estiverem configuradas
        Exception: Se houver erro ao conectar com IBM Quantum
    """
    api_key, instance = load_ibm_credentials()
    
    try:
        # Tenta carregar serviço salvo primeiro
        service = QiskitRuntimeService(channel="ibm_quantum", instance=instance)
        print(f"✓ Conectado ao IBM Quantum (instance: {instance})")
        return service
    except Exception as e:
        # Se falhar, tenta salvar as credenciais e reconectar
        print(f"Salvando credenciais IBM Quantum...")
        try:
            QiskitRuntimeService.save_account(
                channel="ibm_quantum",
                token=api_key,
                instance=instance,
                overwrite=True
            )
            service = QiskitRuntimeService(channel="ibm_quantum", instance=instance)
            print(f"✓ Credenciais salvas e conectado ao IBM Quantum")
            return service
        except Exception as save_error:
            raise Exception(
                f"Erro ao conectar com IBM Quantum: {save_error}\n"
                f"Verifique suas credenciais no .env"
            )


def list_available_qpus(service: QiskitRuntimeService) -> List:
    """
    Lista todos os backends QPU (hardware real) disponíveis
    
    Args:
        service: Serviço Qiskit Runtime conectado
    
    Returns:
        List: Lista de backends QPU disponíveis
    """
    print("\n=== Backends QPU Disponíveis ===\n")
    
    # Filtrar apenas backends reais (QPU)
    qpu_backends = []
    
    for backend in service.backends():
        # Verificar se é hardware real
        if hasattr(backend, 'simulator') and not backend.simulator:
            qpu_backends.append(backend)
            
            # Informações do backend
            num_qubits = backend.num_qubits
            status = backend.status()
            pending_jobs = status.pending_jobs if hasattr(status, 'pending_jobs') else 'N/A'
            operational = status.operational if hasattr(status, 'operational') else True
            
            status_emoji = "✓" if operational else "✗"
            
            print(f"{status_emoji} {backend.name}")
            print(f"   Qubits: {num_qubits}")
            print(f"   Fila: {pending_jobs} jobs pendentes")
            print(f"   Operacional: {'Sim' if operational else 'Não'}")
            print()
    
    if not qpu_backends:
        print("⚠ Nenhum QPU disponível na sua conta.")
        print("Verifique seu plano em: https://quantum.ibm.com/")
    
    return qpu_backends


def select_best_qpu(
    service: QiskitRuntimeService,
    preferred_qpus: Optional[List[str]] = None,
    min_qubits: int = 2
):
    """
    Seleciona o melhor QPU disponível baseado em preferências e fila
    
    Args:
        service: Serviço Qiskit Runtime conectado
        preferred_qpus: Lista de nomes de QPUs preferidos (em ordem de preferência)
        min_qubits: Número mínimo de qubits necessários
    
    Returns:
        Backend: Melhor backend QPU disponível
    
    Raises:
        ValueError: Se nenhum QPU adequado for encontrado
    """
    # Listar todos os QPUs disponíveis
    available_qpus = []
    
    for backend in service.backends():
        # Verificar se é hardware real
        if hasattr(backend, 'simulator') and not backend.simulator:
            # Verificar requisitos mínimos
            if backend.num_qubits >= min_qubits:
                status = backend.status()
                operational = status.operational if hasattr(status, 'operational') else True
                
                if operational:
                    pending = status.pending_jobs if hasattr(status, 'pending_jobs') else 0
                    available_qpus.append({
                        'backend': backend,
                        'name': backend.name,
                        'qubits': backend.num_qubits,
                        'pending_jobs': pending
                    })
    
    if not available_qpus:
        raise ValueError(
            f"Nenhum QPU operacional encontrado com pelo menos {min_qubits} qubits.\n"
            "Verifique seu acesso em: https://quantum.ibm.com/"
        )
    
    # Se há QPUs preferidos, tentar usá-los primeiro
    if preferred_qpus:
        for preferred_name in preferred_qpus:
            for qpu_info in available_qpus:
                if qpu_info['name'] == preferred_name:
                    print(f"\n✓ Selecionado QPU preferido: {preferred_name}")
                    print(f"  Qubits: {qpu_info['qubits']}")
                    print(f"  Fila: {qpu_info['pending_jobs']} jobs\n")
                    return qpu_info['backend']
    
    # Caso contrário, selecionar o com menor fila
    best_qpu = min(available_qpus, key=lambda x: x['pending_jobs'])
    
    print(f"\n✓ Selecionado QPU com menor fila: {best_qpu['name']}")
    print(f"  Qubits: {best_qpu['qubits']}")
    print(f"  Fila: {best_qpu['pending_jobs']} jobs\n")
    
    return best_qpu['backend']


def validate_connection() -> bool:
    """
    Valida a conexão com IBM Quantum e lista QPUs disponíveis
    
    Returns:
        bool: True se a conexão foi bem-sucedida e há QPUs disponíveis
    """
    try:
        print("Testando conexão com IBM Quantum...\n")
        
        # Carregar credenciais
        api_key, instance = load_ibm_credentials()
        print(f"✓ Credenciais carregadas do .env")
        
        # Conectar ao serviço
        service = get_qiskit_service()
        
        # Listar QPUs disponíveis
        qpus = list_available_qpus(service)
        
        if qpus:
            print(f"✓ Conexão bem-sucedida! {len(qpus)} QPU(s) disponível(is).\n")
            return True
        else:
            print("⚠ Conexão estabelecida, mas nenhum QPU disponível.\n")
            return False
            
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}\n")
        return False


if __name__ == "__main__":
    # Teste de conexão
    validate_connection()

