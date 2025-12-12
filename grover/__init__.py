"""
Implementação do Algoritmo de Grover para execução em QPU real da IBM.

Este módulo fornece ferramentas para construir e executar o algoritmo de Grover
diretamente em hardware quântico real da IBM Quantum.
"""

__version__ = "1.0.0"
__author__ = "Grover QPU Implementation"

from grover.circuits import build_grover_2bit_circuit
from grover.utils import (
    load_ibm_credentials,
    get_qiskit_service,
    list_available_qpus,
    select_best_qpu
)

__all__ = [
    'build_grover_2bit_circuit',
    'load_ibm_credentials',
    'get_qiskit_service',
    'list_available_qpus',
    'select_best_qpu'
]

