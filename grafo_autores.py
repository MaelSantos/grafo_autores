import pandas as pd
import itertools
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patheffects as path_effects

# =====================================================================
# CONFIGURAÇÃO DE VISUALIZAÇÃO: Alterne aqui facilmente!
# =====================================================================
# Escolha 'todos_proporcional' ou 'apenas_principais'
modo_visualizacao = 'todos_proporcional' 
# =====================================================================

# 1. Carregar os dados
df = pd.read_csv('Autores_SBES.csv', sep=';', encoding='latin1')

G = nx.Graph()
contagem_autores = {}

for autores_linha in df['Autores']:
    if pd.isna(autores_linha):
        continue
    lista_autores = [autor.strip() for autor in autores_linha.split(',')]
    
    for autor in lista_autores:
        contagem_autores[autor] = contagem_autores.get(autor, 0) + 1
        if not G.has_node(autor):
            G.add_node(autor)
            
    if len(lista_autores) > 1:
        pares = list(itertools.combinations(lista_autores, 2))
        for u, v in pares:
            if G.has_edge(u, v):
                G[u][v]['weight'] += 1
            else:
                G.add_edge(u, v, weight=1)

for autor, qtd in contagem_autores.items():
    G.nodes[autor]['artigos'] = qtd

# 2. Configuração da Área do Gráfico (Bem ampla para o texto circular)
fig, ax = plt.subplots(figsize=(18, 18))

# Ajuste de força (k=0.9) para manter os nós periféricos bem distribuídos
pos = nx.spring_layout(G, k=0.9, seed=42)

# Mapeamento de tamanhos e cores dos nós (Visual limpo e profissional)
tamanhos_nos = [G.nodes[node]['artigos'] * 90 for node in G]
cores_nos = ['#1f77b4' if G.nodes[node]['artigos'] >= 3 else '#aec7e8' for node in G]
pesos_arestas = [G[u][v]['weight'] * 1.0 for u, v in G.edges()]

# Desenhar a estrutura base da rede
nx.draw_networkx_nodes(G, pos, node_size=tamanhos_nos, node_color=cores_nos, edgecolors='#555555', linewidths=0.5, ax=ax)
nx.draw_networkx_edges(G, pos, width=pesos_arestas, edge_color='gray', alpha=0.18, ax=ax)

# Calcular o centro geométrico da rede para definir os lados esquerdo/direito
x_coords = [coords[0] for coords in pos.values()]
y_coords = [coords[1] for coords in pos.values()]
centro_x = np.mean(x_coords)
centro_y = np.mean(y_coords)

# 3. Posicionamento Circular com Lógica de Alternância Dinâmica
for node in G.nodes():
    artigos = G.nodes[node]['artigos']
    x, y = pos[node]
    
    # --- LOGICA DE ALTERNÂNCIA DE MODOS ---
    if modo_visualizacao == 'apenas_principais':
        # Ignora autores secundários (com menos de 3 artigos)
        if artigos < 3:
            continue
        tamanho_fonte = 30
        peso_fonte = 'bold'
        cor_fonte = '#1a1a1a'
        espessura_borda = 3.0
        recuo = 0.05
        
    else: # 'todos_proporcional'
        # Mostra todos, com tamanho dinâmico e gradual
        tamanho_fonte = 8 + (artigos * 3)
        if tamanho_fonte > 45: 
            tamanho_fonte = 45
        peso_fonte = 'bold' if artigos >= 3 else 'normal'
        cor_fonte = '#1a1a1a' if artigos >= 3 else '#555555'
        espessura_borda = 1.0 + (artigos * 0.4)
        recuo = 0.04 + (artigos * 0.005)
    # ---------------------------------------
    
    # Vetor do centro até o nó para saber para onde empurrar o texto
    dx = x - centro_x
    dy = y - centro_y
    distancia = np.sqrt(dx**2 + dy**2)
    
    # Pequeno empurrão para o texto não encostar na bolinha (usando o recuo do modo ativo)
    if distancia > 0:
        nx_txt = x + (dx / distancia) * recuo
        ny_txt = y + (dy / distancia) * recuo
    else:
        nx_txt, ny_txt = x, y + recuo
        
    # Define o alinhamento horizontal com base na posição (Esquerda ou Direita)
    if x > centro_x:
        alinhamento_h = 'left'   # Nós à direita: texto flui para a direita
    else:
        alinhamento_h = 'right'  # Nós à esquerda: texto flui para a esquerda

    # Criação do texto
    txt = ax.text(
        nx_txt, ny_txt, node, 
        fontsize=tamanho_fonte, 
        fontweight=peso_fonte, 
        fontfamily='sans-serif', 
        color=cor_fonte,
        ha=alinhamento_h, 
        va='center'
    )
    
    # Aplica o contorno branco (Stroke) adaptável
    txt.set_path_effects([
        path_effects.Stroke(linewidth=espessura_borda, foreground='white', alpha=0.9),
        path_effects.Normal()
    ])

# Título oficial ajustado perfeitamente próximo ao topo (y=0.95)
plt.title(
    "Grafo de Coautoria (Rede de Autores)", 
    fontsize=60, 
    fontweight='bold', 
    fontfamily='sans-serif', 
    color='#333333',
    # y=0.97
)

plt.axis('off')

# Minimiza margens internas e remove espaços em branco adicionais ao salvar nas laterais
ax.margins(0.02)
plt.tight_layout()

# Salva a imagem final perfeitamente cortada nas extremidades

if modo_visualizacao == 'apenas_principais':
    plt.savefig('grafo_coautoria_circular.png', dpi=300, bbox_inches='tight', pad_inches=0)
else:
    plt.savefig('grafo_coautoria_circular_total.png', dpi=300, bbox_inches='tight', pad_inches=0)
# plt.show()