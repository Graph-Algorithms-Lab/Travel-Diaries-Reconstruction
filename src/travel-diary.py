import networkx as nx
import random

def build_t_partite_graph(t: int, n: int, N: int):
    """
    Costruisce un grafo t-partito con t partizioni di n vertici ciascuna.
    Tra la partizione i ed i+1 il grafo è completo (K_{n,n}).
    Assegna ad ogni arco un'etichetta intera >= 0 in modo che la somma
    delle etichette degli archi tra partizione i e i+1 sia N (per ogni i).

    Restituisce un networkx.Graph con attributo d'arco 'label' (int),
    e una lista `partitions` dove partitions[i] è la lista dei nodi nella partizione i.
    """
    if t < 2:
        raise ValueError("t deve essere almeno 2 (altrimenti non ci sono archi tra partizioni).")
    if n < 1:
        raise ValueError("n deve essere almeno 1.")
    if N < 0:
        raise ValueError("Questa implementazione richiede N >= 0 (etichette non negative).")

    G = nx.DiGraph()
    partitions = []

    # Creazione nodi: li etichettiamo come (i, j) dove i = indice partizione, j = indice dentro la partizione
    for i in range(t):
        part = []
        for j in range(n):
            node = (i, j)
            G.add_node(node, part=i, idx=j)
            part.append(node)
        partitions.append(part)

    # Per ogni coppia di partizioni consecutive aggiungiamo tutti gli archi e assegniamo etichette
    edges_per_pair = n * n
    base = N // edges_per_pair

    for i in range(t - 1):
        # generiamo la lista degli archi (ordine deterministico)
        arc_list = []
        node_list = []
        for u in partitions[i]:
            node_list.append(u)
            for v in partitions[i + 1]:
                arc_list.append((u, v))

        sum=0
        # Assegniamo etichette: primi `rem` archi ricevono base+1, gli altri base
        for k, (u, v) in enumerate(arc_list):
            if u[1]==v[1]:
                continue
            label = int(random.random()*base)
            sum+=label
            G.add_edge(u, v, label=int(label))
        
        remaining=(N-sum)//n
        remrem=(N-sum)%n
        print("remaining", remaining)
        for k, u in enumerate(node_list):
            lab=remaining+(1 if k<remrem else 0)
            print("Adding edge", (i,u[1]), (i+1,u[1]), "with label", int(lab) )
            G.add_edge((i,u[1]), (i+1,u[1]), label=int(lab))

    return G, partitions

def get_degree_distr(G, list):
    #the degree of a node is the sum of the labels of its incoming edges
    dict={}
    for u in list:
        dict[u]=G.out_degree(u)#questo dovrebbe essere grado pesato
    return dict


def get_node_prop_to_its_degree(degree_dist):
    nodes=list(degree_dist.keys())#TODO da cambiare
    ind=int(random.random()*len(nodes))
    return nodes[ind]

def get_next_edge(G, vertex):
    gneigh=list(G.successors(vertex))
    if len(gneigh)==0:
        return 0
    ind=int(random.random()*len(gneigh))
    print("get_next_edge", "vertex", vertex, "gneigh", gneigh, "ind", ind)
    #for u in G.successors(vertex):
    return (vertex, gneigh[ind])

def get_next_travel_diary(G, partitions):
    dict=get_degree_distr(G, partitions[0])
    u=get_node_prop_to_its_degree(dict)
    path=[]
    for i in range(len(partitions)-1): 
        e=get_next_edge(G, u)
        if e==None:
            break
        print("edge", e)
        u=e[1]
        path.append(e)
    return path

# Esempio d'uso:
if __name__ == "__main__":
    t = 3
    n = 5
    N = 200
    G, parts = build_t_partite_graph(t, n, N)
    print("nodes", G.nodes())
    print("edges", G.edges())
    # Verifica: stampiamo la somma delle etichette per ogni coppia di partizioni consecutive
    for i in range(t - 1):
        s = 0
        for u in parts[i]:
            for v in parts[i + 1]:
                s += G[u][v]['label']
                print("edge from ", u, "to", v ,"with label", G[u][v]['label'])
        print(f"Somma etichette tra partizione {i} e {i+1}: {s}")
    
    count=0
    while True:
        count+=1
        path=get_next_travel_diary(G, parts)
        if path==None:
            break
        print(path)
        for edge in path:
            u=edge[0]
            v=edge[1]
            G[u][v]['label']-=1
            if G[u][v]['label']==0:
                G.remove_edge(u,v)
    print("count", count)
    residualEdges=G.edges()
    print(residualEdges)

#TODO genera istanze dove per ogni nodo indegree(v)==outdegree(v) 
#per ogni nodo v nelle partizioni intermedie
#TODO far tornare a casa
#TODO genera primo nodo non a caso ma prop a  grado pesato
#TODO genera prossimo arco prop ai pesi


