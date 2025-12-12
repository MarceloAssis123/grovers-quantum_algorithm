"""
Implementação do circuito do Algoritmo de Grover.

Este módulo constrói o circuito quântico de Grover para buscar
a senha correta em um espaço de 2 qubits (4 possibilidades).
"""

from qiskit import QuantumCircuit


def build_grover_2bit_circuit() -> QuantumCircuit:
    """
    Constrói o circuito do algoritmo de Grover para buscar a senha |11⟩
    em um espaço de busca de 2 qubits.
    
    O circuito implementa:
    1. Superposição inicial (Hadamard gates)
    2. Oracle que marca o estado |11⟩
    3. Difusor de Grover (amplificação de amplitude)
    4. Medição final
    
    Para N=4 (2 qubits), apenas 1 iteração de Grover é necessária,
    pois π/4 * √4 ≈ 1.57 ≈ 1 iteração.
    
    Returns:
        QuantumCircuit: Circuito quântico de Grover pronto para execução
    
    Example:
        >>> circuit = build_grover_2bit_circuit()
        >>> print(circuit)
        >>> # Executar em QPU ou simulador
    """
    # Criar circuito com 2 qubits
    qc = QuantumCircuit(2, name='Grover_2bit')
    
    # ====================================================
    # PASSO 1: SUPERPOSIÇÃO INICIAL
    # ====================================================
    # Aplicar Hadamard em ambos qubits para criar superposição uniforme
    # |00⟩ → (|00⟩ + |01⟩ + |10⟩ + |11⟩) / 2
    qc.h([0, 1])
    qc.barrier(label='Superposição')
    
    # ====================================================
    # PASSO 2: ORACLE
    # ====================================================
    # Marcar o estado alvo |11⟩ com uma fase negativa
    # O gate CZ aplica -1 apenas quando ambos qubits são |1⟩
    qc.cz(0, 1)
    qc.barrier(label='Oracle |11⟩')
    
    # ====================================================
    # PASSO 3: DIFUSOR DE GROVER
    # ====================================================
    # O difusor amplifica a amplitude do estado marcado
    # Implementação: H → X → Multi-controlled-Z → X → H
    
    # 3.1: Aplicar Hadamard
    qc.h([0, 1])
    
    # 3.2: Aplicar X (NOT) - inverte para |00⟩ ser o estado de referência
    qc.x([0, 1])
    
    # 3.3: Multi-controlled-Z (CZ controlado)
    # Para 2 qubits: H-CX-H implementa CZ
    qc.h(1)
    qc.cx(0, 1)
    qc.h(1)
    
    # 3.4: Aplicar X novamente (desfazer inversão)
    qc.x([0, 1])
    
    # 3.5: Aplicar Hadamard final
    qc.h([0, 1])
    qc.barrier(label='Difusor')
    
    # ====================================================
    # PASSO 4: MEDIÇÃO
    # ====================================================
    # Medir todos os qubits
    qc.measure_all()
    
    return qc


def print_circuit_info(circuit: QuantumCircuit) -> None:
    """
    Imprime informações sobre o circuito Grover
    
    Args:
        circuit: Circuito quântico a analisar
    """
    print("=== Informações do Circuito Grover ===\n")
    print(f"Nome: {circuit.name}")
    print(f"Número de qubits: {circuit.num_qubits}")
    print(f"Número de bits clássicos: {circuit.num_clbits}")
    print(f"Profundidade: {circuit.depth()}")
    print(f"Número de operações: {len(circuit.data)}")
    
    # Contar tipos de gates
    gate_counts = {}
    for instruction in circuit.data:
        gate_name = instruction.operation.name
        gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
    
    print("\nGates utilizados:")
    for gate, count in sorted(gate_counts.items()):
        print(f"  - {gate}: {count}")
    
    print("\n" + "="*40 + "\n")


def visualize_circuit() -> None:
    """
    Cria e visualiza o circuito Grover (modo texto)
    """
    circuit = build_grover_2bit_circuit()
    
    print("\n" + "="*60)
    print("CIRCUITO DO ALGORITMO DE GROVER (2 qubits)")
    print("Objetivo: Encontrar a senha |11⟩")
    print("="*60 + "\n")
    
    # Imprimir informações
    print_circuit_info(circuit)
    
    # Desenhar o circuito (modo texto)
    print("Diagrama do Circuito:\n")
    print(circuit.draw(output='text', fold=-1))
    print("\n" + "="*60 + "\n")
    
    print("Estados do algoritmo:")
    print("  1. Inicial: |00⟩")
    print("  2. Após Hadamard: (|00⟩ + |01⟩ + |10⟩ + |11⟩) / 2")
    print("  3. Após Oracle: (|00⟩ + |01⟩ + |10⟩ - |11⟩) / 2")
    print("  4. Após Difusor: ≈ |11⟩ (estado alvo amplificado)")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Demonstração do circuito
    visualize_circuit()

