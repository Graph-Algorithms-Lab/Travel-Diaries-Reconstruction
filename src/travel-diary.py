import networkx as nx
import random
import copy

VERBOSE=True
DEBUG=False
TRACE=False

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

    countersVertex={}
    countersEdge={}
    allTraj=[]
    for traj in range(N):
        S=[]
        for i in range(t):
            randomj=random.randint(0,n-1)
            S.append((i,randomj))
            countersVertex[(i,randomj)]=countersVertex.get((i,randomj),0)+1
            if len(S)!=1:
                last=S[-2]
                edge=(last,(i,randomj))
                countersEdge[edge]=countersEdge.get(edge,0)+1
        allTraj.append(S)

    for node,vcount in countersVertex.items():
        G.nodes[node]["count"] = vcount

    for (u, v), ecount in countersEdge.items():
        # ensure nodes exist even if not already added (defensive)
        if u not in G:
        #    G.add_node(u, count=0, label="0")
            print("Error u not in G")
            exit()
        if v not in G:
            print("Error v not in G")
            exit()
        #    G.add_node(v, count=0, label="0")

        # store edge count, plus label/weight
        G.add_edge(u, v, weight=ecount)

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

def get_next_vertex(G, vertex, uniform ):
    gneigh=list(G.successors(vertex))
    if TRACE:
        print("The neighbors of vertex", vertex, "are", gneigh)
    dest=choose_destination(G, gneigh, uniform )
    return dest

def choose_destination(G, part, uniform=True):
    candidate=[]
    for v in part:
        if G.nodes[v]["count"]>0:
            candidate.append(v)
    if len(candidate)==0:
        return None
    else:
        return random.choice(candidate)

#Edge implica Vertex
#Vertex non implica Edge
def get_next_travel_diary(G, partitions, uniform=True, Edge=True):
    #dict=get_degree_distr(G, partitions[0])
    #u=get_node_prop_to_its_degree(dict)
    if uniform:
        u=choose_destination(G, partitions[0], uniform)
        if u==None:
            return None
    path=[u]
    for i in range(len(partitions)-1): 
        v=get_next_vertex(G, u, uniform)
        if v==None:
            break
        if TRACE:
            print("next vertex", v)
        path.append(v)
        u=v
    if DEBUG:
        print("Found a path ", path)
    #Aggiorniamo per vertice 
    for u in path:
        if G.nodes[u]["count"]<=0:
            print("G.nodes[u][count]<=0")
            system.exit()
        G.nodes[u]["count"]-=1
    #Aggiorniamo gli archi
    if Edge:
        for i in range(len(path)-1):
            u=path[i]
            v=path[i+1]
            if G[u][v]["weight"]<=0:
                print("G[u][v][weight]<=0")
                system.exit()
            G[u][v]["weight"]-=1
            #Quando arco va a zero va rimosso
            if G[u][v]["weight"]==0:
                G.remove_edge(u, v)
    return path

def get_travel_diaries(G, partitions, uniform=True, Edge=True):
    result=[]
    copyG=copy.deepcopy(G)
    while True:
        partialsol=get_next_travel_diary(copyG, partitions, uniform, Edge)
        if partialsol==None:
            break
        result.append(partialsol)
    return result

def check_result(G, partitions, travel_diaries):
    #Gprime=copy.deepcopy(G)
    Gprime = nx.DiGraph()
    for t in range(len(partitions)):
        for v in partitions[t]:
            Gprime.add_node(v, part=v[0], idx=v[1])
    for traj in travel_diaries:
        for v in traj:
            Gprime.nodes[v]["count"]=0
    for traj in travel_diaries:
        for v in traj:
            Gprime.nodes[v]["count"]=Gprime.nodes[v]["count"]+1
        for j in range(len(traj)-1):
            u=traj[j]
            v=traj[j+1]
            if not Gprime.has_edge(u, v):
                Gprime.add_edge(u, v, weight=0)
            Gprime[u][v]["weight"]+=1
    print(G.edges())
    print(Gprime.edges())
    #check whether G and Gprime are equal
    same_nodes = set(G.nodes()) == set(Gprime.nodes())
    same_edges = set(G.edges()) == set(Gprime.edges())
    same_counts=True
    for n in G.nodes():
        if G.nodes[n].get("count") != Gprime.nodes[n].get("count"):
            same_counts=False
    weights_G = nx.get_edge_attributes(G, "weight")
    weights_Gprime = nx.get_edge_attributes(Gprime, "weight")
    same_weights = weights_G == weights_Gprime
    #return nx.utils.graphs_equal(G, Gprime)
    print("same_nodes and same_edges and same_counts and same_weights", same_nodes , same_edges , same_counts , same_weights)
    return same_nodes and same_edges and same_counts and same_weights
    

# Esempio d'uso:
if __name__ == "__main__":
    seed=171
    random.seed(171)
    EDGE=True
    UNIFORM=True
    t = 3
    n = 5
    N = 200
    G, parts = build_t_partite_graph(t, n, N)
    if VERBOSE:
        print("nodes", G.nodes())
        print("edges", G.edges())

    for i in range(t):
        s=0
        for u in parts[i]:
            s+=G.nodes[u]["count"]
            if DEBUG:
                print("Vertex", u, "with count", G.nodes[u]["count"])
        if DEBUG:
            print(f"Somma etichette dei vertici partizione {i}: {s}")

    # Verifica: stampiamo la somma delle etichette per ogni coppia di partizioni consecutive
    for i in range(t - 1):
        s = 0
        for u in parts[i]:
            for v in parts[i + 1]:
                s += G[u][v]['weight']
                if DEBUG:
                    print("edge from", u, "to", v ,"with label", G[u][v]['weight'])
        if DEBUG:
            print(f"Somma etichette tra partizione {i} e {i+1}: {s}")

    res=get_travel_diaries(G, parts, UNIFORM, EDGE)
    print("Found", len(res), "travel diaries")
    if DEBUG:
        print(res)

    if VERBOSE:
        print("Checking correctness of travel diaries found")
        print(check_result(G,parts,res))

#    count=0
#    while True:
#        count+=1
#        path=get_next_travel_diary(G, parts)
#        if path==None:
#            break
#        print(path)
#        for edge in path:
#            u=edge[0]
#            v=edge[1]
#            G[u][v]['label']-=1
#            if G[u][v]['label']==0:
#                G.remove_edge(u,v)
#    print("count", count)
#    residualEdges=G.edges()
#    print(residualEdges)

#TODO genera istanze dove per ogni nodo indegree(v)==outdegree(v) 
#per ogni nodo v nelle partizioni intermedie
#TODO far tornare a casa
#TODO genera primo nodo non a caso ma prop a  grado pesato
#TODO genera prossimo arco prop ai pesi


