import os
import time

class ListaAdjacencia:
    def __init__(self, num_vertices, dirigido=False):
        self.num_vertices = num_vertices
        self.dirigido = dirigido
        self.adjacencias = {i: [] for i in range(num_vertices)}

    def adicionar_aresta(self, u, v, peso=1, label=None):
        if not self.checar_adjacencia(u, v):
            self.adjacencias[u].append((v, peso))
            if not self.dirigido:
                self.adjacencias[v].append((u, peso))

    def remover_aresta(self, u, v):
        self.adjacencias[u] = [w for w in self.adjacencias[u] if w[0] != v]
        if not self.dirigido:
            self.adjacencias[v] = [w for w in self.adjacencias[v] if w[0] != u]

    def checar_adjacencia(self, u, v):
        return any(w == v for w, _ in self.adjacencias[u])

    def exibir(self):
        for vertice, adj in self.adjacencias.items():
            print(f"{vertice}: {adj}")

class MatrizAdjacencia:
    def __init__(self, num_vertices, dirigido=False):
        self.num_vertices = num_vertices
        self.dirigido = dirigido
        self.adj_matrix = [[0] * num_vertices for _ in range(num_vertices)]

    def adicionar_aresta(self, u, v, peso=1):
        self.adj_matrix[u][v] = peso
        if not self.dirigido:
            self.adj_matrix[v][u] = peso

    def remover_aresta(self, u, v):
        self.adj_matrix[u][v] = 0
        if not self.dirigido:
            self.adj_matrix[v][u] = 0

    def checar_adjacencia(self, u, v):
        return self.adj_matrix[u][v] != 0

    def exibir(self):
        for row in self.adj_matrix:
            print(row)

class MatrizIncidencia:
    def __init__(self, num_vertices, dirigido=False):
        self.num_vertices = num_vertices
        self.dirigido = dirigido
        self.inc_matrix = []  
        self.edge_list = []   

    def adicionar_aresta(self, u, v, peso=1, label=None):
        self.edge_list.append({'u': u, 'v': v, 'peso': peso, 'label': label})
        edge_index = len(self.edge_list) - 1

        for row in self.inc_matrix:
            row.append(0)
        
        nova_coluna = [0] * self.num_vertices
        nova_coluna[u] = 1
        if not self.dirigido:
            nova_coluna[v] = 1
        else:
            nova_coluna[v] = -1
        self.inc_matrix.append(nova_coluna)

    def remover_aresta(self, u, v):
        for i, edge in enumerate(self.edge_list):
            if edge['u'] == u and edge['v'] == v:
                del self.edge_list[i]
                del self.inc_matrix[i]
                for row in self.inc_matrix:
                    del row[i]
                break

    def checar_adjacencia(self, u, v):
        for edge in self.edge_list:
            if edge['u'] == u and edge['v'] == v:
                return True
            if not self.dirigido and edge['u'] == v and edge['v'] == u:
                return True
        return False

    def exibir(self):
        print("Matriz de Incidência:")
        for row in self.inc_matrix:
            print(row)

class Grafo:
    def __init__(self, num_vertices, dirigido=False, nome=""):
        self.num_vertices = num_vertices
        self.dirigido = dirigido
        self.nome = nome  # Adicionado para armazenar o nome do grafo
        self.lista_adj = ListaAdjacencia(num_vertices, dirigido)
        self.matriz_adj = MatrizAdjacencia(num_vertices, dirigido)
        self.matriz_inc = MatrizIncidencia(num_vertices, dirigido)
        self.edge_list = []
        self.vertex_labels = {i: f"V{i + 1}" for i in range(num_vertices)}
        self.tempo = 0
        self.frame_count = 0

    def adicionar_vertice(self, label=None):
        v = self.num_vertices
        self.lista_adj.num_vertices += 1
        self.matriz_adj.num_vertices += 1
        self.matriz_inc.num_vertices += 1
        self.num_vertices += 1
        self.lista_adj.adjacencias[v] = []
        
        for row in self.matriz_adj.adj_matrix:
            row.append(0)
        self.matriz_adj.adj_matrix.append([0] * self.matriz_adj.num_vertices)
        
        for row in self.matriz_inc.inc_matrix:
            row.append(0)
        
        self.vertex_labels[v] = label if label else f"V{v + 1}"

    def adicionar_aresta(self, u, v, peso=1, label=None):
        self.lista_adj.adicionar_aresta(u, v, peso, label)
        self.matriz_adj.adicionar_aresta(u, v, peso)
        self.matriz_inc.adicionar_aresta(u, v, peso, label)
        self.edge_list.append({'u': u, 'v': v, 'peso': peso, 'label': label})

    def remover_aresta(self, u, v):
        self.lista_adj.remover_aresta(u, v)
        self.matriz_adj.remover_aresta(u, v)
        self.matriz_inc.remover_aresta(u, v)
        
        for i, edge in enumerate(self.edge_list):
            if edge['u'] == u and edge['v'] == v:
                del self.edge_list[i]
                break
            if not self.dirigido and edge['u'] == v and edge['v'] == u:
                del self.edge_list[i]
                break

    def checar_adjacencia_vertices(self, u, v):
        return (self.lista_adj.checar_adjacencia(u, v) and
                self.matriz_adj.checar_adjacencia(u, v) and
                self.matriz_inc.checar_adjacencia(u, v))

    def contar_vertices_arestas(self):
        num_vertices = self.num_vertices
        num_arestas = len(self.edge_list)
        return num_vertices, num_arestas

    def grafo_vazio(self):
        return self.contar_vertices_arestas()[1] == 0

    def grafo_completo(self):
        for u in range(self.num_vertices):
            grau = len(self.lista_adj.adjacencias[u])
            if self.dirigido:
                if grau != self.num_vertices - 1:
                    return False
            else:
                if grau != self.num_vertices - 1:
                    return False
        return True

    def identificar_pontes_naive(self):
        pontes = []
        for u in range(self.num_vertices):
            for v, _ in list(self.lista_adj.adjacencias[u]):
                if (u < v) or self.dirigido:
                    self.remover_aresta(u, v)
                    if not self.grafo_conexo():
                        pontes.append((u, v))
                    self.adicionar_aresta(u, v)
        return pontes

    def identificar_pontes_tarjan(self):
        num = [0] * self.num_vertices
        low = [0] * self.num_vertices
        self.tempo = 1
        pontes = []
        visited = [False] * self.num_vertices
        parent = [-1] * self.num_vertices

        for u in range(self.num_vertices):
            if not visited[u]:
                self._tarjan_dfs(u, visited, parent, num, low, pontes)
        return pontes

    def _tarjan_dfs(self, u, visited, parent, num, low, pontes):
        stack = [(u, iter(self.lista_adj.adjacencias[u]))]
        visited[u] = True
        num[u] = low[u] = self.tempo
        self.tempo += 1

        while stack:
            v, children = stack[-1]
            try:
                w, _ = next(children)
                if not visited[w]:
                    parent[w] = v
                    visited[w] = True
                    num[w] = low[w] = self.tempo
                    self.tempo += 1
                    stack.append((w, iter(self.lista_adj.adjacencias[w])))
                elif w != parent[v]:
                    low[v] = min(low[v], num[w])
            except StopIteration:
                stack.pop()
                if parent[v] != -1:
                    low[parent[v]] = min(low[parent[v]], low[v])
                    if low[v] > num[parent[v]]:
                        pontes.append((parent[v], v))

    def identificar_articulacoes(self):
        num = [0] * self.num_vertices
        low = [0] * self.num_vertices
        parent = [-1] * self.num_vertices
        self.tempo = 1
        articulacoes = set()
        visited = [False] * self.num_vertices

        for u in range(self.num_vertices):
            if not visited[u]:
                self._articulacao_dfs(u, visited, parent, num, low, articulacoes)
        return list(articulacoes)

    def _articulacao_dfs(self, u, visited, parent, num, low, articulacoes):
        stack = [(u, iter(self.lista_adj.adjacencias[u]), False)]
        children = 0
        visited[u] = True
        num[u] = low[u] = self.tempo
        self.tempo += 1
        articulation_found = False

        while stack:
            v, children_iter, is_return = stack[-1]
            if not is_return:
                stack[-1] = (v, children_iter, True)
                try:
                    w, _ = next(children_iter)
                    if not visited[w]:
                        parent[w] = v
                        children += 1
                        visited[w] = True
                        num[w] = low[w] = self.tempo
                        self.tempo += 1
                        stack.append((w, iter(self.lista_adj.adjacencias[w]), False))
                    elif w != parent[v]:
                        low[v] = min(low[v], num[w])
                except StopIteration:
                    stack.pop()
                    if parent[v] != -1:
                        low[parent[v]] = min(low[parent[v]], low[v])
                        if low[v] >= num[parent[v]]:
                            articulacoes.add(parent[v])
                    else:
                        if children > 1:
                            articulacoes.add(v)
            else:
                stack.pop()

    def grafo_conexo(self):
        visitados = [False] * self.num_vertices
        stack = [0]
        visitados[0] = True
        while stack:
            v = stack.pop()
            for w, _ in self.lista_adj.adjacencias[v]:
                if not visitados[w]:
                    visitados[w] = True
                    stack.append(w)
        return all(visitados)

    def kosaraju_scc(self):
        visited = [False] * self.num_vertices
        stack = []

        def dfs_fill_order(v):
            visited[v] = True
            for w, _ in self.lista_adj.adjacencias[v]:
                if not visited[w]:
                    dfs_fill_order(w)
            stack.append(v)

        for i in range(self.num_vertices):
            if not visited[i]:
                dfs_fill_order(i)

        transposto = {i: [] for i in range(self.num_vertices)}
        for u in self.lista_adj.adjacencias:
            for v, peso in self.lista_adj.adjacencias[u]:
                transposto[v].append((u, peso))

        visited = [False] * self.num_vertices
        scc_list = []

        def dfs_transpose(v, component):
            visited[v] = True
            component.append(v)
            for w, _ in transposto[v]:
                if not visited[w]:
                    dfs_transpose(w, component)

        while stack:
            v = stack.pop()
            if not visited[v]:
                component = []
                dfs_transpose(v, component)
                scc_list.append(component)

        return scc_list

    def grafo_fortemente_conexo(self):
        if not self.dirigido:
            return self.grafo_conexo()
        scc = self.kosaraju_scc()
        return len(scc) == 1

    def grafo_conexo_fraco(self):
        if not self.dirigido:
            return self.grafo_conexo()
        visitados = [False] * self.num_vertices
        stack = [0]
        visitados[0] = True
        while stack:
            v = stack.pop()
            for w, _ in self.lista_adj.adjacencias[v]:
                if not visitados[w]:
                    visitados[w] = True
                    stack.append(w)
            for u in range(self.num_vertices):
                if self.lista_adj.checar_adjacencia(u, v) and not visitados[u]:
                    visitados[u] = True
                    stack.append(u)
        return all(visitados)

    def grafo_semi_fortemente_conexo(self):
        if not self.dirigido:
            return self.grafo_conexo()
        for i in range(self.num_vertices):
            visitados = [False] * self.num_vertices
            stack = [i]
            visitados[i] = True
            while stack:
                v = stack.pop()
                for w, _ in self.lista_adj.adjacencias[v]:
                    if not visitados[w]:
                        visitados[w] = True
                        stack.append(w)
                for u in range(self.num_vertices):
                    if self.lista_adj.checar_adjacencia(u, v) and not visitados[u]:
                        visitados[u] = True
                        stack.append(u)
            if not all(visitados):
                return False
        return True

    def fleury(self):
        if not self.grafo_euleriano():
            print("O grafo não é Euleriano.")
            return []
        grafo_copia = Grafo(self.num_vertices, self.dirigido, self.nome)
        grafo_copia.lista_adj.adjacencias = {v: list(self.lista_adj.adjacencias[v]) for v in self.lista_adj.adjacencias}
        grafo_copia.matriz_adj.adj_matrix = [row.copy() for row in self.matriz_adj.adj_matrix]
        grafo_copia.matriz_inc.inc_matrix = [row.copy() for row in self.matriz_inc.inc_matrix]
        grafo_copia.edge_list = list(self.edge_list)
        grafo_copia.vertex_labels = dict(self.vertex_labels)

        caminho = []
        atual = 0
        while grafo_copia.contar_vertices_arestas()[1] > 0:
            if not grafo_copia.lista_adj.adjacencias[atual]:
                break
            for vizinho, _ in list(grafo_copia.lista_adj.adjacencias[atual]):
                grafo_copia.remover_aresta(atual, vizinho)
                if not grafo_copia.grafo_conexo():
                    grafo_copia.adicionar_aresta(atual, vizinho)
                else:
                    caminho.append((atual, vizinho))
                    atual = vizinho
                    break
        return caminho

    def grafo_euleriano(self):
        if not self.grafo_conexo():
            return False
        graus = [len(self.lista_adj.adjacencias[v]) for v in self.lista_adj.adjacencias]
        return all(g % 2 == 0 for g in graus)

    def exportar_para_gexf(self, nome_arquivo="grafo.gexf"):
        dados_dir = "dados"
        if not os.path.exists(dados_dir):
            os.makedirs(dados_dir)
        with open(os.path.join(dados_dir, nome_arquivo), "w", encoding="utf-8") as arquivo:
            arquivo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            arquivo.write('<gexf xmlns="http://www.gexf.net/1.3draft" version="1.3">\n')
            arquivo.write('  <graph mode="static" defaultedgetype="{}">\n'.format("directed" if self.dirigido else "undirected"))
            arquivo.write("    <nodes>\n")
            for vertice in range(self.num_vertices):
                label = self.vertex_labels.get(vertice, f"V{vertice + 1}")
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
        dados_dir = "dados"
        if not os.path.exists(dados_dir):
            os.makedirs(dados_dir)
        
        largura = 800
        altura = 800
        raio_vertice = 20
        num_cols = int(self.num_vertices ** 0.5) + 1
        num_rows = (self.num_vertices // num_cols) + 1
        espacamento_x = largura // (num_cols + 1)
        espacamento_y = altura // (num_rows + 1)
        posicoes = {}

        idx = 0
        for row in range(1, num_rows + 1):
            for col in range(1, num_cols + 1):
                if idx < self.num_vertices:
                    x = col * espacamento_x
                    y = row * espacamento_y
                    posicoes[idx] = (x, y)
                    idx += 1

        caminho_frames = os.path.join(dados_dir, "imagens_ppm")
        if not os.path.exists(caminho_frames):
            os.makedirs(caminho_frames)

        imagem_base = [[(255, 255, 255) for _ in range(largura)] for _ in range(altura)]
        for i in range(self.num_vertices):
            x, y = posicoes[i]
            self.desenhar_circulo(imagem_base, x, y, raio_vertice, (0, 0, 255))

        for idx in range(len(self.edge_list)):
            imagem = [row.copy() for row in imagem_base]
            for edge in self.edge_list[:idx+1]:
                u = edge['u']
                v = edge['v']
                x1, y1 = posicoes[u]
                x2, y2 = posicoes[v]
                self.desenhar_linha(imagem, x1, y1, x2, y2, (0, 0, 0))
            frame_nome = f"frame_{self.frame_count}.ppm"
            self.salvar_imagem_ppm(imagem, os.path.join(caminho_frames, frame_nome))
            self.frame_count += 1

        imagem_final = [row.copy() for row in imagem_base]
        for edge in self.edge_list:
            u = edge['u']
            v = edge['v']
            x1, y1 = posicoes[u]
            x2, y2 = posicoes[v]
            self.desenhar_linha(imagem_final, x1, y1, x2, y2, (0, 0, 0))
        self.salvar_imagem_ppm(imagem_final, os.path.join(dados_dir, nome_arquivo))
        print(f"Imagem PPM exportada como {os.path.join(dados_dir, nome_arquivo)}")

    def exportar_para_txt(self, nome_arquivo="grafo.txt"):
        dados_dir = "dados"
        if not os.path.exists(dados_dir):
            os.makedirs(dados_dir)
        with open(os.path.join(dados_dir, nome_arquivo), 'w', encoding='utf-8') as f:
            f.write(f"Grafo: {self.nome}\n")
            f.write(f"Direcionado: {'Sim' if self.dirigido else 'Não'}\n")
            f.write(f"Vértices: {self.num_vertices}\n")
            f.write(f"Arestas: {len(self.edge_list)}\n\n")

            f.write("Lista de Adjacência:\n")
            for vertice, adj in self.lista_adj.adjacencias.items():
                vertice_exibicao = vertice + 1
                adj_exibicao = ", ".join([f"{v + 1}({peso})" for v, peso in adj])
                f.write(f"{vertice_exibicao}: {adj_exibicao}\n")

            f.write("\nMatriz de Adjacência:\n")
            header = "   " + " ".join([f"{i+1:3}" for i in range(self.num_vertices)])
            f.write(header + "\n")
            for i, row in enumerate(self.matriz_adj.adj_matrix):
                linha = f"{i+1:3} " + " ".join([f"{val:3}" for val in row])
                f.write(linha + "\n")

            f.write("\nMatriz de Incidência:\n")
            if self.edge_list:
                header = "   " + " ".join([f"{i+1:3}" for i in range(len(self.edge_list))])
                f.write(header + "\n")
                for i, row in enumerate(self.matriz_inc.inc_matrix):
                    linha = f"{i+1:3} " + " ".join([f"{val:3}" for val in row])
                    f.write(linha + "\n")
            else:
                f.write("Sem arestas.\n")

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
        for y in range(y0 - raio, y0 + raio + 1):
            for x in range(x0 - raio, x0 + raio + 1):
                if 0 <= x < len(imagem[0]) and 0 <= y < len(imagem):
                    if (x - x0) ** 2 + (y - y0) ** 2 <= raio ** 2:
                        imagem[y][x] = cor

    def salvar_imagem_ppm(self, imagem, nome_arquivo):
        with open(nome_arquivo, "wb") as f:
            f.write(b"P6\n")
            f.write(f"{len(imagem[0])} {len(imagem)}\n".encode())
            f.write(b"255\n")
            for row in imagem:
                for pixel in row:
                    f.write(bytes(pixel))

    def exibir_lista_adjacencia(self):
        print("Lista de Adjacência:")
        for vertice, adj in self.lista_adj.adjacencias.items():
            vertice_exibicao = vertice + 1
            adj_exibicao = [(v + 1, peso) for v, peso in adj]
            print(f"{vertice_exibicao}: {adj_exibicao}")

    def exibir_matriz_adjacencia(self):
        print("Matriz de Adjacência:")
        header = "   " + " ".join([f"{i+1:3}" for i in range(self.num_vertices)])
        print(header)
        for i, row in enumerate(self.matriz_adj.adj_matrix):
            linha = f"{i+1:3} " + " ".join([f"{val:3}" for val in row])
            print(linha)

    def exibir_matriz_incidencia(self):
        print("Matriz de Incidência:")
        header = "   " + " ".join([f"{i+1:3}" for i in range(len(self.edge_list))])
        print(header)
        for i, row in enumerate(self.matriz_inc.inc_matrix):
            linha = f"{i+1:3} " + " ".join([f"{val:3}" for val in row])
            print(linha)

    def exibir_representacoes(self):
        self.exibir_lista_adjacencia()
        print()
        self.exibir_matriz_adjacencia()
        print()
        self.exibir_matriz_incidencia()

def teste_desempenho():
    tamanhos = [100, 1000, 10000, 100000]
    for tamanho in tamanhos:
        grafo = Grafo(tamanho)
        num_componentes = 5
        tamanho_componente = tamanho // num_componentes
        vertices_componentes = []

        for i in range(num_componentes):
            vertices = list(range(i * tamanho_componente, (i + 1) * tamanho_componente))
            vertices_componentes.append(vertices)
            for j in range(len(vertices)):
                u = vertices[j]
                v = vertices[(j + 1) % len(vertices)]
                grafo.adicionar_aresta(u, v)

        for i in range(num_componentes - 1):
            u = vertices_componentes[i][-1]
            v = vertices_componentes[i + 1][0]
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
            'arestas': [(0, 1), (1, 2), (2, 0)],
            'dirigido': True
        },
        "4": {
            'arestas': [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],
            'dirigido': False
        },
        "5": {
            'arestas': [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 2)],
            'dirigido': True
        },
        "6": {
            'arestas': [(0, 1), (1, 2), (2, 3)],
            'dirigido': False
        },
        "7": {
            'arestas': [(0, 1), (1, 2), (2, 3), (3, 0), (3, 4), (4, 5), (5, 3)],
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
                grafo_nome = f"Grafo_{nome}"
                grafo = Grafo(num_vertices, dirigido, nome=grafo_nome)
                for u, v in arestas:
                    grafo.adicionar_aresta(u, v)
                print(f"\n{grafo.nome}:")
                print(f"O grafo é {'direcionado' if grafo.dirigido else 'não direcionado'}.")
                print(f"Vértices: {grafo.num_vertices}")
                print(f"Arestas: {grafo.contar_vertices_arestas()[1]}")
                pontes_naive = grafo.identificar_pontes_naive()
                pontes_tarjan = grafo.identificar_pontes_tarjan()
                print("Pontes (Naive):", [(u + 1, v + 1) for u, v in pontes_naive])
                print("Pontes (Tarjan):", [(u + 1, v + 1) for u, v in pontes_tarjan])
                articulacoes = grafo.identificar_articulacoes()
                print("Articulações:", [v + 1 for v in articulacoes])
                if dirigido:
                    print("Fortemente Conexo:", grafo.grafo_fortemente_conexo())
                    print("Conexo Fraco:", grafo.grafo_conexo_fraco())
                    print("Semi-fortemente Conexo:", grafo.grafo_semi_fortemente_conexo())
                else:
                    print("Conexo:", grafo.grafo_conexo())
                grafo.exportar_para_gexf(f"{grafo.nome}.gexf")
                grafo.exportar_para_ppm(f"{grafo.nome}.ppm")
                grafo.exportar_para_txt(f"{grafo.nome}.txt")
                print(f"Grafo '{grafo.nome}' exportado para os formatos GEXF, PPM e TXT no diretório 'dados'.")
        elif opcao == 2:
            try:
                num_vertices = int(input("Digite o número de vértices: "))
                if num_vertices <= 0:
                    print("O número de vértices deve ser positivo.")
                    continue
                dirigido = input("O grafo é direcionado? (s/n): ").lower() == 's'
                nome_grafo = input("Digite o nome do grafo: ").strip()
                if not nome_grafo:
                    nome_grafo = "Grafo_Manual"
            except ValueError:
                print("Entrada inválida. Por favor, digite um número inteiro.")
                continue
            grafo = Grafo(num_vertices, dirigido, nome=nome_grafo)
            while True:
                print("\n1. Adicionar Aresta")
                print("2. Remover Aresta")
                print("3. Verificar Adjacência")
                print("4. Exibir Lista de Adjacência")
                print("5. Exibir Matriz de Adjacência")
                print("6. Exibir Matriz de Incidência")
                print("7. Verificar Conectividade")
                print("8. Identificar Pontes")
                print("9. Identificar Articulações")
                print("10. Exportar Grafo")
                print("11. Exportar para PPM")
                print("12. Voltar")
                try:
                    escolha = int(input("Escolha uma opção: "))
                except ValueError:
                    print("Entrada inválida. Por favor, digite números inteiros.")
                    continue
                if escolha == 1:
                    try:
                        u = int(input(f"Digite o vértice u (1 a {grafo.num_vertices}): ")) - 1
                        v = int(input(f"Digite o vértice v (1 a {grafo.num_vertices}): ")) - 1
                        if u < 0 or u >= grafo.num_vertices or v < 0 or v >= grafo.num_vertices:
                            print(f"Erro: Vértices válidos estão entre 1 e {grafo.num_vertices}.")
                            continue
                        peso_input = input("Digite o peso da aresta (padrão 1): ")
                        peso = int(peso_input) if peso_input else 1
                        label = input("Digite o rótulo da aresta (opcional): ")
                        grafo.adicionar_aresta(u, v, peso, label)
                        print(f"Aresta ({u + 1}, {v + 1}) adicionada!")
                    except ValueError:
                        print("Entrada inválida. Por favor, digite números inteiros.")
                elif escolha == 2:
                    try:
                        u = int(input(f"Digite o vértice u (1 a {grafo.num_vertices}): ")) - 1
                        v = int(input(f"Digite o vértice v (1 a {grafo.num_vertices}): ")) - 1
                        if u < 0 or u >= grafo.num_vertices or v < 0 or v >= grafo.num_vertices:
                            print(f"Erro: Vértices válidos estão entre 1 e {grafo.num_vertices}.")
                            continue
                        grafo.remover_aresta(u, v)
                        print(f"Aresta ({u + 1}, {v + 1}) removida!")
                    except ValueError:
                        print("Entrada inválida. Por favor, digite números inteiros.")
                elif escolha == 3:
                    try:
                        u = int(input(f"Digite o vértice u (1 a {grafo.num_vertices}): ")) - 1
                        v = int(input(f"Digite o vértice v (1 a {grafo.num_vertices}): ")) - 1
                        if u < 0 or u >= grafo.num_vertices or v < 0 or v >= grafo.num_vertices:
                            print(f"Erro: Vértices válidos estão entre 1 e {grafo.num_vertices}.")
                            continue
                        if grafo.checar_adjacencia_vertices(u, v):
                            print(f"Aresta ({u + 1}, {v + 1}) existe!")
                        else:
                            print(f"Aresta ({u + 1}, {v + 1}) não existe.")
                    except ValueError:
                        print("Entrada inválida. Por favor, digite números inteiros.")
                elif escolha == 4:
                    grafo.exibir_lista_adjacencia()
                elif escolha == 5:
                    grafo.exibir_matriz_adjacencia()
                elif escolha == 6:
                    grafo.exibir_matriz_incidencia()
                elif escolha == 7:
                    if grafo.dirigido:
                        print("Fortemente Conexo:", grafo.grafo_fortemente_conexo())
                        print("Conexo Fraco:", grafo.grafo_conexo_fraco())
                        print("Semi-fortemente Conexo:", grafo.grafo_semi_fortemente_conexo())
                    else:
                        print("Conexo:", grafo.grafo_conexo())
                elif escolha == 8:
                    pontes_naive = grafo.identificar_pontes_naive()
                    pontes_tarjan = grafo.identificar_pontes_tarjan()
                    pontes_naive_exib = [(u + 1, v + 1) for u, v in pontes_naive]
                    pontes_tarjan_exib = [(u + 1, v + 1) for u, v in pontes_tarjan]
                    print("Pontes (Naive):", pontes_naive_exib)
                    print("Pontes (Tarjan):", pontes_tarjan_exib)
                elif escolha == 9:
                    articulacoes = [v + 1 for v in grafo.identificar_articulacoes()]
                    print("Articulações:", articulacoes)
                elif escolha == 10:
                    nome = input("Digite o nome base dos arquivos (sem extensão): ").strip()
                    if not nome:
                        nome = grafo.nome.replace(" ", "_")  # Substituir espaços por underscores
                    grafo.exportar_para_gexf(f"{nome}.gexf")
                    grafo.exportar_para_ppm(f"{nome}.ppm")
                    grafo.exportar_para_txt(f"{nome}.txt")
                    print("Exportação concluída.")
                elif escolha == 11:
                    nome_ppm = input("Digite o nome do arquivo PPM (com extensão .ppm): ").strip()
                    if not nome_ppm.endswith('.ppm'):
                        print("Erro: O nome do arquivo deve terminar com '.ppm'.")
                        continue
                    grafo.exportar_para_ppm(nome_ppm)
                elif escolha == 12:
                    # Ao sair do menu de criação manual, salvar automaticamente
                    export_nome = grafo.nome.replace(" ", "_")  # Substituir espaços por underscores
                    grafo.exportar_para_gexf(f"{export_nome}.gexf")
                    grafo.exportar_para_ppm(f"{export_nome}.ppm")
                    grafo.exportar_para_txt(f"{export_nome}.txt")
                    print(f"Grafo '{grafo.nome}' exportado automaticamente após a criação.")
                    break
                else:
                    print("Opção inválida, tente novamente.")
        elif opcao == 3:
            teste_desempenho()
        elif opcao == 4:
            print("Saindo do programa. Até logo!")
            break
        else:
            print("Opção inválida, tente novamente.")

if __name__ == "__main__":
    menu()
