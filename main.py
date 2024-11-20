import os
import sys

class Grafo:
    def __init__(self, num_vertices):
        self.num_vertices = num_vertices
        self.adjacencias = {i: [] for i in range(num_vertices)}
        self.tempo = 0

    def adicionar_aresta(self, u, v):
        if v not in [w for w, _ in self.adjacencias[u]]:
            self.adjacencias[u].append((v, 1))
            self.adjacencias[v].append((u, 1))

    def remover_aresta(self, u, v):
        self.adjacencias[u] = [w for w in self.adjacencias[u] if w[0] != v]
        self.adjacencias[v] = [w for w in self.adjacencias[v] if w[0] != u]

    def checar_adjacencia_vertices(self, u, v):
        return any(w == v for w, _ in self.adjacencias[u])

    def contar_vertices_arestas(self):
        num_arestas = sum(len(self.adjacencias[v]) for v in self.adjacencias) // 2
        return self.num_vertices, num_arestas

    def grafo_vazio(self):
        return all(len(self.adjacencias[v]) == 0 for v in self.adjacencias)

    def grafo_completo(self):
        for u in range(self.num_vertices):
            for v in range(self.num_vertices):
                if u != v and not self.checar_adjacencia_vertices(u, v):
                    return False
        return True

    def identificar_pontes_naive(self):
        pontes = []
        for u in range(self.num_vertices):
            for v, _ in self.adjacencias[u]:
                self.remover_aresta(u, v)
                if not self.grafo_conectado():
                    pontes.append((u, v))
                self.adicionar_aresta(u, v)
        return pontes

    def identificar_pontes_tarjan(self):
        TD = [0] * self.num_vertices
        low = [float("inf")] * self.num_vertices
        pai = [None] * self.num_vertices
        pontes = []
        self.tempo = 0

        def dfs_tarjan(v):
            TD[v] = low[v] = self.tempo = self.tempo + 1
            for w, _ in self.adjacencias[v]:
                if TD[w] == 0:
                    pai[w] = v
                    dfs_tarjan(w)
                    low[v] = min(low[v], low[w])
                    if low[w] > TD[v]:
                        pontes.append((v, w))
                elif w != pai[v]:
                    low[v] = min(low[v], TD[w])

        for v in range(self.num_vertices):
            if TD[v] == 0:
                dfs_tarjan(v)

        return pontes

    def grafo_conectado(self):
        visitados = [False] * self.num_vertices

        def dfs(v):
            visitados[v] = True
            for w, _ in self.adjacencias[v]:
                if not visitados[w]:
                    dfs(w)

        dfs(0)
        return all(visitados)

    def fleury(self):
        def eh_aresta_ponte(u, v):
            self.remover_aresta(u, v)
            conectado = self.grafo_conectado()
            self.adicionar_aresta(u, v)
            return not conectado

        caminho = []
        atual = 0
        while any(self.adjacencias[atual]):
            for vizinho, _ in self.adjacencias[atual]:
                if not eh_aresta_ponte(atual, vizinho) or len(self.adjacencias[atual]) == 1:
                    caminho.append((atual, vizinho))
                    self.remover_aresta(atual, vizinho)
                    atual = vizinho
                    break
        return caminho

    def exportar_para_gexf(self, nome_arquivo="grafo.gexf"):
        if not os.path.exists("dados"):
            os.makedirs("dados")
        with open(f"dados/{nome_arquivo}", "w", encoding="utf-8") as arquivo:
            arquivo.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            arquivo.write('<gexf xmlns="http://www.gexf.net/1.3" version="1.3">\n')
            arquivo.write('  <graph mode="static" defaultedgetype="undirected">\n')
            arquivo.write("    <nodes>\n")
            for vertice in range(self.num_vertices):
                arquivo.write(f'      <node id="{vertice}" label="V{vertice}" />\n')
            arquivo.write("    </nodes>\n")
            arquivo.write("    <edges>\n")
            id_aresta = 0
            arestas = set()
            for u in range(self.num_vertices):
                for v, peso in self.adjacencias[u]:
                    if (u, v) not in arestas and (v, u) not in arestas:
                        arestas.add((u, v))
                        arquivo.write(f'      <edge id="{id_aresta}" source="{u}" target="{v}" weight="{peso}" />\n')
                        id_aresta += 1
            arquivo.write("    </edges>\n")
            arquivo.write("  </graph>\n")
            arquivo.write("</gexf>\n")

    def exportar_para_csv(self, nome_arquivo="grafo.csv"):
        if not os.path.exists("dados"):
            os.makedirs("dados")
        with open(f"dados/{nome_arquivo}", "w", encoding="utf-8") as arquivo:
            arquivo.write("Source,Target,Weight\n")
            arestas = set()
            for u in range(self.num_vertices):
                for v, peso in self.adjacencias[u]:
                    if (u, v) not in arestas and (v, u) not in arestas:
                        arestas.add((u, v))
                        arquivo.write(f"{u},{v},{peso}\n")


def ajustar_limite_recursao(tamanho_grafo):
    limite = min(2000 + tamanho_grafo, 20000)  
    sys.setrecursionlimit(limite)

def testeDesempenho():
    tamanhos = [100, 1000, 10000, 100000]
    num_arestas = [150, 1500, 15000, 150000]

    for tamanho, arestas in zip(tamanhos, num_arestas):
        ajustar_limite_recursao(tamanho)  

        grafo = Grafo(tamanho)
        for i in range(arestas):
            grafo.adicionar_aresta(i % tamanho, (i + 1) % tamanho)
        print(f"Teste para {tamanho} vértices:")
        print("Método Naive:")
        pontes_naive = grafo.identificar_pontes_naive()
        print(f"Pontes encontradas: {len(pontes_naive)}")
        print("Método Tarjan:")
        pontes_tarjan = grafo.identificar_pontes_tarjan()
        print(f"Pontes encontradas: {len(pontes_tarjan)}")
        caminho_euleriano = grafo.fleury()
        print(f"Caminho Euleriano: {caminho_euleriano}")
        grafo.exportar_para_gexf(f"grafo_{tamanho}.gexf")
        grafo.exportar_para_csv(f"grafo_{tamanho}.csv")

def menu():
    grafos_prontos = {
        "1": [(0, 1), (1, 2), (2, 3), (3, 0)],
        "2": [(0, 1), (1, 2), (2, 3), (3, 0), (3, 1)],
        "3": [(0, 1), (1, 2), (2, 3), (3, 0), (3, 2), (2, 0)],
    }

    while True:
        print("Escolha as opções abaixo:")
        print("1. Analisar Grafos Prontos")
        print("2. Criar Grafo Manualmente")
        print("3. Realizar Teste de Desempenho (Parte 2)")
        print("4. Sair")
        opcao = int(input("Escolha uma opção: "))

        if opcao == 1:
            for nome, arestas in grafos_prontos.items():
                num_vertices = max(max((u, v), default=0) for u, v in arestas) + 1
                grafo = Grafo(num_vertices)
                for u, v in arestas:
                    grafo.adicionar_aresta(u, v)
                print(f"Grafo {nome}:")
                print(f"Vértices: {grafo.num_vertices}")
                print(f"Arestas: {grafo.contar_vertices_arestas()[1]}")
                grafo.exportar_para_gexf(f"grafo_{nome}.gexf")
                grafo.exportar_para_csv(f"grafo_{nome}.csv")
        elif opcao == 2:
            num_vertices = int(input("Digite o número de vértices: "))
            grafo = Grafo(num_vertices)
            while True:
                print("1. Adicionar Aresta")
                print("2. Remover Aresta")
                print("3. Verificar Adjacência")
                print("4. Voltar")
                escolha = int(input("Escolha uma opção: "))
                if escolha == 1:
                    u = int(input("Digite o vértice u: "))
                    v = int(input("Digite o vértice v: "))
                    grafo.adicionar_aresta(u, v)
                    print(f"Aresta ({u}, {v}) adicionada!")
                elif escolha == 2:
                    u = int(input("Digite o vértice u: "))
                    v = int(input("Digite o vértice v: "))
                    grafo.remover_aresta(u, v)
                    print(f"Aresta ({u}, {v}) removida!")
                elif escolha == 3:
                    u = int(input("Digite o vértice u: "))
                    v = int(input("Digite o vértice v: "))
                    if grafo.checar_adjacencia_vertices(u, v):
                        print(f"Aresta ({u}, {v}) existe!")
                    else:
                        print(f"Aresta ({u}, {v}) não existe.")
                elif escolha == 4:
                    grafo.exportar_para_gexf(f"grafo_{num_vertices}.gexf")
                    grafo.exportar_para_csv(f"grafo_{num_vertices}.csv")
                    break
        elif opcao == 3:
            testeDesempenho()
        elif opcao == 4:
            break
        else:
            print("Opção inválida, tente novamente.")


menu()
