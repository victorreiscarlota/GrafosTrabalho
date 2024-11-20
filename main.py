import os

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

    def contar_vertices_arestas(self):
        num_arestas = sum(len(self.adjacencias[v]) for v in self.adjacencias) // 2
        return self.num_vertices, num_arestas

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

    def exportar_para_ppm(self, nome_arquivo="grafo.ppm"):
        largura = 500
        altura = 500
        raio = 10
        centro = largura // 2, altura // 2
        espacamento = 360 // self.num_vertices

        vertices_posicoes = {}
        for i in range(self.num_vertices):
            angulo = espacamento * i
            x = int(centro[0] + (largura // 2.5) * (angulo / 360))
            y = int(centro[1] + (altura // 2.5) * (angulo / 360))
            vertices_posicoes[i] = (x, y)

        imagem = [["255 255 255" for _ in range(largura)] for _ in range(altura)]

        for u, vizinhos in self.adjacencias.items():
            x1, y1 = vertices_posicoes[u]
            for v, _ in vizinhos:
                x2, y2 = vertices_posicoes[v]
                for t in range(101):
                    x = int(x1 + (x2 - x1) * t / 100)
                    y = int(y1 + (y2 - y1) * t / 100)
                    imagem[y][x] = "0 0 0"

        for x, y in vertices_posicoes.values():
            for i in range(-raio, raio + 1):
                for j in range(-raio, raio + 1):
                    if 0 <= x + i < largura and 0 <= y + j < altura:
                        imagem[y + j][x + i] = "255 0 0"

        if not os.path.exists("dados"):
            os.makedirs("dados")
        with open(f"dados/{nome_arquivo}", "w") as arquivo:
            arquivo.write(f"P3\n{largura} {altura}\n255\n")
            for linha in imagem:
                arquivo.write(" ".join(linha) + "\n")

def menu():
    grafos_prontos = {
        "1": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)],  
        "2": [(0, 1), (1, 2), (2, 3), (3, 4)],          
        "3": [(0, 1), (0, 2), (0, 3), (0, 4)],         
        "4": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (2, 5), (1, 4), (0, 3)],  # Complexo
        "5": [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5), (1, 3), (2, 4), (0, 2), (3, 5)],  # Denso
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
                grafo.exportar_para_gexf(f"grafo_{nome}.gexf")
                grafo.exportar_para_csv(f"grafo_{nome}.csv")
                grafo.exportar_para_ppm(f"grafo_{nome}.ppm")
                print(f"Grafo {nome} salvo nos formatos GEXF, CSV e PPM.")
        elif opcao == 2:
            num_vertices = int(input("Digite o número de vértices: "))
            grafo = Grafo(num_vertices)
            while True:
                print("1. Adicionar Aresta")
                print("2. Remover Aresta")
                print("3. Mostrar Informações")
                print("4. Salvar Grafo")
                print("5. Voltar")
                sub_opcao = int(input("Escolha: "))
                if sub_opcao == 1:
                    u, v = map(int, input("Digite os vértices da aresta (u v): ").split())
                    grafo.adicionar_aresta(u, v)
                elif sub_opcao == 2:
                    u, v = map(int, input("Digite os vértices da aresta para remover (u v): ").split())
                    grafo.remover_aresta(u, v)
                elif sub_opcao == 3:
                    print(f"Vértices: {grafo.num_vertices}")
                    print(f"Arestas: {grafo.contar_vertices_arestas()[1]}")
                elif sub_opcao == 4:
                    grafo.exportar_para_gexf("grafo_manual.gexf")
                    grafo.exportar_para_csv("grafo_manual.csv")
                    grafo.exportar_para_ppm("grafo_manual.ppm")
                    print("Grafo salvo.")
                elif sub_opcao == 5:
                    break
        elif opcao == 3:
            print("Teste de desempenho não implementado aqui.")
        elif opcao == 4:
            break

menu()
