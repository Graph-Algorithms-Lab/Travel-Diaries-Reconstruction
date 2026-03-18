import networkx as nx
import random
from odparser import *
from traveldiary import *

# Esempio d'uso:
if __name__ == "__main__":
    
    random.seed(31)
    
    EDGE=True
    UNIFORM=True
    
    # t = 30
    t = len(range(0, 7)) # see the shared doc about fasce orarie lookup. TODO: fix that later.
    n = 50
    N = 200
    
    G, parts = build_t_partite_graph_from_od_matrix(t, '../data/fs/Output Matrice Fondamentale Firenze.csv', EDGE)
    
    if VERBOSE:
        print("nodes", G.nodes())
        print("edges", G.edges())

    for i in range(t):
        s=0
        for u in parts[i]:
            s0 = G.nodes[u].get("count", 0)
            s += s0
            if DEBUG:
                print("Vertex", u, "with count", s0)
        if DEBUG:
            print(f"Somma etichette dei vertici partizione {i}: {s}")

    # Verifica: stampiamo la somma delle etichette per ogni coppia di partizioni consecutive
    if EDGE and DEBUG:
        for i in range(t - 1):
            s = 0
            for u in parts[i]:
                for v in parts[i + 1]:
                    w = G[u].get(v, {'weight': 0})['weight']
                    s += w
                    print("edge from", u, "to", v ,"with label", w)
            
            print(f"Somma etichette tra partizione {i} e {i+1}: {s}")

    res=get_travel_diaries(G, parts, UNIFORM, EDGE)
    print("Found", len(res), "travel diaries")
    if DEBUG:
        print(res)

    if True or VERBOSE:
        print("Checking correctness of travel diaries found")
        print(check_result(G,parts,res, EDGE))

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


