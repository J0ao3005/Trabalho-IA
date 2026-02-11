import os
import re 
import data_instance
import manual_solver 
import visualization 

def main():
    PASTA_INSTANCIAS = "instances" 

    if not os.path.exists(PASTA_INSTANCIAS):
        print(f"ERRO: A pasta '{PASTA_INSTANCIAS}' não existe.")
        return

    arquivos = [f for f in os.listdir(PASTA_INSTANCIAS) if f.endswith('.ros')]
    
    def extrair_numero(nome_arquivo):

        numeros = re.findall(r'\d+', nome_arquivo)
        return int(numeros[0]) if numeros else 0
    

    arquivos.sort(key=extrair_numero)

    if not arquivos:
        print("Nenhum arquivo encontrado.")
        return

    print("\n=== SOLVER MANUAL CSP (BACKTRACKING) ===")
    for i, arq in enumerate(arquivos):
        print(f" [{i+1}] {arq}")
    
    try:
        opt = input("\nEscolha o número do arquivo: ")
        idx = int(opt) - 1
        arquivo = arquivos[idx]
    except:
        print("Opção inválida.")
        return


    caminho = os.path.join(PASTA_INSTANCIAS, arquivo)
    print(f"\nLendo arquivo: {arquivo} ...")
    
    try:
        data = data_instance.read_ros_instance(caminho)
        print(f"Leitura OK! Encontrados {len(data['employees'])} funcionários.")
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return
    
    try:
        dias_input = input("Quantos dias deseja resolver? (Recomendado: 7): ")
        dias = int(dias_input)
    except:
        dias = 7

    solver = manual_solver.ManualSolver(data)
    found, solution, tempo, nos = solver.solve(limit_days=dias)

    print("\n" + "="*50)
    if found:
        print(f"SOLUÇÃO ENCONTRADA!")
        print(f"Tempo: {tempo:.4f} segundos")
        print(f"Nós (estados) visitados: {nos}")
        print("-" * 50)
        
        # Gera o gráfico
        visualization.salvar_imagem_escala(solution, data['employees'], dias, data['shift_types'])
        
    else:
        print(f"NENHUMA SOLUÇÃO ENCONTRADA.")
        print(f"Tempo: {tempo:.4f}s | Nós: {nos}")
        print("Dica: Tente reduzir o número de dias ou verificar a demanda.")

if __name__ == "__main__":
    main()