import networkx as nx
import random
import copy
from odparser import *

VERBOSE=False
DEBUG=False
TRACE=False


def build_t_partite_graph_from_od_matrix(t, file_path, F):

    rows, locations, V, Vinv = parse_od_matrix(file_path, filename_gis="../data/gis/mavfa-fs-3000_zone.shp")

    def M(x):
        u = get_time_window(x) - 1, Vinv[get_source_id(x)]
        v = get_time_window(x), Vinv[get_destination_id(x)]
        w = get_weight(x)
        return u, v, w

    G = nx.DiGraph()
    
    discovered_nodes = set()

    for u, v, w in map(M, filter(F, rows)):
        d = locations[V[u[1]]].geometry.centroid.distance(locations[V[v[1]]].geometry.centroid)
        G.add_edge(u, v, weight=w, distance=d)
        discovered_nodes.add(u[1])
        discovered_nodes.add(v[1])

    discovered_nodes = list(sorted(discovered_nodes))
    
    partitions = []
    
    for i in range(t):
        
        part = []
        
        for j in discovered_nodes:

            node = i, j

            if node not in G.nodes: G.add_node(node)
            
            nn = G.nodes[node]
            
            centroid = locations[V[j]].geometry.centroid

            nn['count'] = 0
            nn['part'] = i
            nn['idx'] = j
            nn['lat'] = float(locations[V[j]].lat)
            nn['lon'] = float(locations[V[j]].lon)
            nn['centroid'] = centroid
            nn['zone_name'] = locations[V[j]].zone_name

            part.append(node)
        
        partitions.append(part)
    
    for part in partitions:
        
        for tpart_u in part:
            
            tpart, u = tpart_u

            w_in = sum(w for _, _, w in G.in_edges(tpart_u, data='weight'))
            w_out = sum(w for _, _, w in G.out_edges(tpart_u, data='weight'))

            if tpart == 0: G.nodes[tpart_u]['count'] = w_out
            elif tpart == t - 1: G.nodes[tpart_u]['count'] = w_in
            else: # 0 < tpart < t - 1:
                d = w_in - w_out

                if d < 0:
                    dd = -d
                    for j in range(tpart):
                        ju = j, u
                        j1u = j + 1, u
                        if G.has_edge(ju, j1u): G[ju][j1u]['weight'] += dd
                        else: G.add_edge(ju, j1u, weight=dd, distance=0)
                        G.nodes[ju]['count'] += dd
                elif d > 0: G.add_edge((tpart, u), (tpart + 1, u), weight=d, distance=0)

                G.nodes[tpart_u]['count'] = max(w_in, w_out)

    if VERBOSE:

        c = 0
        for v in discovered_nodes:

            count_start = G.nodes[(0, v)]['count']
            count_end = G.nodes[(t-1, v)]['count']

            d = abs(count_start - count_end) / max(count_start, count_end)

            if d > 0.1:
                c += 1
                print(f"Warning: node {v} ({locations[V[v]]['zone_name']}) has count {count_start} in partition 0 and count {count_end} in partition {t-1}, with relative difference {d:.2%}")

        print(len(discovered_nodes), "nodes discovered in the OD matrix, with", c, "nodes having a relative difference in count greater than 1% between partition 0 and partition", t-1)

    return G, partitions, locations, V, Vinv

def build_t_partite_graph(t: int, n: int, N: int, Edge = True, go_back_home=False):
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

            if go_back_home and i == t-1: randomj=S[0][1]

            new_node = i, randomj
            S.append(new_node)
            countersVertex[new_node] = countersVertex.get(new_node,0) + 1
            if len(S) != 1 and Edge:
                edge=(S[-2], new_node)
                countersEdge[edge] = countersEdge.get(edge,0) + 1

        if TRACE: print("Generated trajectory", S)

        allTraj.append(S)

    for node,vcount in countersVertex.items():
        G.nodes[node]["count"] = vcount

    if Edge:
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
    else:
        for i in range(t-1):
            for u in partitions[i]:
                for v in partitions[i+1]:
                    G.add_edge(u, v)

    # print ("Built graph with", G.number_of_nodes(), "nodes and", G.number_of_edges(), "edges")
    
    return G, partitions

def get_next_vertex(G, vertex, uniform, weighted): 
    return choose_destination(G, vertex, list(G.successors(vertex)), uniform, weighted)

def choose_destination(G, source, part, uniform, weighted):

    sum_count = sum(G.nodes[v].get("count", 0) for v in part) if weighted.get('vertex', False) else 0
    sum_weight = sum(G.edges[source, v]['weight'] for v in part if G.has_edge(source, v)) if weighted.get('edge', False) and source else 0
    sum_distance = sum(1 / (G.edges[source, v]['distance'] or 1) for v in part if G.has_edge(source, v)) if weighted.get('distance', False) and source else 0

    candidates, weights = [], []
    
    for v in part:

        w = 0
       
        w += (G.nodes[v].get("count", 0) / sum_count) * weighted.get('vertex', 0)

        if source: w += (G.edges[source, v]['weight'] / sum_weight) * weighted.get('edge', 0)

        if source: w += ((1 / (G.edges[source, v]['distance'] or 1)) / sum_distance) * weighted.get('distance', 0)

        if G.nodes[v].get("count", 0) > 0:
            candidates.append(v)
            weights.append(w)

    if candidates: return random.choice(candidates) if uniform else random.choices(candidates, weights=weights)[0]
    
#Edge implica Vertex, Vertex non implica Edge
def get_next_travel_diary(G, partitions, uniform, edge, exact, weighted, go_back_home):
    
    u = choose_destination(G, None, partitions[0], uniform, weighted)
    
    if not u: return None
    
    path = [u]
    
    for i in range(len(partitions)-1): 
        
        v = (i + 1, path[0][1]) if i == len(partitions)-2 and go_back_home else get_next_vertex(G, u, uniform, weighted)
        
        if v == None: break
        
        if TRACE: print("next vertex", v)

        path.append(v)
        u = v

    if DEBUG: print("Found a path ", path)

    if exact: 
        
        #Aggiorniamo per vertice
        for u in path:

            assert G.nodes[u].get("count", 0) > 0, f"Error: node {u} has count {G.nodes[u].get('count', 0)} but should be > 0"
            G.nodes[u]["count"]-=1

        #Aggiorniamo gli archi
        if edge:
            for i in range(len(path)-1):
                u=path[i]
                v=path[i+1]
                
                if G[u].get(v, {"weight":0})['weight'] <= 0:
                    print("G[u][v][weight]<=0")
                    print ("Error: edge from", u, "to", v, "has weight", G[u].get(v, {"weight":-1})['weight'], "but should be > 0")
                    exit(1)

                G[u][v]["weight"] -= 1
                
                if G[u][v]["weight"]==0: #Quando arco va a zero va rimosso
                    G.remove_edge(u, v)

    return path

def get_travel_diaries(G, partitions, uniform=True, edge=True, exact=True,  go_back_home=False, 
                       weighted={'vertex': 1, 'edge': 1, 'distance': 1}):
    
    copyG = copy.deepcopy(G)
    
    while True:

        partialsol = get_next_travel_diary(copyG, partitions, uniform, edge, exact, weighted, go_back_home)

        if not partialsol: break

        yield partialsol

def check_result(G, partitions, travel_diaries, Edge=True):
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
            Gprime.nodes[v]["count"] += 1
        if Edge:
            for j in range(len(traj)-1):
                u=traj[j]
                v=traj[j+1]
                if not Gprime.has_edge(u, v):
                    Gprime.add_edge(u, v, weight=0)
                Gprime[u][v]["weight"]+=1
    
    #check whether G and Gprime are equal
    same_nodes = set(G.nodes()) == set(Gprime.nodes())

    if Edge:
        print(G.edges())
        print(Gprime.edges())
    
        #check whether G and Gprime are equal
        same_edges = set(G.edges()) == set(Gprime.edges())

    same_counts=True
    for n in G.nodes():
        if G.nodes[n].get("count", 0) != Gprime.nodes[n].get("count", 0):
            print ("Node", n, "has count", G.nodes[n].get("count", 0), "in G and count", Gprime.nodes[n].get("count", 0), "in Gprime")
            same_counts=False
            break
    
    if Edge:
        weights_G = nx.get_edge_attributes(G, "weight")
        weights_Gprime = nx.get_edge_attributes(Gprime, "weight")
        same_weights = weights_G == weights_Gprime
        print("same_nodes and same_edges and same_counts and same_weights", same_nodes , same_edges , same_counts , same_weights)
        return same_nodes and same_edges and same_counts and same_weights
    else:
        print("same_nodes and same_counts", same_nodes, same_counts)
        return same_nodes and same_counts