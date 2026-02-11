import matplotlib


matplotlib.use('Agg') 

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

def salvar_imagem_escala(solution, employees, days_count, shifts):
    print(">>> Gerando imagem da escala (escala_visual.png)...")
    
    # 1. Configuração de Cores
    cores_turnos = {
        'E': '#ff9999',  # Vermelho Claro
        'L': '#66b3ff',  # Azul Claro
        'D': '#99ff99',  # Verde Claro
        'N': '#c2c2f0',  # Roxo
        '-': '#f0f0f0',  # Cinza (Folga)
        '.': '#f0f0f0'   # Cinza (Folga visual)
    }
    
    # Cores aleatórias para turnos extras
    for s in shifts:
        if s not in cores_turnos:
            cores_turnos[s] = "#" + "".join([random.choice('89ABCDEF') for i in range(6)])

    # 2. Configurações do Gráfico
    largura_fig = max(10, days_count * 0.6)
    altura_fig = max(4, len(employees) * 0.6)
    
    fig, ax = plt.subplots(figsize=(largura_fig, altura_fig))
    
    # 3. Desenhar a Grade
    for i, emp in enumerate(employees):
        y = len(employees) - 1 - i
        
        for d in range(days_count):
            shift = solution.get((emp, d), '-')
            if shift == '.': shift = '-' 
            
            cor = cores_turnos.get(shift, '#ffffff')
            
            # Retângulo
            rect = patches.Rectangle(
                (d, y), 1, 1, 
                linewidth=1, edgecolor='white', facecolor=cor
            )
            ax.add_patch(rect)
            
            # Texto
            texto_cor = 'black' if shift != '-' else '#bbbbbb'
            ax.text(
                d + 0.5, y + 0.5, shift, 
                ha='center', va='center', fontsize=9, 
                color=texto_cor, fontweight='bold'
            )

    # 4. Eixos e Legendas
    ax.set_xlim(0, days_count)
    ax.set_ylim(0, len(employees))
    
    ax.set_xticks([x + 0.5 for x in range(days_count)])
    ax.set_xticklabels([f"{d+1}" for d in range(days_count)], fontsize=8)
    ax.set_xlabel("Dias", fontsize=10)
    
    ax.set_yticks([y + 0.5 for y in range(len(employees))])
    ax.set_yticklabels(employees[::-1], fontsize=10, fontweight='bold')
    
    plt.title(f"Escala Gerada ({days_count} dias)", fontsize=14, pad=15)
    
    # Limpeza visual
    ax.tick_params(left=False, bottom=False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # 5. Salvar
    plt.savefig("escala_visual.png", bbox_inches='tight', dpi=150)
    plt.close()
    print("Imagem salva com sucesso!")