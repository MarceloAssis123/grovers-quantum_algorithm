"""
Execução do Algoritmo de Grover em QPU real da IBM.

Este script executa o circuito de Grover diretamente em hardware quântico real,
analisa os resultados e compara com o resultado ideal.
"""

import json
import os
from pathlib import Path
from typing import Dict, Tuple
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2, Session

from grover.circuits import build_grover_2bit_circuit, print_circuit_info
from grover.utils import get_qiskit_service, select_best_qpu


def load_config() -> Dict:
    """
    Carrega configurações do arquivo backend_names.json
    
    Returns:
        Dict: Configurações de execução
    """
    config_path = Path(__file__).parent.parent / 'config' / 'backend_names.json'
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return config


def run_grover_on_qpu() -> Tuple[Dict[str, int], str, str]:
    """
    Executa o algoritmo de Grover em um QPU real da IBM
    
    Returns:
        Tuple: (counts, job_id, backend_name)
            - counts: Dicionário com contagens de medições
            - job_id: ID do job para referência
            - backend_name: Nome do backend QPU usado
    
    Raises:
        Exception: Se houver erro na execução
    """
    print("\n" + "="*70)
    print("EXECUTANDO ALGORITMO DE GROVER EM QPU REAL DA IBM")
    print("="*70 + "\n")
    
    # 1. Carregar configuração
    print("📋 Carregando configurações...")
    config = load_config()
    print(f"   Shots: {config['shots']}")
    print(f"   Optimization level: {config['optimization_level']}")
    print(f"   QPUs preferidos: {', '.join(config['preferred_qpus'])}\n")
    
    # 2. Conectar ao IBM Quantum
    print("🔌 Conectando ao IBM Quantum...")
    service = get_qiskit_service()
    
    # 3. Selecionar melhor QPU disponível
    print("🔍 Selecionando melhor QPU disponível...")
    backend = select_best_qpu(
        service, 
        config['preferred_qpus'],
        min_qubits=2
    )
    
    # 4. Construir circuito
    print("🔧 Construindo circuito de Grover...")
    circuit = build_grover_2bit_circuit()
    print_circuit_info(circuit)
    
    # 5. Transpilar para o backend
    print(f"⚙️  Transpilando circuito para {backend.name}...")
    t_circuit = transpile(
        circuit, 
        backend, 
        optimization_level=config['optimization_level']
    )
    print(f"   Circuito transpilado:")
    print(f"   - Profundidade: {t_circuit.depth()}")
    print(f"   - Operações: {len(t_circuit.data)}\n")
    
    # 6. Executar com Session e SamplerV2
    print(f"🚀 Iniciando execução no QPU {backend.name}...")
    print(f"   Aguarde: o tempo de fila pode variar de minutos a horas...")
    print(f"   Você pode fechar este programa - use o Job ID para recuperar resultados.\n")
    
    with Session(service=service, backend=backend) as session:
        sampler = SamplerV2(session=session)
        job = sampler.run([t_circuit], shots=config['shots'])
        
        job_id = job.job_id()
        print(f"✓ Job submetido com sucesso!")
        print(f"   Job ID: {job_id}")
        print(f"   Backend: {backend.name}\n")
        
        print("⏳ Aguardando execução no QPU...")
        print("   (Pressione Ctrl+C para cancelar a espera, o job continuará rodando)\n")
        
        try:
            result = job.result()[0]
            counts = result.data.meas.get_counts()
            
            print("✓ Execução concluída com sucesso!\n")
            
            return counts, job_id, backend.name
            
        except KeyboardInterrupt:
            print("\n⚠ Espera cancelada pelo usuário.")
            print(f"   Job {job_id} continua executando no QPU.")
            print(f"   Use retrieve_job('{job_id}') para recuperar resultados depois.\n")
            raise
        except Exception as e:
            print(f"\n✗ Erro durante execução: {e}\n")
            raise


def analyze_results(counts: Dict[str, int], backend_name: str, expected_state: str = '11') -> float:
    """
    Analisa os resultados da execução no QPU
    
    Args:
        counts: Dicionário com contagens de medições
        backend_name: Nome do backend usado
        expected_state: Estado esperado (padrão: '11')
    
    Returns:
        float: Fidelidade (probabilidade do estado correto)
    """
    total_shots = sum(counts.values())
    
    print("="*70)
    print("ANÁLISE DE RESULTADOS")
    print("="*70 + "\n")
    
    print(f"Backend: {backend_name}")
    print(f"Total de medições: {total_shots}\n")
    
    # Calcular fidelidade (probabilidade do estado correto)
    correct_count = counts.get(expected_state, 0)
    fidelity = correct_count / total_shots
    
    # Distribuição de resultados
    print("📊 Distribuição de resultados (ordenado por frequência):\n")
    
    for state, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        prob = count / total_shots
        bar_length = int(prob * 50)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        
        marker = "← ALVO" if state == expected_state else ""
        print(f"|{state}⟩: {count:4d} ({prob*100:5.2f}%) {bar} {marker}")
    
    print(f"\n{'='*70}")
    print(f"FIDELIDADE: {fidelity*100:.2f}% (estado |{expected_state}⟩)")
    print(f"{'='*70}\n")
    
    # Interpretação dos resultados
    print("💡 Interpretação:\n")
    
    if fidelity >= 0.80:
        print("   ✓ Excelente! Resultado muito próximo do ideal.")
        print("     O algoritmo de Grover funcionou bem mesmo com ruído quântico.")
    elif fidelity >= 0.60:
        print("   ✓ Bom resultado considerando o ruído quântico real.")
        print("     O estado correto foi amplificado com sucesso.")
    elif fidelity >= 0.40:
        print("   ⚠ Resultado moderado - ruído quântico significativo.")
        print("     O algoritmo funcionou parcialmente, mas o ruído afetou a precisão.")
    else:
        print("   ⚠ Resultado abaixo do esperado.")
        print("     Alto nível de ruído ou erro na execução.")
    
    print(f"\n   Comparação com ideal:")
    print(f"   - Resultado ideal: |{expected_state}⟩ com ~100%")
    print(f"   - QPU real: |{expected_state}⟩ com {fidelity*100:.2f}%")
    print(f"   - Degradação: {(1-fidelity)*100:.2f}% devido a ruído quântico")
    
    print("\n" + "="*70 + "\n")
    
    return fidelity


def retrieve_job(job_id: str, service: QiskitRuntimeService = None) -> Dict[str, int]:
    """
    Recupera resultados de um job anterior
    
    Args:
        job_id: ID do job a recuperar
        service: Serviço Qiskit (opcional, será criado se não fornecido)
    
    Returns:
        Dict: Contagens de medições
    """
    if service is None:
        service = get_qiskit_service()
    
    print(f"\n🔍 Recuperando job {job_id}...")
    
    try:
        job = service.job(job_id)
        status = job.status()
        
        print(f"   Status: {status}\n")
        
        if status.name == 'DONE':
            result = job.result()[0]
            counts = result.data.meas.get_counts()
            print("✓ Resultados recuperados com sucesso!\n")
            return counts
        else:
            print(f"⏳ Job ainda não concluído. Status: {status.name}\n")
            return None
            
    except Exception as e:
        print(f"✗ Erro ao recuperar job: {e}\n")
        raise


def save_results(counts: Dict[str, int], job_id: str, backend_name: str, fidelity: float):
    """
    Salva os resultados em um arquivo para referência futura
    
    Args:
        counts: Contagens de medições
        job_id: ID do job
        backend_name: Nome do backend
        fidelity: Fidelidade do resultado
    """
    results_dir = Path(__file__).parent.parent / 'results'
    results_dir.mkdir(exist_ok=True)
    
    result_file = results_dir / f'grover_result_{job_id}.json'
    
    result_data = {
        'job_id': job_id,
        'backend': backend_name,
        'counts': counts,
        'fidelity': fidelity,
        'total_shots': sum(counts.values()),
        'expected_state': '11'
    }
    
    with open(result_file, 'w') as f:
        json.dump(result_data, f, indent=2)
    
    print(f"💾 Resultados salvos em: {result_file}\n")


def main():
    """
    Função principal - executa o algoritmo de Grover no QPU
    """
    try:
        # Executar no QPU
        counts, job_id, backend_name = run_grover_on_qpu()
        
        # Analisar resultados
        fidelity = analyze_results(counts, backend_name)
        
        # Salvar resultados
        save_results(counts, job_id, backend_name, fidelity)
        
        print(f"✓ Execução completa!")
        print(f"   Job ID para referência: {job_id}\n")
        
        return counts, job_id, fidelity
        
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.\n")
        return None
    except Exception as e:
        print(f"\n✗ Erro: {e}\n")
        raise


if __name__ == "__main__":
    main()

