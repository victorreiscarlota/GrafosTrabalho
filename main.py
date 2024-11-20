class Grafo:
    def __init__(self, num_vertices):
        """
        Inicializa o grafo.
        """
        self.num_vertices = num_vertices
        self.adjacencias = {i: [] for i in range(num_vertices)}
        self.tempo = 0

    def adicionar_aresta(self, u, v):
        """
        Adiciona uma aresta entre os vértices u e v.
        """
        if v not in [w for w, _ in self.adjacencias[u]]:
            self.adjacencias[u].append((v, 1))
            self.adjacencias[v].append((u, 1))

    def remover_aresta(self, u, v):
        """
        Remove a aresta entre os vértices u e v.
        """
        self.adjacencias[u] = [w for w in self.adjacencias[u] if w[0] != v]
        self.adjacencias[v] = [w for w in self.adjacencias[v] if w[0] != u]

    def gerar_grafo_simples(self, num_arestas):
        """
        Gera um grafo aleatório simples com o número de arestas especificado.
        """
        for i in range(num_arestas):
            u = i % self.num_vertices
            v = (i + 1) % self.num_vertices
            self.adicionar_aresta(u, v)

    def verificar_conectividade(self, visitados, v):
        """
        Verifica a conectividade do grafo usando DFS manual.
        """
        visitados[v] = True
        for w, _ in self.adjacencias[v]:
            if not visitados[w]:
                self.verificar_conectividade(visitados, w)

    def grafo_conectado(self):
        """
        Verifica se o grafo é conectado.
        """
        visitados = [False] * self.num_vertices
        self.verificar_conectividade(visitados, 0)
        return all(visitados)
    

    def identificar_pontes_naive(self):
        """
        Identifica pontes usando o método Naive.
        """
        pontes = []
        for u in range(self.num_vertices):
            for v, _ in self.adjacencias[u]:
                self.remover_aresta(u, v)
                if not self.grafo_conectado():
                    pontes.append((u, v))
                self.adicionar_aresta(u, v)
        return pontes

    def identificar_pontes_tarjan(self):
        """
        Identifica pontes usando o algoritmo de Tarjan.
        """
        TD = [0] * self.num_vertices
        low = [float("inf")] * self.num_vertices
        pai = [None] * self.num_vertices
        pontes = []
        self.tempo = 0

        def busca_pontes(v):
            self.tempo += 1
            TD[v] = low[v] = self.tempo
            for w, _ in self.adjacencias[v]:
                if TD[w] == 0:
                    pai[w] = v
                    busca_pontes(w)
                    low[v] = min(low[v], low[w])
                    if low[w] > TD[v]:
                        pontes.append((v, w))
                elif w != pai[v]:
                    low[v] = min(low[v], TD[w])

        for v in range(self.num_vertices):
            if TD[v] == 0:
                busca_pontes(v)

        return pontes

    def fleury(self):
        """
        Implementa o Algoritmo de Fleury para encontrar caminho Euleriano.
        """
        def grafo_conectado():
            visitados = [False] * self.num_vertices

            def dfs(v):
                visitados[v] = True
                for w, _ in self.adjacencias[v]:
                    if not visitados[w]:
                        dfs(w)

            inicio = next((v for v in range(self.num_vertices) if self.adjacencias[v]), None)
            if inicio is None:
                return True

            dfs(inicio)
            return all(visitados[v] or not self.adjacencias[v] for v in range(self.num_vertices))

        def eh_aresta_ponte(u, v):
            self.remover_aresta(u, v)
            conectado = grafo_conectado()
            self.adicionar_aresta(u, v)
            return not conectado

        caminho = []
        atual = next((v for v in range(self.num_vertices) if len(self.adjacencias[v]) % 2 == 1), 0)

        while any(self.adjacencias[atual]):
            for vizinho, _ in self.adjacencias[atual]:
                if not eh_aresta_ponte(atual, vizinho) or len(self.adjacencias[atual]) == 1:
                    caminho.append((atual, vizinho))
                    self.remover_aresta(atual, vizinho)
                    atual = vizinho
                    break

        return caminho



def teste_desempenho():
    tamanhos = [100, 1000, 10000, 100000]
    num_arestas = [150, 1500, 15000, 150000]

    for i, tamanho in enumerate(tamanhos):
        grafo = Grafo(tamanho)
        grafo.gerar_grafo_simples(num_arestas[i])

        
        print(f"Teste para {tamanho} vértices usando método Naive:")
        operacoes_naive = 0
        for u in range(grafo.num_vertices):
            for v, _ in grafo.adjacencias[u]:
                operacoes_naive += 1  
        print(f"Operações simuladas: {operacoes_naive}")

        
        print(f"Teste para {tamanho} vértices usando método Tarjan:")
        grafo.tempo = 0
        pontes_tarjan = grafo.identificar_pontes_tarjan()
        print(f"Pontes encontradas: {len(pontes_tarjan)}")
        print(f"Operações simuladas: {grafo.tempo}")

        print()


teste_desempenho()
