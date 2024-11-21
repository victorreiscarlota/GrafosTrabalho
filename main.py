import os
import time

class Grafo:
    def __init__(self, num_vertices, dirigido=False):
        self.num_vertices = num_vertices
        self.dirigido = dirigido
        self.adjacencias = {i: [] for i in range(num_vertices)}
        self.adj_matrix = [[0]*num_vertices for _ in range(num_vertices)]
        self.inc_matrix = []
        self.edge_list = []
        self.vertex_labels = {i: f"V{i}" for i in range(num_vertices)}
        self.tempo = 0
        self.frame_count = 0 

    def adicionar_vertice(self, label=None):
        v = self.num_vertices
        self.adjacencias[v] = []
        self.num_vertices += 1
        for row in self.adj_matrix:
            row.append(0)
        self.adj_matrix.append([0]*self.num_vertices)
        for row in self.inc_matrix:
            row.append(0)
        self.vertex_labels[v] = label if label else f"V{v}"

    def adicionar_aresta(self, u, v, peso=1, label=None):
        if v not in [w for w, _ in self.adjacencias[u]]:
            self.adjacencias[u].append((v, peso))
            if not self.dirigido:
                self.adjacencias[v].append((u, peso))
            self.adj_matrix[u][v] = peso
            if not self.dirigido:
                self.adj_matrix[v][u] = peso
            self.edge_list.append({'u': u, 'v': v, 'peso': peso, 'label': label})
            edge_index = len(self.edge_list) - 1
            if not self.inc_matrix:
                self.inc_matrix = [[0] for _ in range(self.num_vertices)]
            else:
                for row in self.inc_matrix:
                    row.append(0)
            self.inc_matrix[u][edge_index] = 1
            if not self.dirigido:
                self.inc_matrix[v][edge_index] = 1
            else:
                self.inc_matrix[v][edge_index] = -1

    def remover_aresta(self, u, v):
        self.adjacencias[u] = [w for w in self.adjacencias[u] if w[0] != v]
        if not self.dirigido:
            self.adjacencias[v] = [w for w in self.adjacencias[v] if w[0] != u]
        self.adj_matrix[u][v] = 0
        if not self.dirigido:
            self.adj_matrix[v][u] = 0
        for i, edge in enumerate(self.edge_list):
            if edge['u'] == u and edge['v'] == v:
                del self.edge_list[i]
                for row in self.inc_matrix:
                    del row[i]
                break

    def checar_adjacencia_vertices(self, u, v):
        return any(w == v for w, _ in self.adjacencias[u])

    def contar_vertices_arestas(self):
        num_arestas = len(self.edge_list)
        return self.num_vertices, num_arestas

    def grafo_vazio(self):
        return all(len(self.adjacencias[v]) == 0 for v in self.adjacencias)

    def grafo_completo(self):
        for u in range(self.num_vertices):
            if len(self.adjacencias[u]) != (self.num_vertices - 1):
                return False
        return True

    def identificar_pontes_naive(self):
        pontes = []
        for u in range(self.num_vertices):
            for v, _ in list(self.adjacencias[u]):
                if (u < v) or self.dirigido:
                    self.remover_aresta(u, v)
                    if not self.grafo_conectado():
                        pontes.append((u, v))
                    self.adicionar_aresta(u, v)
        return pontes

    def identificar_pontes_tarjan(self):
        num = [0] * self.num_vertices
        low = [0] * self.num_vertices
        self.tempo = 1
        pontes = []
        def dfs(u, parent):
            num[u] = low[u] = self.tempo
            self.tempo += 1
            for v, _ in self.adjacencias[u]:
                if num[v] == 0:
                    dfs(v, u)
                    low[u] = min(low[u], low[v])
                    if low[v] > num[u]:
                        pontes.append((u, v))
                elif v != parent:
                    low[u] = min(low[u], num[v])
        for u in range(self.num_vertices):
            if num[u] == 0:
                dfs(u, -1)
        return pontes

    def identificar_articulacoes(self):
        num = [0] * self.num_vertices
        low = [0] * self.num_vertices
        parent = [-1] * self.num_vertices
        self.tempo = 1
        articulacoes = set()
        def dfs(u):
            children = 0
            num[u] = low[u] = self.tempo
            self.tempo += 1
            for v, _ in self.adjacencias[u]:
                if num[v] == 0:
                    parent[v] = u
                    children += 1
                    dfs(v)
                    low[u] = min(low[u], low[v])
                    if parent[u] == -1 and children > 1:
                        articulacoes.add(u)
                    if parent[u] != -1 and low[v] >= num[u]:
                        articulacoes.add(u)
                elif v != parent[u]:
                    low[u] = min(low[u], num[v])
        for u in range(self.num_vertices):
            if num[u] == 0:
                dfs(u)
        return list(articulacoes)

    def grafo_conectado(self):
        visitados = [False] * self.num_vertices
        stack = [0]
        visitados[0] = True
        while stack:
            v = stack.pop()
            for w, _ in self.adjacencias[v]:
                if not visitados[w]:
                    visitados[w] = True
                    stack.append(w)
        return all(visitados)

    def grafo_fortemente_conectado(self):
        if not self.dirigido:
            return self.grafo_conectado()
        def dfs(v, visitados, stack):
            visitados[v] = True
            for w, _ in self.adjacencias[v]:
                if not visitados[w]:
                    dfs(w, visitados, stack)
            stack.append(v)
        def dfs_transposto(v, visitados, transposto):
            visitados[v] = True
            for w, _ in transposto[v]:
                if not visitados[w]:
                    dfs_transposto(w, visitados, transposto)
        stack = []
        visitados = [False] * self.num_vertices
        for i in range(self.num_vertices):
            if not visitados[i]:
                dfs(i, visitados, stack)
        transposto = {i: [] for i in range(self.num_vertices)}
        for u in self.adjacencias:
            for v, peso in self.adjacencias[u]:
                transposto[v].append((u, peso))
        visitados = [False] * self.num_vertices
        dfs_transposto(stack[-1], visitados, transposto)
        return all(visitados)

    def fleury(self):
        if not self.grafo_euleriano():
            print("O grafo não é Euleriano.")
            return []
        grafo_copia = Grafo(self.num_vertices, self.dirigido)
        grafo_copia.adjacencias = {v: list(self.adjacencias[v]) for v in self.adjacencias}
        caminho = []
        atual = 0
        while any(grafo_copia.adjacencias.values()):
            if not grafo_copia.adjacencias[atual]:
                break
            for vizinho, _ in grafo_copia.adjacencias[atual]:
                grafo_copia.remover_aresta(atual, vizinho)
                if not grafo_copia.grafo_conectado():
                    grafo_copia.adicionar_aresta(atual, vizinho)
                else:
                    caminho.append((atual, vizinho))
                    atual = vizinho
                    break
        return caminho

    def grafo_euleriano(self):
        if not self.grafo_conectado():
            return False
        graus = [len(self.adjacencias[v]) for v in self.adjacencias]
        return all(g % 2 == 0 for g in graus)

    def exportar_para_gexf(self, nome_arquivo="grafo.gexf"):
        if not os.path.exists("dados"):
            os.makedirs("dados")
        with open(os.path.join("dados", nome_arquivo), "w", encoding="utf-8") as arquivo:
            arquivo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            arquivo.write('<gexf xmlns="http://www.gexf.net/1.3draft" version="1.3">\n')
            arquivo.write('  <graph mode="static" defaultedgetype="{}">\n'.format("directed" if self.dirigido else "undirected"))
            arquivo.write("    <nodes>\n")
            for vertice in range(self.num_vertices):
                label = self.vertex_labels.get(vertice, f"V{vertice}")
                arquivo.write(f'      <node id="{vertice}" label="{label}" />\n')
            arquivo.write("    </nodes>\n")
            arquivo.write("    <edges>\n")
            for i, edge in enumerate(self.edge_list):
                u = edge['u']
                v = edge['v']
                peso = edge['peso']
                label = edge['label'] if edge['label'] else ""
                arquivo.write(f'      <edge id="{i}" source="{u}" target="{v}" weight="{peso}" label="{label}" />\n')
            arquivo.write("    </edges>\n")
            arquivo.write("  </graph>\n")
            arquivo.write("</gexf>\n")

    def exportar_para_ppm(self, nome_arquivo="grafo.ppm"):
        largura = 800
        altura = 800
        raio_vertice = 20
        num_cols = int(self.num_vertices ** 0.5) + 1
        num_rows = (self.num_vertices // num_cols) + 1
        espacamento_x = largura // (num_cols + 1)
        espacamento_y = altura // (num_rows + 1)
        posicoes = {}
        imagem = [[(255, 255, 255) for _ in range(largura)] for _ in range(altura)]
        
        idx = 0
        for row in range(1, num_rows + 1):
            for col in range(1, num_cols + 1):
                if idx < self.num_vertices:
                    x = col * espacamento_x
                    y = row * espacamento_y
                    posicoes[idx] = (x, y)
                    idx += 1
        
        caminho_frames = os.path.join("dados", "imagens_ppm")
        if not os.path.exists(caminho_frames):
            os.makedirs(caminho_frames)
        
        for edge in self.edge_list:
            u = edge['u']
            v = edge['v']
            x1, y1 = posicoes[u]
            x2, y2 = posicoes[v]
            self.desenhar_linha(imagem, x1, y1, x2, y2, (0, 0, 0))
            frame_nome = f"frame_{self.frame_count}.ppm"
            self.salvar_imagem_ppm(imagem, os.path.join(caminho_frames, frame_nome))
            self.frame_count += 1
        
        for i in range(self.num_vertices):
            x, y = posicoes[i]
            self.desenhar_circulo(imagem, x, y, raio_vertice, (0, 0, 255))
        if not os.path.exists("dados"):
            os.makedirs("dados")
        self.salvar_imagem_ppm(imagem, os.path.join("dados", nome_arquivo))
        print(f"Imagem PPM exportada como dados/{nome_arquivo}")

    def desenhar_linha(self, imagem, x1, y1, x2, y2, cor):
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        if x2 > x1:
            sx = 1
        else:
            sx = -1
        if y2 > y1:
            sy = 1
        else:
            sy = -1
        if dx > dy:
            err = dx // 2
            while x != x2:
                if 0 <= x < len(imagem[0]) and 0 <= y < len(imagem):
                    imagem[y][x] = cor
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy // 2
            while y != y2:
                if 0 <= x < len(imagem[0]) and 0 <= y < len(imagem):
                    imagem[y][x] = cor
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        
        if 0 <= x2 < len(imagem[0]) and 0 <= y2 < len(imagem):
            imagem[y2][x2] = cor

    def desenhar_circulo(self, imagem, x0, y0, raio, cor):
        x0 = int(x0)
        y0 = int(y0)
        x = raio
        y = 0
        erro = 0
        while x >= y:
            pontos = [
                (x0 + x, y0 + y), (x0 + y, y0 + x),
                (x0 - y, y0 + x), (x0 - x, y0 + y),
                (x0 - x, y0 - y), (x0 - y, y0 - x),
                (x0 + y, y0 - x), (x0 + x, y0 - y)
            ]
            for px, py in pontos:
                if 0 <= px < len(imagem[0]) and 0 <= py < len(imagem):
                    imagem[py][px] = cor
            y += 1
            if erro <= 0:
                erro += 2 * y + 1
            if erro > 0:
                x -= 1
                erro -= 2 * x + 1

    def salvar_imagem_ppm(self, imagem, nome_arquivo):
        with open(nome_arquivo, "w") as f:
            f.write("P3\n")
            f.write(f"{len(imagem[0])} {len(imagem)}\n")
            f.write("255\n")
            for row in imagem:
                for pixel in row:
                    f.write(f"{pixel[0]} {pixel[1]} {pixel[2]} ")
                f.write("\n")

def testeDesempenho():
    tamanhos = [100, 1000, 10000]
    for tamanho in tamanhos:
        num_arestas = tamanho * 2
        grafo = Grafo(tamanho)
        for i in range(tamanho):
            grafo.adicionar_aresta(i, (i + 1) % tamanho)
        for i in range(tamanho, num_arestas):
            u = i % tamanho
            v = (i + 2) % tamanho
            if not grafo.checar_adjacencia_vertices(u, v):
                grafo.adicionar_aresta(u, v)
        print(f"\nTeste para {tamanho} vértices e {grafo.contar_vertices_arestas()[1]} arestas:")
        inicio_naive = time.time()
        pontes_naive = grafo.identificar_pontes_naive()
        fim_naive = time.time()
        tempo_naive = fim_naive - inicio_naive
        print(f"Método Naive: {len(pontes_naive)} pontes encontradas em {tempo_naive:.4f} segundos.")
        inicio_tarjan = time.time()
        pontes_tarjan = grafo.identificar_pontes_tarjan()
        fim_tarjan = time.time()
        tempo_tarjan = fim_tarjan - inicio_tarjan
        print(f"Método Tarjan: {len(pontes_tarjan)} pontes encontradas em {tempo_tarjan:.4f} segundos.")
        inicio_fleury = time.time()
        caminho_euleriano = grafo.fleury()
        fim_fleury = time.time()
        tempo_fleury = fim_fleury - inicio_fleury
        print(f"Fleury executado em {tempo_fleury:.4f} segundos.")
        grafo.exportar_para_gexf(f"grafo_{tamanho}.gexf")
        grafo.exportar_para_csv(f"grafo_{tamanho}.csv")

def menu():
    grafos_prontos = {
        "1": {
            'arestas': [(0, 1), (1, 2), (2, 3), (3, 0)],
            'dirigido': False
        },
        "2": {
            'arestas': [(0, 1), (1, 2), (2, 3), (3, 0), (3, 1)],
            'dirigido': False
        },
        "3": {
            'arestas': [(0, 1), (1, 2), (2, 3), (3, 0), (3, 2), (2, 0)],
            'dirigido': True
        },
    }
    while True:
        print("\nEscolha as opções abaixo:")
        print("1. Analisar Grafos Prontos")
        print("2. Criar Grafo Manualmente")
        print("3. Realizar Teste de Desempenho (Parte 2)")
        print("4. Sair")
        try:
            opcao = int(input("Escolha uma opção: "))
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")
            continue
        if opcao == 1:
            for nome, info in grafos_prontos.items():
                arestas = info['arestas']
                dirigido = info['dirigido']
                num_vertices = max(max(u, v) for u, v in arestas) + 1
                grafo = Grafo(num_vertices, dirigido)
                for u, v in arestas:
                    grafo.adicionar_aresta(u, v)
                print(f"\nGrafo {nome}:")
                print(f"Vértices: {grafo.num_vertices}")
                print(f"Arestas: {grafo.contar_vertices_arestas()[1]}")
                print("Pontes (Naive):", grafo.identificar_pontes_naive())
                print("Pontes (Tarjan):", grafo.identificar_pontes_tarjan())
                print("Articulações:", grafo.identificar_articulacoes())
                if dirigido:
                    print("Fortemente Conectado:", grafo.grafo_fortemente_conectado())
                else:
                    print("Conectado:", grafo.grafo_conectado())
                grafo.exportar_para_gexf(f"grafo_{nome}.gexf")
                grafo.exportar_para_ppm(f"grafo_{nome}.ppm")
        elif opcao == 2:
            try:
                num_vertices = int(input("Digite o número de vértices: "))
                dirigido = input("O grafo é dirigido? (s/n): ").lower() == 's'
            except ValueError:
                print("Entrada inválida. Por favor, digite um número inteiro.")
                continue
            grafo = Grafo(num_vertices, dirigido)
            while True:
                print("\n1. Adicionar Aresta")
                print("2. Remover Aresta")
                print("3. Verificar Adjacência")
                print("4. Exibir Matriz de Adjacência")
                print("5. Exibir Matriz de Incidência")
                print("6. Verificar Conectividade")
                print("7. Identificar Pontes")
                print("8. Identificar Articulações")
                print("9. Exportar Grafo")
                print("10. Exportar para PPM")
                print("11. Voltar")
                try:
                    escolha = int(input("Escolha uma opção: "))
                except ValueError:
                    print("Entrada inválida. Por favor, digite números inteiros.")
                    continue
                if escolha == 1:
                    try:
                        u = int(input("Digite o vértice u: "))
                        v = int(input("Digite o vértice v: "))
                        peso = int(input("Digite o peso da aresta (padrão 1): ") or 1)
                        label = input("Digite o rótulo da aresta (opcional): ")
                        grafo.adicionar_aresta(u, v, peso, label)
                        print(f"Aresta ({u}, {v}) adicionada!")
                    except ValueError:
                        print("Entrada inválida. Por favor, digite números inteiros.")
                elif escolha == 2:
                    try:
                        u = int(input("Digite o vértice u: "))
                        v = int(input("Digite o vértice v: "))
                        grafo.remover_aresta(u, v)
                        print(f"Aresta ({u}, {v}) removida!")
                    except ValueError:
                        print("Entrada inválida. Por favor, digite números inteiros.")
                elif escolha == 3:
                    try:
                        u = int(input("Digite o vértice u: "))
                        v = int(input("Digite o vértice v: "))
                        if grafo.checar_adjacencia_vertices(u, v):
                            print(f"Aresta ({u}, {v}) existe!")
                        else:
                            print(f"Aresta ({u}, {v}) não existe.")
                    except ValueError:
                        print("Entrada inválida. Por favor, digite números inteiros.")
                elif escolha == 4:
                    print("Matriz de Adjacência:")
                    for row in grafo.adj_matrix:
                        print(row)
                elif escolha == 5:
                    print("Matriz de Incidência:")
                    for row in grafo.inc_matrix:
                        print(row)
                elif escolha == 6:
                    if dirigido:
                        print("Fortemente Conectado:", grafo.grafo_fortemente_conectado())
                    else:
                        print("Conectado:", grafo.grafo_conectado())
                elif escolha == 7:
                    print("Pontes (Naive):", grafo.identificar_pontes_naive())
                    print("Pontes (Tarjan):", grafo.identificar_pontes_tarjan())
                elif escolha == 8:
                    print("Articulações:", grafo.identificar_articulacoes())
                elif escolha == 9:
                    nome = input("Digite o nome base dos arquivos (sem extensão): ")
                    grafo.exportar_para_gexf(f"{nome}.gexf")
                    grafo.exportar_para_ppm(f"{nome}.ppm")
                    print("Exportação concluída.")
                elif escolha == 10:
                    nome_ppm = input("Digite o nome do arquivo PPM (com extensão .ppm): ")
                    grafo.exportar_para_ppm(nome_ppm)
                elif escolha == 11:
                    break
                else:
                    print("Opção inválida, tente novamente.")
        elif opcao == 3:
            testeDesempenho()
        elif opcao == 4:
            break
        else:
            print("Opção inválida, tente novamente.")

menu()
